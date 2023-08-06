# Copyright 2018 Cochise Ruhulessin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# type: ignore
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding
from pyasn1.codec.der import decoder
from pyasn1.type.namedtype import NamedType
from pyasn1.type.namedtype import NamedTypes
from pyasn1.type.namedtype import OptionalNamedType
from pyasn1.type.univ import ObjectIdentifier
from pyasn1.type.univ import OctetString
from pyasn1.type.univ import Sequence
from pyasn1.type.univ import SetOf

from ckms.algorithm import Algorithm
from ckms.types import Digest
from ckms.types import JSONWebKey
from .status import PKIStatusInfo
from .timestamptoken import TimeStampToken


MessageDigestOID: ObjectIdentifier = ObjectIdentifier((1,2,840,113549,1,9,4,))
TimestampInfoOID: ObjectIdentifier = ObjectIdentifier((1,2,840,113549,1,9,16,1,4))


class TimestampResponse(Sequence):
    algorithms: dict[tuple[str, str], str] = {
        ('2.16.840.1.101.3.4.2.1', '1.2.840.113549.1.1.1'): 'RS256',
        ('2.16.840.1.101.3.4.2.2', '1.2.840.113549.1.1.1'): 'RS384',
        ('2.16.840.1.101.3.4.2.3', '1.2.840.113549.1.1.1'): 'RS512',
    }
    certificate: x509.Certificate
    componentType = NamedTypes(
        NamedType(
            name='status',
            asn1Object=PKIStatusInfo()
        ),
        OptionalNamedType(
            name='timeStampToken',
            asn1Object=TimeStampToken()
        )
    )

    @classmethod
    def frombytes(
        cls,
        certificate: x509.Certificate,
        response: bytes
    ) -> 'TimestampResponse':
        response, substrate = decoder.decode(response, asn1Spec=cls())
        if substrate:
            raise ValueError('Extra data returned')
        response.certificate = certificate
        return response

    @property
    def algorithm(self) -> Algorithm | None:
        name = self.algorithms.get(
            (
                self.digest_algorithm,
                str(self.signer['digestEncryptionAlgorithm'][0])
            )
        )
        return Algorithm.get(name)

    @property
    def content_type(self) -> ObjectIdentifier:
        return self.timestamp.content['contentInfo']['contentType']

    @property
    def digest_algorithm(self) -> str:
        return str(self.signer['digestAlgorithm'][0])

    @property
    def hasher(self) -> hashes.HashAlgorithm:
        return getattr(hashes, str.upper(Digest.digest_oid[self.digest_algorithm]))()

    @property
    def info(self):
        return self[0]

    @property
    def public_key(self) -> JSONWebKey:
        """A :class:`JSONWebKey` representing the public key of the TSA."""
        return JSONWebKey.fromcertificate(self.algorithm, self.certificate)

    @property
    def serial_number(self) -> int:
        """The serial number of the certificate that was used to sign the
        response.
        """
        return int(self.signer['issuerAndSerialNumber'][1])

    @property
    def signature(self) -> bytes:
        return bytes(self.signer['encryptedDigest'])

    @property
    def signed_data(self) -> bytes:
        # Validate only only signature for now
        content, _ = decoder.decode(
            substrate=self.timestamp.content['contentInfo']['content'],
            asn1Spec=OctetString()
        )
        digest = Digest.fromoid(
            data=bytes(content),
            oid=str(self.digest_algorithm)
        )
        signer = self.signer
        if bool(signer['authenticatedAttributes']):
            attrs = signer['authenticatedAttributes']
            for attr in attrs:
                if attr[0] != MessageDigestOID:
                    continue
                value, _ = decoder.decode(
                    substrate=attr[1][0],
                    asn1Spec=OctetString()
                )
                if bytes(value) != bytes(digest):
                    raise ValueError("Mismatch between content and attribute.")
                content = value
                break
            else:
                raise ValueError("No signed data present.")
        return bytes(content)

    @property
    def signers(self):
        return self.timestamp.content['signerInfos']

    @property
    def signer(self):
        return self.signers[0]

    @property
    def timestamp(self) -> TimeStampToken:
        return self[1]

    def validate(self) -> None:
        """Validates that the response is as expected."""
        if self.content_type != TimestampInfoOID:
            raise ValueError(f"Invalid content type: {str(self.content_type)}")
        if not self.signers:
            raise ValueError("The response did not contain a signature.")
        if len(self.signers) > 1:
            # The time-stamp token MUST NOT contain any signatures
            # other than the signature of the TSA.  The certificate
            # identifier (ESSCertID) of the TSA certificate MUST
            # be included as a signerInfo attribute inside a
            # SigningCertificate attribute (RFC 3161).
            raise ValueError(
                "The time-stamp token MUST NOT contain any signature "
                "other than the signature of the TSA."
            )
        if self.algorithm is None:
            raise ValueError(
                "The signing algorithm used by the TSA is not supported."
            )
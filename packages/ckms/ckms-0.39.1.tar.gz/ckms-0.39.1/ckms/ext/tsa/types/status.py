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
from pyasn1.type.char import UTF8String
from pyasn1.type.constraint import ValueSizeConstraint
from pyasn1.type.namedtype import NamedType
from pyasn1.type.namedtype import NamedTypes
from pyasn1.type.namedtype import OptionalNamedType
from pyasn1.type.namedval import NamedValues
from pyasn1.type.univ import BitString
from pyasn1.type.univ import Integer
from pyasn1.type.univ import Sequence
from pyasn1.type.univ import SequenceOf
from pyasn1_modules.rfc2459 import MAX


class PKIFreeText(SequenceOf):
    componentType = UTF8String
    sizeSpec = SequenceOf.sizeSpec + ValueSizeConstraint(1, MAX)


class PKIStatus(Integer):
    namedValues = NamedValues(
        ('granted', 0),
        # when the PKIStatus contains the value zero a TimeStampToken, as
        # requested, is present.
        ('grantedWithMods', 1),
        # when the PKIStatus contains the value one a TimeStampToken,
        # with modifications, is present.
        ('rejection', 2), ('waiting', 3), ('revocationWarning', 4),
        # this message contains a warning that a revocation is
        # imminent
        ('revocationNotification', 5),
    )


class PKIFailureInfo(BitString):
    namedValues = NamedValues(
        # unrecognized or unsupported Algorithm Identifier
        ('badAlg', 0),
        # transaction not permitted or supported
        ('badRequest', 2),
        # the data submitted has the wrong format
        ('badDataFormat', 5),
        # the TSA's time source is not available
        ('timeNotAvailable', 14),
        # the requested TSA policy is not supported by the TSA
        ('unacceptedPolicy', 15),
        # the requested extension is not supported by the TSA
        ('unacceptedExtension', 16),
        # the additional information requested could not be understood
        # or is not available
        ('addInfoNotAvailable', 17),
        # the request cannot be handled due to system failure  }
        ('systemFailure', 25)
    )


class PKIStatusInfo(Sequence):
    componentType = NamedTypes(
        NamedType(
            name='status',
            asn1Object=PKIStatus()
        ),
        OptionalNamedType(
            name='statusString',
            asn1Object=PKIFreeText()
        ),
        OptionalNamedType(
            name='failInfo',
            asn1Object=PKIFailureInfo()
        )
    )

    @property
    def status_code(self) -> int:
        return self[0]

    @property
    def status(self) -> int:
        return self[1]
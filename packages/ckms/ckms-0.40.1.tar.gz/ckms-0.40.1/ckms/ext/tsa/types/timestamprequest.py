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
from pyasn1.codec.der import encoder
from pyasn1.type.namedtype import DefaultedNamedType
from pyasn1.type.namedtype import NamedType
from pyasn1.type.namedtype import NamedTypes
from pyasn1.type.namedtype import OptionalNamedType
from pyasn1.type.namedval import NamedValues
from pyasn1.type import tag
from pyasn1.type.univ import Boolean
from pyasn1.type.univ import Integer
from pyasn1.type.univ import ObjectIdentifier
from pyasn1.type.univ import Sequence
from pyasn1_modules.rfc2459 import Extensions

from .algorithmidentifier import AlgorithmIdentifier
from .messageimprint import MessageImprint


class TimestampRequest(Sequence):
    componentType: NamedTypes = NamedTypes(
        NamedType('version', Integer(namedValues=NamedValues(('v1', 1)))),
        NamedType('messageImprint', MessageImprint()),
        OptionalNamedType('reqPolicy', ObjectIdentifier()),
        OptionalNamedType('nonce', Integer()),
        DefaultedNamedType('certReq', Boolean(False)),
        OptionalNamedType(
            'extensions',
            Extensions().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0)
            )
        )
    )

    @classmethod
    def new(cls, digest: bytes, digestmod: str) -> bytes:
        message = MessageImprint()
        message.setComponentByPosition(0, AlgorithmIdentifier.new(digestmod))
        message.setComponentByPosition(1, digest)
        request = cls()
        request.setComponentByPosition(0, 'v1')
        request.setComponentByPosition(1, message)
        request.setComponentByPosition(4)
        return encoder.encode(request)
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
from pyasn1_modules.rfc2459 import Extensions
from pyasn1.type import tag
from pyasn1.type.namedtype import DefaultedNamedType
from pyasn1.type.namedtype import NamedType
from pyasn1.type.namedtype import NamedTypes
from pyasn1.type.namedtype import OptionalNamedType
from pyasn1.type.namedval import NamedValues
from pyasn1.type.univ import Boolean
from pyasn1.type.univ import Integer
from pyasn1.type.univ import ObjectIdentifier
from pyasn1.type.univ import Sequence
from pyasn1.type.useful import GeneralizedTime

from .accuracy import Accuracy
from .generalname import GeneralName
from .messageimprint import MessageImprint


class TimestampInfo(Sequence):
    componentType = NamedTypes(
        NamedType(
            name='version',
            asn1Object=Integer(namedValues=NamedValues(('v1', 1)))
        ),
        OptionalNamedType(
            name='policy',
            asn1Object=ObjectIdentifier()
        ),
        NamedType(
            name='messageImprint',
            asn1Object=MessageImprint()
        ),
        # MUST have the same value as the similar field in
        # TimeStampReq
        NamedType(
            name='serialNumber',
            asn1Object=Integer()
        ),
        # Time-Stamping users MUST be ready to accommodate integers
        # up to 160 bits.
        NamedType(
            name='genTime',
            asn1Object=GeneralizedTime()
        ),
        OptionalNamedType(
            name='accuracy',
            asn1Object=Accuracy()
        ),
        DefaultedNamedType(
            name='ordering',
            asn1Object=Boolean(False)
        ),
        OptionalNamedType(
            name='nonce',
            asn1Object=Integer()
        ),
        # MUST be present if the similar field was present
        # in TimeStampReq.  In that case it MUST have the same value.
        OptionalNamedType(
            name='tsa',
            asn1Object=GeneralName().subtype(
                explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0)
            )
        ),
        OptionalNamedType(
            name='extensions',
            asn1Object=Extensions().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 1)
            )
        )
    )

    @property
    def version(self) -> int:
        return int(self[0])

    @property
    def policy(self) -> str:
        return str(self[1])

    @property
    def message_imprint(self) -> MessageImprint:
        return self[2]

    @property
    def tsa(self):
        return self[8]

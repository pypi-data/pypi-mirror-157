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
from pyasn1.type import tag
from pyasn1.type.namedtype import NamedType
from pyasn1.type.namedtype import NamedTypes
from pyasn1.type.namedtype import OptionalNamedType
from pyasn1_modules.rfc2315 import signedData
from pyasn1_modules.rfc2315 import ContentInfo
from pyasn1_modules.rfc2315 import SignedData
from pyasn1.codec.ber import decoder

from .timestampinfo import TimestampInfo


class TimeStampToken(ContentInfo):
    componentType = NamedTypes(
        NamedType('contentType', signedData),
        OptionalNamedType(
            name='content',
            asn1Object=SignedData().subtype(
                explicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0)
            )
        )
    )

    @property
    def content(self):
        return self[1]

    @property
    def info(self) -> TimestampInfo:
        x, s = decoder.decode(bytes(self.content['contentInfo']['content']))
        if s:
            raise ValueError('Incomplete decoding')
        x, s = decoder.decode(bytes(x), asn1Spec=TimestampInfo())
        if s:
            raise ValueError('Incomplete decoding')
        return x
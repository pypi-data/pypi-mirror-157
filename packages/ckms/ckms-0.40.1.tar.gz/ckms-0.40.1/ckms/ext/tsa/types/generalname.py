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
from pyasn1.type.char import IA5String
from pyasn1.type.namedtype import NamedType
from pyasn1.type.namedtype import NamedTypes
from pyasn1.type.univ import Any
from pyasn1.type.univ import Choice
from pyasn1.type.univ import ObjectIdentifier


class GeneralName(Choice):
    componentType = NamedTypes(
        NamedType(
            name='rfc822Name',
            asn1Object=IA5String().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 1)
            )
        ),
        #namedtype.NamedType('dNSName', univ.Any().subtype(
        #    implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 2))),
        #namedtype.NamedType('x400Address', univ.Any().subtype(
        #    implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3))),
        NamedType(
            name='directoryName',
            asn1Object=Any().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 4)
            )
        ),
        #namedtype.NamedType('ediPartyName', univ.Any().subtype(
        #    implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 5))),
        #namedtype.NamedType('uniformResourceIdentifier', char.IA5String().subtype(
        #    implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 6))),
        #namedtype.NamedType('iPAddress', univ.OctetString().subtype(
        #    implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 7))),
        NamedType(
            name='registeredID',
            asn1Object=ObjectIdentifier().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 8)
            )
        )
    )
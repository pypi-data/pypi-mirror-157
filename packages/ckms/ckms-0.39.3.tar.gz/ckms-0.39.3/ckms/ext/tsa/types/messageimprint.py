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
from typing import Any

from pyasn1.type import namedtype
from pyasn1.type import univ
from pyasn1_modules.rfc2459 import AlgorithmIdentifier


class MessageImprint(univ.Sequence):
    componentType: namedtype.NamedTypes = namedtype.NamedTypes(
        namedtype.NamedType('hashAlgorithm', AlgorithmIdentifier()),
        namedtype.NamedType('hashedMessage', univ.OctetString())
    )

    @property
    def algorithm(self) -> univ.ObjectIdentifier:
        return self[0][0] # type: ignore

    @property
    def hashed_message(self) -> Any:
        return self[1] # type: ignore
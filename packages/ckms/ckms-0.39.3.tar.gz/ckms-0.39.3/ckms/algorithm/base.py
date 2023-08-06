# Copyright 2022 Cochise Ruhulessin
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
from typing import Callable
from typing import Generator

from ckms.types import UnknownAlgorithm


class Algorithm(str):
    """The base class for all cryptographic algorithms."""
    __module__: str = 'ckms.algorithm'
    _registry: dict[str, 'Algorithm'] = {}
    allowed_ops: list[str]
    default_ops: list[str]
    digest: str | None
    padding: str | None
    use: str | None

    @classmethod
    def get(cls, name: str) -> 'Algorithm':
        return cls._registry[name]

    @staticmethod
    def register(
        name: str,
        *,
        base: type['Algorithm'],
        **params: Any
    ) -> None:
        """Register a new algorithm preset using the given class."""
        Algorithm._registry[name] = base(name, **params)

    @classmethod
    def __get_validators__(
        cls
    ) -> Generator[Callable[..., 'Algorithm'], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> 'Algorithm':
        if str(value) not in Algorithm._registry:
            raise UnknownAlgorithm(value)
        if isinstance(value, cls): # pragma: no cover
            return value
        return Algorithm._registry[value]

    def __new__(
        cls,
        name: str,
        allowed_ops: set[str] | None = None,
        default_ops: set[str] | None = None,
        digest: str | None = None,
        padding: str | None = None,
        use: str | None = None,
        *args: Any,
        **kwargs: Any
    ):
        if name in Algorithm._registry:
            return Algorithm._registry[name]

        self = str.__new__(cls, name)
        self.allowed_ops = allowed_ops or set()
        self.default_ops = default_ops or set()
        self.digest = digest
        self.padding = padding
        self.use = use
        return self

    def get_hasher(self) -> Any:
        """Return the hasher used to perform a cryptographic operation."""
        raise NotImplementedError

    def get_padding(self) -> Any:
        """Return an instance of the padding, if the algorithm implements it."""
        raise NotImplementedError
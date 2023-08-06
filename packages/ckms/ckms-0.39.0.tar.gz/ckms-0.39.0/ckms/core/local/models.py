"""Declares various models used by :class:`LocalProvider`."""
import pathlib
from typing import Any
from typing import Literal
from typing import TypeAlias

import pydantic
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import ed448
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.asymmetric import x25519
from typing_extensions import Annotated

from ckms import types
from ckms.core import const
from ckms.core import models
from ckms.core import Provider
from ckms.types import KeyUseType


class HMAC(bytes):

    @property
    def key(self) -> bytes:
        return bytes(self)

    def __repr__(self) -> str:
        return f'<HMAC: {len(self)}>'


class LocalKey(pydantic.BaseModel):
    path: str | pathlib.Path
    password: bytes | None
    encoding: Literal['pem'] = 'pem'

    async def setup(self, spec: 'LocalKeySpecification') -> Any:
        with open(self.path, 'rb') as f:
            return load_pem_private_key(f.read(), self.password)


class ParameterLessKey(pydantic.BaseModel):

    async def setup(self, spec: 'LocalKeySpecification') -> Any:
        assert isinstance(spec.provider, types.IProvider) # nosec
        return await spec.provider.generate(
            types.GenerateKeyOperation(
                kty=spec.kty,
                curve=spec.curve,
                use=spec.use
            )
        )


class TransientKey(pydantic.BaseModel):
    length: int

    async def setup(self, spec: 'LocalKeySpecification') -> Any:
        assert isinstance(spec.provider, types.IProvider) # nosec
        return await spec.provider.generate(
            types.GenerateKeyOperation(
                kty=spec.kty,
                length=self.length,
                curve=spec.curve,
                use=spec.use
            )
        )


class ContentEncryptionKey(pydantic.BaseModel):
    cek: bytes

    async def setup(self, spec: 'LocalKeySpecification') -> algorithms.AES:
        return algorithms.AES(self.cek)


class Key(pydantic.BaseModel):
    __root__: LocalKey | TransientKey

    @classmethod
    def parse_obj(cls: type[pydantic.BaseModel], obj: Any) -> pydantic.BaseModel:
        return super().parse_obj(obj).__root__ # type: ignore

    async def setup(self, spec: 'LocalKeySpecification') -> 'Key':
        return await self.__root__.setup(spec)


class LocalKeySpecification(models.KeySpecification):
    kty: str | None = None # type: ignore
    provider: Literal['local'] | Provider = 'local' # type: ignore
    key: Any

    @classmethod
    def autodiscover(
        cls,
        provider: types.IProvider,
        inspector: types.IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        values.update({
            'use': inspector.get_algorithm_use(values['algorithm'])
        })

    async def load(self) -> models.KeySpecification:
        """Load or generate the key as specified by the parameters."""
        assert isinstance(self.provider, types.IProvider)
        if not self.loaded:
            self.key = await self.key.setup(self)
        self.kid = self.provider.get_key_identifier(self)
        self.loaded = True
        return self

    def get_key_material(self) -> bytes:
        assert isinstance(self.provider, types.IProvider)
        return self.provider.inspector.to_pem(self.key)

    def has_key_material(self) -> bool:
        return True

    def get_private_key(self) -> Any:
        return self.key


class RSAKeySpecification(LocalKeySpecification):
    kty: Literal['RSA'] = 'RSA'
    #algorithm: types.RSAAlgorithmType | None = None
    use: KeyUseType | None = None
    key: LocalKey | TransientKey | rsa.RSAPrivateKey

    @classmethod
    def autodiscover(
        cls,
        provider: types.IProvider,
        inspector: types.IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        if not values.get('use') and not values.get('algorithm'):
            raise ValueError(
                "Unable to infer the key algorithm. Specify either the "
                "`algorithm` or `use` parameter."
            )
        if values.get('use') == 'sig':
            values['algorithm'] = const.DEFAULT_RSA_SIGNING_ALG
        elif values.get('use') == 'enc':
            values['algorithm'] = const.DEFAULT_RSA_ENCRYPTION_ALG
        else:
            values['use'] = inspector.get_algorithm_use(values['algorithm'])

    def get_public_key(self) -> rsa.RSAPublicKey:
        assert isinstance(self.key, rsa.RSAPrivateKey)
        return self.key.public_key()


class EllipticCurveKeySpecification(LocalKeySpecification):
    kty: Literal['EC'] = 'EC'
    #algorithm: types.EllipticCurveAlgorithmType | None = None
    curve: types.EllipticCurveType | None = None
    use: KeyUseType | None = None
    key: LocalKey | ParameterLessKey = ParameterLessKey()

    @classmethod
    def autodiscover(
        cls,
        provider: types.IProvider,
        inspector: types.IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        if not values.get('algorithm') and not values.get('use'):
            raise ValueError(
                "Specify either the `algorithm` parameter or the "
                "`use` parameter."
            )
        if values.get('algorithm'):
            values['use'] = inspector.get_algorithm_use(values['algorithm'])
        elif values.get('use') == 'sig' and not values.get('algorithm'):
            values['algorithm'] = const.DEFAULT_EC_SIGNING_ALGORITHM
        elif values.get('use') == 'enc' and not values.get('algorithm'):
            values['algorithm'] = const.DEFAULT_EC_ENCRYPTION_ALGORITHM
        else:
            raise ValueError("Unable to infer key parameters.")
        if not values.get('curve'):
            values['curve'] = inspector.get_algorithm_curve(values['algorithm'])

    def get_public_key(self) -> ec.EllipticCurvePublicKey:
        assert isinstance(self.key, ec.EllipticCurvePrivateKey)
        return self.key.public_key()


OKPPublic: TypeAlias = (
    ed448.Ed448PublicKey |
    ed25519.Ed25519PublicKey |
    x448.X448PublicKey |
    x25519.X25519PublicKey
)


OKPPrivate: TypeAlias = (
    ed448.Ed448PrivateKey |
    ed25519.Ed25519PrivateKey |
    x448.X448PrivateKey |
    x25519.X25519PrivateKey
)


class EdwardsCurveKeySpecification(LocalKeySpecification):
    kty: Literal['OKP'] = 'OKP'
    #algorithm: types.EdwardsCurveAlgorithmType | None
    curve: types.EdwardsCurveType | None
    key: LocalKey | ParameterLessKey = ParameterLessKey()
    use: KeyUseType

    @classmethod
    def autodiscover(
        cls,
        provider: types.IProvider,
        inspector: types.IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        if not values.get('use') and not values.get('curve'):
            raise ValueError(
                "Specify either the `use` parameter the `curve` parameter."
            )
        if values.get('curve') in {'Ed448', 'Ed25519'}:
            values['use'] = 'sig'
        elif values.get('curve') in {'X448', 'X25519'}:
            values['use'] = 'enc'
        elif values.get('use') == 'sig':
            values['curve'] = const.DEFAULT_ED_SIGNING_CURVE
        elif values.get('use') == 'enc':
            values['curve'] = const.DEFAULT_ED_ENCRYPTION_CURVE
        else:
            raise ValueError("Unable to infer key parameters.")
        if values['use'] == 'sig':
            values['algorithm'] = 'EdDSA'
        if values['use'] == 'enc' and not values.get('algorithm'):
            values['algorithm'] = const.DEFAULT_ED_ENCRYPTION_ALGORITHM

    def get_public_key(self) -> OKPPublic:
        assert isinstance(self.key, OKPPrivate)
        return self.key.public_key()


class SymmetricKeySpecification(LocalKeySpecification):
    kty: Literal['oct'] = 'oct'
    #algorithm: types.HMACAlgorithmType | types.AESAlgorithmType | None
    use: KeyUseType | None = None
    key: ContentEncryptionKey | LocalKey | TransientKey | ParameterLessKey | None

    @pydantic.root_validator(pre=True)
    def set_key_params(cls, values: dict[str, Any]) -> dict[str, Any]:
        algorithm = values.get('algorithm')
        if algorithm is not None and not bool(values.get('key')):
            # TODO: Very ugly
            if str.startswith(algorithm, 'A128'):
                length = 16
            elif str.startswith(algorithm, 'A192'):
                length = 24
            elif str.startswith(algorithm, 'A256'):
                length = 32
            else:
                raise NotImplementedError(algorithm)
            values['key'] = {'length': length}
        return values

    @classmethod
    def autodiscover(
        cls,
        provider: types.IProvider,
        inspector: types.IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        if not values.get('algorithm') and not values.get('use'):
            raise ValueError(
                "Specify either the `algorithm` parameter or the "
                "`use` parameter."
            )
        if values.get('algorithm'):
            values['use'] = inspector.get_algorithm_use(values['algorithm'])
        elif values.get('use') == 'sig':
            values['algorithm'] = const.DEFAULT_SYMMETRIC_SIGNING_ALGORITHM
        elif values.get('use') == 'enc':
            values['algorithm'] = const.DEFAULT_SYMMETRIC_ENCRYPTION_ALGORITHM

    def get_private_bytes(self) -> bytes:
        private = self.get_private_key()
        return private.key

    def get_private_key(self) -> algorithms.AES | HMAC:
        assert isinstance(self.key, (algorithms.AES, HMAC)), type(self.key)
        return self.key


class KeySpecification(models.BaseKeySpecification):
    __root__: Annotated[
        EllipticCurveKeySpecification |
        RSAKeySpecification |
        EdwardsCurveKeySpecification |
        SymmetricKeySpecification,
        pydantic.Field(discriminator='kty')
    ]

    @classmethod
    def generate(cls, **kwargs: Any) -> models.KeySpecification:
        return cls.parse_obj(kwargs)

    @classmethod
    def parse_obj(cls: type[pydantic.BaseModel], obj: Any) -> models.KeySpecification:
        return super().parse_obj(obj).__root__ # type: ignore
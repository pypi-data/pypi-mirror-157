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
import asyncio

import pytest
import pytest_asyncio

import ckms.core
from ckms.core import Keychain
from ckms.core.models import KeySpecification


SIGNING_KEYS_ASYMMETRIC: list[KeySpecification] = [
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'ec_sign_secp256k1_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'ec_sign_p256_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'ec_sign_p384_sha384',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_sign_pss_2048_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_sign_pss_3072_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_sign_pss_4096_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_sign_pss_4096_sha512',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_sign_pkcs1_2048_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_sign_pkcs1_3072_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_sign_pkcs1_4096_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_sign_pkcs1_4096_sha512',
        'version': 1
    }),
]

SIGNING_KEYS_SYMMETRIC: list[KeySpecification] = [
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'hmac_sha256',
        'version': 1
    })
]


ENCRYPTION_KEYS: list[KeySpecification] = [
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'aes256gcm',
        'version': 3
    }),

    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_decrypt_oaep_2048_sha1',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_decrypt_oaep_2048_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_decrypt_oaep_3072_sha1',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_decrypt_oaep_3072_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_decrypt_oaep_4096_sha1',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_decrypt_oaep_4096_sha256',
        'version': 1
    }),
    ckms.core.parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'rsa_decrypt_oaep_4096_sha512',
        'version': 1
    }),
]

SUPPORTED_KEYS: list[KeySpecification] = (
    SIGNING_KEYS_ASYMMETRIC
    + SIGNING_KEYS_SYMMETRIC
    + ENCRYPTION_KEYS
)


@pytest.fixture(scope='session')
def decrypter() -> Keychain:
    return Keychain()


@pytest.fixture(scope='session')
def encrypter() -> Keychain:
    return Keychain()


@pytest.fixture(scope='session')
def signer() -> Keychain:
    return Keychain()


@pytest.fixture(scope='session')
def verifier() -> Keychain:
    return Keychain()


@pytest_asyncio.fixture(scope='session', autouse=True) # type: ignore
async def setup_keys(
    decrypter: Keychain,
    encrypter: Keychain,
    signer: Keychain,
    verifier: Keychain
):
    await asyncio.gather(*SUPPORTED_KEYS)
    for spec in SUPPORTED_KEYS:
        assert spec.kid is not None
        assert spec.is_loaded()
        public = spec.as_public() if spec.is_asymmetric() else spec
        if spec.can_sign():
            signer.add(spec.kid, spec)
            verifier.add(public.kid, public) # type: ignore
        if spec.can_decrypt():
            decrypter.add(spec.kid, spec)
            encrypter.add(public.kid, public) # type: ignore
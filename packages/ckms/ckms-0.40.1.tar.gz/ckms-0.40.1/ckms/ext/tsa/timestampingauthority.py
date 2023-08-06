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
import inspect
from typing import cast
from typing import Any

from cryptography import x509

from ckms.types import Digest
from ckms.types import Message
from ckms.types import IHTTPClient
from .types import TimestampRequest
from .types import TimestampResponse


class TimestampingAuthority:
    """Provides an interface to create a timestamp using a specific authority."""
    __module__: str = 'ckms.ext.tsa'
    certificate: x509.Certificate
    digest: str
    url: str

    def __init__(
        self,
        *,
        url: str,
        crtpath: str,
        digest: str = 'sha1'
    ):
        self.certificate = x509.load_pem_x509_certificate(open(crtpath, 'rb').read())
        self.digest = digest
        self.url = url

    async def timestamp(
        self,
        *,
        client: Any,
        data: bytes | Message,
        digest: str | None = None
    ) -> bytes:
        """Create a timestamp of the given input data."""
        client = cast(IHTTPClient, client)
        if not isinstance(data, (Digest, Message)):
            data = Message(buf=data, digest=digest or self.digest)

        assert isinstance(data, Message)
        response = client.post(
            url=self.url,
            content=TimestampRequest.new(
                digest=await data.digest(),
                digestmod=digest or self.digest
            ),
            headers={
                'Content-Type': 'application/timestamp-query'
            }
        )
        if inspect.isawaitable(response):
            response = await response
        return TimestampResponse.frombytes(self.certificate, response.content)

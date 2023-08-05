from __future__ import absolute_import

from typing import Optional  # noqa: F401

from eth_keys.datatypes import (  # noqa: F401
    PrivateKey,
    PublicKey,
    Signature,
)
from eth_keys.exceptions import (
    BadSignature,
)

from .base import BaseECCBackend


def is_coincurve_available() -> bool:
    try:
        import coincurve  # noqa: F401
    except ImportError:
        return False
    else:
        return True


class CoinCurveECCBackend(BaseECCBackend):
    def __init__(self) -> None:
        try:
            import coincurve
        except ImportError:
            raise ImportError("The CoinCurveECCBackend requires the coincurve \
                               library which is not available for import.")
        self.keys = coincurve.keys
        self.ecdsa = coincurve.ecdsa
        super(CoinCurveECCBackend, self).__init__()

    def ecdsa_sign(self,
                   msg_hash: bytes,
                   private_key: PrivateKey) -> Signature:
        private_key_bytes = private_key.to_bytes()
        signature_bytes = self.keys.PrivateKey(private_key_bytes).sign_recoverable(
            msg_hash,
            hasher=None,
        )
        signature = Signature(signature_bytes, backend=self)
        return signature

    def ecdsa_recover(self,
                      msg_hash: bytes,
                      signature: Signature) -> PublicKey:
        signature_bytes = signature.to_bytes()
        try:
            public_key_bytes = self.keys.PublicKey.from_signature_and_message(
                signature_bytes,
                msg_hash,
                hasher=None,
            ).format(compressed=False)[1:]
        except (ValueError, Exception) as err:
            # `coincurve` can raise `ValueError` or `Exception` dependending on
            # how the signature is invalid.
            raise BadSignature(str(err))
        public_key = PublicKey(public_key_bytes, backend=self)
        return public_key

    def private_key_to_public_key(self, private_key: PrivateKey) -> PublicKey:
        public_key_bytes = self.keys.PrivateKey(private_key.to_bytes()).public_key.format(
            compressed=False,
        )[1:]
        return PublicKey(public_key_bytes, backend=self)

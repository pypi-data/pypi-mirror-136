from cryptography.hazmat.primitives.ciphers import aead

from .common import ConfidentialityIntegrityCipher

class AES_GCMCipher(ConfidentialityIntegrityCipher):
    @classmethod
    def get_iv_length(cls) -> int:
        return 12

    @classmethod
    def encrypt_with_key_iv(
        cls,
        plain_bytes: bytes,
        cipher_key: bytes,
        initialization_vector: bytes
    ) -> bytes:
        return aead.AESGCM(cipher_key).encrypt(
            initialization_vector,
            plain_bytes,
            None
        )

    @classmethod
    def decrypt_with_key_iv(
        cls,
        cipher_bytes: bytes,
        cipher_key: bytes,
        initialization_vector: bytes
    ) -> bytes:
        return aead.AESGCM(cipher_key).decrypt(
            initialization_vector,
            cipher_bytes,
            None
        )


class ChaCha20Poly1305Cipher(ConfidentialityIntegrityCipher):
    @classmethod
    def get_iv_length(cls) -> int:
        return 64

    @classmethod
    def encrypt_with_key_iv(
        cls,
        plain_bytes: bytes,
        cipher_key: bytes,
        initialization_vector: bytes
    ) -> bytes:
        return aead.ChaCha20Poly1305(cipher_key).encrypt(
            initialization_vector,
            plain_bytes,
            None
        )

    @classmethod
    def decrypt_with_key_iv(
        cls,
        cipher_bytes: bytes,
        cipher_key: bytes,
        initialization_vector: bytes
    ) -> bytes:
        return aead.ChaCha20Poly1305(cipher_key).decrypt(
            initialization_vector,
            cipher_bytes,
            None
        )

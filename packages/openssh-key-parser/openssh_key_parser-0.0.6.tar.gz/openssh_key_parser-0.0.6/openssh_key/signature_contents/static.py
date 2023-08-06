import abc
import types
import typing

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dsa as cryptography_dsa
from cryptography.hazmat.primitives.asymmetric import ec as cryptography_ec
from cryptography.hazmat.primitives.asymmetric import \
    ed25519 as cryptography_ed25519
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa as cryptography_rsa
from cryptography.hazmat.primitives.asymmetric import \
    utils as cryptography_utils
from openssh_key.key_params import (DSSPrivateKeyParams, DSSPublicKeyParams,
                                    ECDSA_NISTP256_PrivateKeyParams,
                                    ECDSA_NISTP256_PublicKeyParams,
                                    ECDSA_NISTP384_PrivateKeyParams,
                                    ECDSA_NISTP384_PublicKeyParams,
                                    ECDSA_NISTP521_PrivateKeyParams,
                                    ECDSA_NISTP521_PublicKeyParams,
                                    ECDSAPrivateKeyParams,
                                    ECDSAPublicKeyParams,
                                    Ed25519PrivateKeyParams,
                                    Ed25519PublicKeyParams,
                                    PrivateKeyParamsTypeVar,
                                    PublicKeyParamsTypeVar,
                                    RSAPrivateKeyParams, RSAPublicKeyParams)
from openssh_key.key_params.ecdsa import (ECDSAPrivateKeyParamsTypeVar,
                                          ECDSAPublicKeyParamsTypeVar)
from openssh_key.pascal_style_byte_stream import (FormatInstructionsDict,
                                                  PascalStyleByteStream,
                                                  PascalStyleDict,
                                                  PascalStyleFormatInstruction)
from openssh_key.utils import readonly_static_property

from .common import SignatureContents, SignatureContentsTypeVar


class StaticKeySignatureContents(
    SignatureContents[
        PublicKeyParamsTypeVar,
        PrivateKeyParamsTypeVar,
        SignatureContentsTypeVar
    ],
    PascalStyleDict,
):
    __STATIC_KEY_SIGNATURE_CONTENTS_FORMAT_INSTRUCTIONS_DICT: FormatInstructionsDict = {
        'signature': PascalStyleFormatInstruction.BYTES,
    }

    @classmethod
    def get_format_instructions_dict(cls) -> FormatInstructionsDict:
        return cls.__STATIC_KEY_SIGNATURE_CONTENTS_FORMAT_INSTRUCTIONS_DICT


class RSASignatureContents(
    StaticKeySignatureContents[
        RSAPublicKeyParams,
        RSAPrivateKeyParams,
        'RSASignatureContents'
    ],
    abc.ABC
):
    @classmethod
    @abc.abstractmethod
    def get_hash_algorithm(cls) -> typing.Type[hashes.HashAlgorithm]:
        raise NotImplementedError('abstract method')

    HASH_ALGORITHM = readonly_static_property(get_hash_algorithm)

    def verify(
        self,
        public_key_params: RSAPublicKeyParams,
        challenge: bytes,
    ) -> bool:
        try:
            public_key_params.convert_to(cryptography_rsa.RSAPublicKey).verify(
                self['signature'],
                challenge,
                padding.PKCS1v15(),
                self.HASH_ALGORITHM()
            )
        except InvalidSignature:
            return False
        return True

    @classmethod
    def sign(
        cls,
        private_key_params: RSAPrivateKeyParams,
        challenge: bytes,
    ) -> 'RSASignatureContents':
        return cls({
            'signature': private_key_params.convert_to(
                cryptography_rsa.RSAPrivateKey
            ).sign(
                challenge,
                padding.PKCS1v15(),
                cls.HASH_ALGORITHM()
            )
        })


class RSA_SHA1_SignatureContents(RSASignatureContents):
    @classmethod
    def get_hash_algorithm(cls) -> typing.Type[hashes.HashAlgorithm]:
        return hashes.SHA1


class RSA_SHA256_SignatureContents(RSASignatureContents):
    @classmethod
    def get_hash_algorithm(cls) -> typing.Type[hashes.HashAlgorithm]:
        return hashes.SHA256


class RSA_SHA512_SignatureContents(RSASignatureContents):
    @classmethod
    def get_hash_algorithm(cls) -> typing.Type[hashes.HashAlgorithm]:
        return hashes.SHA512


class Ed25519SignatureContents(
    StaticKeySignatureContents[
        Ed25519PublicKeyParams,
        Ed25519PrivateKeyParams,
        'Ed25519SignatureContents'
    ]
):
    def verify(
        self,
        public_key_params: Ed25519PublicKeyParams,
        challenge: bytes,
    ) -> bool:
        try:
            public_key_params.convert_to(cryptography_ed25519.Ed25519PublicKey).verify(
                self['signature'],
                challenge
            )
        except InvalidSignature:
            return False
        return True

    @classmethod
    def sign(
        cls,
        private_key_params: Ed25519PrivateKeyParams,
        challenge: bytes,
    ) -> 'Ed25519SignatureContents':
        return cls({
            'signature': private_key_params.convert_to(
                cryptography_ed25519.Ed25519PrivateKey
            ).sign(
                challenge
            )
        })


class DSSSignatureContents(
    StaticKeySignatureContents[
        DSSPublicKeyParams,
        DSSPrivateKeyParams,
        'DSSSignatureContents'
    ],
    abc.ABC
):
    @classmethod
    def get_r_length(cls) -> int:
        return 20

    R_LENGTH = readonly_static_property(get_r_length)

    @classmethod
    def get_s_length(cls) -> int:
        return 20

    S_LENGTH = readonly_static_property(get_s_length)

    def verify(
        self,
        public_key_params: DSSPublicKeyParams,
        challenge: bytes,
    ) -> bool:
        if len(self['signature']) != self.R_LENGTH + self.S_LENGTH:
            return False
        r = self['signature'][:self.R_LENGTH]
        s = self['signature'][self.R_LENGTH:(self.R_LENGTH + self.S_LENGTH)]
        dss_signature = cryptography_utils.encode_dss_signature(r, s)
        try:
            public_key_params.convert_to(cryptography_dsa.DSAPublicKey).verify(
                dss_signature,
                challenge,
                hashes.SHA1()
            )
        except InvalidSignature:
            return False
        return True

    @classmethod
    def sign(
        cls,
        private_key_params: DSSPrivateKeyParams,
        challenge: bytes,
    ) -> 'DSSSignatureContents':
        dss_signature = private_key_params.convert_to(
            cryptography_dsa.DSAPrivateKey
        ).sign(
            challenge,
            hashes.SHA1()
        )
        r, s = cryptography_utils.decode_dss_signature(dss_signature)
        byte_string = r.to_bytes(
            cls.R_LENGTH, 'big'
        ) + s.to_bytes(
            cls.S_LENGTH, 'big'
        )
        return cls({
            'signature': byte_string
        })


class ECDSASignatureContents(
    StaticKeySignatureContents[
        ECDSAPublicKeyParams,
        ECDSAPrivateKeyParams,
        'ECDSASignatureContents[ECDSAPublicKeyParamsTypeVar, ECDSAPrivateKeyParamsTypeVar, SignatureContentsTypeVar]'
    ],
    typing.Generic[
        ECDSAPublicKeyParamsTypeVar,
        ECDSAPrivateKeyParamsTypeVar,
        SignatureContentsTypeVar
    ],
):
    @classmethod
    @abc.abstractmethod
    def get_hash_algorithm(cls) -> typing.Type[hashes.HashAlgorithm]:
        raise NotImplementedError('abstract method')

    HASH_ALGORITHM = readonly_static_property(get_hash_algorithm)

    __ECDSA_SIGNATURE_FORMAT_INSTRUCTIONS_DICT = {
        'r': PascalStyleFormatInstruction.MPINT,
        's': PascalStyleFormatInstruction.MPINT,
    }

    @classmethod
    def get_ecdsa_signature_format_instructions_dict(cls) -> FormatInstructionsDict:
        return types.MappingProxyType(
            cls.__ECDSA_SIGNATURE_FORMAT_INSTRUCTIONS_DICT
        )

    ECDSA_SIGNATURE_FORMAT_INSTRUCTIONS_DICT = readonly_static_property(
        get_ecdsa_signature_format_instructions_dict
    )

    def verify(
        self,
        public_key_params: ECDSAPublicKeyParams,
        challenge: bytes
    ) -> bool:
        signature = PascalStyleByteStream(
            self['signature']
        ).read_from_format_instructions_dict(
            self.ECDSA_SIGNATURE_FORMAT_INSTRUCTIONS_DICT
        )
        dss_signature = cryptography_utils.encode_dss_signature(
            signature['r'], signature['s']
        )
        try:
            public_key_params.convert_to(
                cryptography_ec.EllipticCurvePublicKey
            ).verify(
                dss_signature,
                challenge,
                cryptography_ec.ECDSA(self.HASH_ALGORITHM())
            )
        except InvalidSignature:
            return False
        return True

    @classmethod
    def sign(
        cls,
        private_key_params: ECDSAPrivateKeyParams,
        challenge: bytes,
    ) -> 'ECDSASignatureContents[ECDSAPublicKeyParamsTypeVar, ECDSAPrivateKeyParamsTypeVar, SignatureContentsTypeVar]':
        dss_signature = private_key_params.convert_to(
            cryptography_ec.EllipticCurvePrivateKey
        ).sign(
            challenge,
            cryptography_ec.ECDSA(cls.HASH_ALGORITHM())
        )
        r, s = cryptography_utils.decode_dss_signature(dss_signature)
        byte_stream = PascalStyleByteStream()
        byte_stream.write_from_format_instructions_dict(
            cls.ECDSA_SIGNATURE_FORMAT_INSTRUCTIONS_DICT,
            {
                'r': r,
                's': s,
            }
        )
        return cls({
            'signature': byte_stream.getvalue()
        })


class ECDSA_NISTP256_SignatureContents(ECDSASignatureContents[
    ECDSA_NISTP256_PublicKeyParams,
    ECDSA_NISTP256_PrivateKeyParams,
    'ECDSA_NISTP256_SignatureContents'
]):
    @classmethod
    def get_hash_algorithm(cls) -> typing.Type[hashes.HashAlgorithm]:
        return hashes.SHA256


class ECDSA_NISTP384_SignatureContents(ECDSASignatureContents[
    ECDSA_NISTP384_PublicKeyParams,
    ECDSA_NISTP384_PrivateKeyParams,
    'ECDSA_NISTP384_SignatureContents'
]):
    @classmethod
    def get_hash_algorithm(cls) -> typing.Type[hashes.HashAlgorithm]:
        return hashes.SHA384


class ECDSA_NISTP521_SignatureContents(ECDSASignatureContents[
    ECDSA_NISTP521_PublicKeyParams,
    ECDSA_NISTP521_PrivateKeyParams,
    'ECDSA_NISTP521_SignatureContents'
]):
    @classmethod
    def get_hash_algorithm(cls) -> typing.Type[hashes.HashAlgorithm]:
        return hashes.SHA512

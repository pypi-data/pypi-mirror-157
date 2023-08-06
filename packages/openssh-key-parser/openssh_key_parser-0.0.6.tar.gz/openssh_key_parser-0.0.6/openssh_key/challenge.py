import abc
import types
import typing
import warnings
from openssh_key import utils

from openssh_key.pascal_style_byte_stream import FormatInstructionsDict, PascalStyleByteStream, PascalStyleDict, PascalStyleFormatInstruction


ChallengeTypeVar = typing.TypeVar(
    'ChallengeTypeVar',
    bound='Challenge[typing.Any]'
)


class Challenge(typing.Generic[ChallengeTypeVar], abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_byte_stream(
        cls,
        byte_stream: PascalStyleByteStream
    ) -> ChallengeTypeVar:
        raise NotImplementedError('abstract method')

    @classmethod
    def from_bytes(cls, byte_string: bytes) -> ChallengeTypeVar:
        byte_stream = PascalStyleByteStream(byte_string)

        challenge = cls.from_byte_stream(byte_stream)

        remainder = byte_stream.read()
        if len(remainder) > 0:
            warnings.warn('Excess bytes in challenge')
            challenge.remainder = remainder

        return challenge

    @abc.abstractmethod
    def pack_bytes(self) -> bytes:
        raise NotImplementedError('abstract method')


class SSH2Challenge(Challenge['SSH2Challenge'], PascalStyleDict):
    __SSH2_CHALLENGE_FORMAT_INSTRUCTIONS_DICT: FormatInstructionsDict = {
        'session_id': PascalStyleFormatInstruction.STRING,
        'packet_type': '>B',
        'user_name': PascalStyleFormatInstruction.STRING,
        'service_name': PascalStyleFormatInstruction.STRING,
        'auth_type': PascalStyleFormatInstruction.STRING,
        'includes_sig': '>B',
        'sig_alg_name': PascalStyleFormatInstruction.STRING,
        'public_key': PascalStyleFormatInstruction.STRING
    }

    @classmethod
    def get_format_instructions_dict(cls) -> FormatInstructionsDict:
        return types.MappingProxyType(
            SSH2Challenge.__SSH2_CHALLENGE_FORMAT_INSTRUCTIONS_DICT
        )

    FORMAT_INSTRUCTIONS_DICT = utils.readonly_static_property(
        get_format_instructions_dict
    )

    def pack_bytes(self) -> bytes:
        byte_stream = PascalStyleByteStream()
        byte_stream.write_from_format_instructions_dict(
            self.FORMAT_INSTRUCTIONS_DICT,
            self
        )
        return byte_stream.getvalue()

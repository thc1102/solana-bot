from construct import Bit, BitsSwapped, BitStruct, Bytes, BytesInteger, Int8ul, Int64ul, Padding, Adapter, Int32ul
from solders.pubkey import Pubkey


def u8(key: str):
    return key / Int8ul


def u32(key: str):
    return key / Int32ul


def u64(key: str):
    return key / Int64ul


def u128(key: str):
    return key / BytesInteger(16, False, True)


def publicKey(key: str):
    return key / PublicKeyAdapter(Bytes(32))


def pad(key: str, length: int):
    return key / Padding(length)


def blob(key: str, length: int):
    return key / Bytes(length)


class PublicKeyAdapter(Adapter):
    def _decode(self, obj, context, path):
        # 将字节序列转换为PublicKey对象
        return Pubkey(obj)

    def _encode(self, obj, context, path):
        # 将PublicKey对象转换为字节序列
        return bytes(obj)


class WideBitsBuilder:
    def __init__(self, property_name: str, _len=64):
        self.property_name = property_name
        self.fields = []
        self.len = _len

    def add_boolean(self, key: str):
        assert len(self.fields) < self.len
        self.fields.append(key / Bit)

    def get_layout(self):
        return self.property_name / BitsSwapped(
            BitStruct(*self.fields + [Padding(self.len - len(self.fields))])
        )

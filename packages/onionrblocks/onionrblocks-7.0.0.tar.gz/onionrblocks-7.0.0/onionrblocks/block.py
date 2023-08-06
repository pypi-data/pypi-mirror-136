from enum import auto
from hashlib import new
from typing import Union, TYPE_CHECKING
from binascii import hexlify

if TYPE_CHECKING:
    from kasten.generator import KastenPacked
from kasten import Kasten
from . import generators

class Block:
    def __init__(
            self, block_hash: str,
            raw_block_data: 'KastenPacked', auto_verify=True):
        generator = generators.AnonVDFGenerator
        bl = Kasten(
            block_hash,
            raw_block_data,
            generator, auto_check_generator=auto_verify)
        self.timestamp = bl.get_timestamp()
        self.metadata = bl.get_metadata()
        self.ttl = self.metadata['ttl']
        self.id = block_hash
        self.type = bl.get_data_type()
        self.data = bl.data
        self.raw = bl.get_packed()


def kasten_to_block(kasten: Kasten):
    return Block(hexlify(kasten.id), kasten.get_packed(), auto_verify=False)


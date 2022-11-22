import bitstring as bs 
from bitstring import BitArray as ba
from math import log

class cache:
    def __init__(self,block_size=16,num_blocks=16,associativity = 1):
        #2d cache data structure with all rows init to 0's
        self.cache = self._create_cache(block_size,num_blocks,associativity)
    
    def _create_cache(self,block_size,num_blocks,associativity=1):
        num_sets = 0
        valid_bits = 1
        addr_size = log(num_blocks,2)
        offset = log(block_size,2)
        if associativity == 1:
            num_sets = num_blocks
        elif associativity == 2:
            num_sets = num_blocks/2

        index_bits = log(num_sets,2)
        tag_bits = addr_size - index_bits - offset
        row_len = block_size + tag_bits + index_bits + valid_bits
        #2d cache data structure with all rows init to 0's
        return [bs.BitArray(row_len) for i in range(num_blocks)]
        
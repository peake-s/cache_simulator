import bitstring as bs 
from bitstring import BitArray as ba
from math import log

class cache:
    def __init__(self,block_size=16,num_blocks=16,associativity = 1):
        #2d cache data structure with all rows init to 0's
        #rowlen - index_bits
        #contains ending index of index
        self.index_bits = 0
        #contains ending index of valid bit
        self.valid_bit = 1
        #contains ending index of tag bits
        self.tag_bits = 0
        self.offset = 0
        self.address_size = 32
        self._addr_structure(block_size,num_blocks,associativity)
        self.cache = self._create_cache(num_blocks,32)

    def _addr_structure(self,block_size,num_blocks,associativity=1):
        num_sets = 0
        valid_bits = 1
        #addr_size = log(num_blocks,2)
        addr_size =32
        self.offset = int(log(block_size,2))
        if associativity == 1:
            num_sets = num_blocks
        elif associativity == 2:
            num_sets = num_blocks/2
        
        #[]
        self.index_bits = int(log(num_sets,2))
        self.tag_bits = addr_size - self.index_bits - self.offset - valid_bits
        #row_len = block_size + self.tag_bits + self.index_bits + valid_bits

    def _create_cache(num_blocks,row_len):
        #2d cache data structure with all rows init to 0's
        return [bs.BitArray(row_len) for i in range(num_blocks)]
        
class direct_mapping:
    def __init__(self):
        pass

class associative_mapping:
    def __init__(self):
        pass

def read_addr_file():
    pass

def read_input():
    pass

def main():
    c = cache(16,64)
    print(f"idx: {c.index_bits} tag: {c.tag_bits} off: {c.offset}")
    print(c.cache[0])   

if __name__ == "__main__":
    main()
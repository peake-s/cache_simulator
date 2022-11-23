import bitstring as bs 
from bitstring import BitArray as ba
from math import log
import sys
import argparse
import pandas as pd
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
        self.size = num_blocks * block_size

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
    def __init__(self,cache):
        self.cache = cache
        self.hits = 0
        self.misses = 0
        self.num_reads = 0

    def cache_read(self):
        pass

    def check_valid(self):
        pass

    def check_tag(self):
        pass

class associative_mapping:
    def __init__(self):
        pass

def read_addr_file(file):
    addr = pd.read_csv(file, delimiter=' ', header=None)
    return addr[0].values.tolist()

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input_file")
    parser.add_argument("-b","--block_size")
    parser.add_argument("-n","--num_blocks")
    parser.add_argument("-a", "--associativity")
    parser.add_argument("-t","--hit_time")
    parser.add_argument("-m","--miss_time")
    parser.add_argument("-l","--lru")
    args = parser.parse_args()
    address_data = read_addr_file(args.input_file)
    block_size = args.block_size
    num_block = args.num_blocks
    associativity = args.associativity
    hit_time = args.hit_time
    miss_time = args.miss_time
    lru = args.lru
    cche = cache(block_size=block_size,num_blocks=num_block,associativity=1)

if __name__ == "__main__":
    main(sys.argv[1:])
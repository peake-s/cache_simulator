import bitstring as bs 
from bitstring import BitArray
from math import log,pow
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
        self.num_sets = 0
        self.offset = 0
        self.address_size = 32
        self.hits = 0
        self.misses = 0
        self.num_reads = 0
        self.block_size = block_size
        self.num_blocks = num_blocks
        self._addr_structure(self.block_size,self.num_blocks,associativity)
        self.size = int(pow(2,num_blocks))
        self.cache = self._create_cache(self.num_blocks*block_size,(self.block_size+1+self.tag_bits))
        print(self.tag_bits)
        self._check_validity(associativity,num_blocks,self.num_sets)

    def _addr_structure(self,block_size,num_blocks,associativity=1):
        valid_bits = 1
        #addr_size = log(num_blocks,2)
        addr_size =32
        #self.offset = int(log(block_size,2))
        self.offset = int(num_blocks/block_size)
        if associativity == 1:
            self.num_sets = num_blocks
        elif associativity == 2:
            self.num_sets = num_blocks/2
        
        #[]
        self.index_bits = int(log(self.num_sets,2))
        self.tag_bits = addr_size - self.index_bits - self.offset 
        #row_len = block_size + self.tag_bits + self.index_bits + valid_bits

    def _create_cache(self,num_blocks,row_len):
        #2d cache data structure with all rows init to 0's
        return [BitArray(row_len) for i in range(num_blocks)]
        #return [BitArray(row_len)] * num_blocks

    def _check_validity(self,asc,nb,ns):
        if asc*ns != nb:
            print("invalid number of blocks")
            exit()

    def _block_addr(self,address):
        return address/self.block_size
    
    def _index(self,block_addr):
        return block_addr%self.num_sets

    def _check_valid_bit(self,idx):
        vb = self.cache[idx][0]
        
        if vb:
            #self.cache[idx][0] = 0
            return True
        else:
            self.misses += 1
            self.cache[idx][0] = 1
            return False

    def _check_tag(self,idx,tag):
        act_tag = self.cache[idx][1:self.tag_bits+1]
        #print(self.cache[idx][1:self.tag_bits+1])
        #print(f"act tag: {act_tag.i} tag: {tag}")
        if tag == act_tag.i:
            self.hits += 1
            #self.cache[idx][1:self.tag_bits+1] = BitArray(int=tag,length=self.tag_bits)
        else:
            self.misses += 1
            self.cache[idx][1:self.tag_bits+1] = BitArray(int=tag,length=self.tag_bits)

    def _find_tag(self,address):
        return address/(self.num_blocks*self.block_size)

    def cache_read(self,address):
        #find address
        block_addr = int(self._block_addr(address))
        #print(f"ba: {block_addr}")
        #go to line number
        index = int(self._index(block_addr))
        #print(index)
        tag = int(self._find_tag(address))
        #check valid bit
        vb = self._check_valid_bit(index)
        #print(f"idx: {index} vb: {vb}")
        #if 0, cache miss
        #set valid bit to 1
        #set tag
        if vb:
            self._check_tag(index,tag)
    
    
    def read_all(self,addr_list):
        for addr in addr_list:
            self.cache_read(int(addr,base=16))

        cache_reads = len(addr_list)
        self.results(cache_reads)

    def results(self,cache_reads):
        hit_ratio = self.hits/cache_reads
        miss_ratio = 1 - hit_ratio

        print(f"Reads: {cache_reads}")
        print(f"Hits: {self.hits}")
        print(f"Misses: {self.misses}")
        print(f"Hit rate: {(hit_ratio*100):.2f}%")
        print(f"Miss rate: {(miss_ratio*100):.2f}%")


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
    cche = cache(block_size=int(block_size),num_blocks=int(num_block),associativity=1)
    cche.read_all(address_data)


if __name__ == "__main__":
    main(sys.argv[1:])
import pandas as pd
from math import log,pow
import numpy as np
import sys
import argparse

class cache:
    def __init__(self,num_blocks,associativity,isz,tsz,off,bsz,replacement_policy=None):
        self.idx_sz = isz
        self.tag_sz = tsz
        self.off_sz = off
        self.block_sz = bsz
        num_sets = int(num_blocks/associativity)
        self._check_validity(num_blocks,associativity,num_sets)
        df = self._init_df(num_blocks,associativity,num_sets,replacement_policy)
        self.cache = pd.DataFrame(df)
        #self.num_sets = int(num_blocks/associativity)
        
    def _check_validity(self,num_blocks,associativity,num_sets):
        if associativity*num_sets != num_blocks:
            print("invalid number of blocks")
            exit()

    def _init_df(self,num_blocks,associativity,num_sets,replacement_policy):
        df = {}

        if associativity == 1:
            df = {
              'index': [(bin(i)[2:].zfill(self.idx_sz)) for i in range(num_blocks)],
              'valid':[bin(0)[2:] for i in range(num_blocks)], 
              'tag': [(bin(0)[2:].zfill(self.tag_sz)) for i in range(num_blocks)], 
              'data': [(bin(0)[2:].zfill(self.block_sz)) for i in range(num_blocks)],
             }
        elif associativity > 1 and replacement_policy == 'LRU':
            tags = [[(bin(0)[2:].zfill(self.tag_sz))]*associativity] * num_sets
            valid = [[(bin(0)[2:])]*associativity] * num_sets
            data = [[(bin(0)[2:].zfill(self.block_sz))]*associativity] * num_sets
            LRU = [[(bin(0)[2:].zfill(self.block_sz))]*associativity] * num_sets
            df = {
              'index': [(bin(i)[2:].zfill(self.idx_sz))for i in range(int(num_blocks/associativity))],
              'valid':valid, 
              'tag': tags, 
              'LRU': LRU,
              'data': data
             }
        else:
            tags = [[(bin(0)[2:].zfill(self.tag_sz))]*associativity] * num_sets
            valid = [[(bin(0)[2:])]*associativity] * num_sets
            data = [[(bin(0)[2:].zfill(self.block_sz))]*associativity] * num_sets
            df = {
              'index': [(bin(i)[2:].zfill(self.idx_sz))for i in range(int(num_blocks/associativity))],
              'valid':valid, 
              'tag': tags, 
              'data': data
             }

        return df

class direct_mapped():
    def __init__(self,block_size =1, num_blocks =16):
        self.offset = int(num_blocks/block_size)
        self.index = int(log(num_blocks,2))
        self.valid_bits = 1
        self.associativity = 1
        self.block_size = block_size
        self.num_blocks = num_blocks
        self.hits = 0
        self.misses = 0
        #address bits always 32
        addr_size = 32
        self.tag = addr_size - self.index - self.offset
        self.cache = cache(self.num_blocks,self.associativity,self.index,
                           self.tag,self.offset,self.block_size)

    def _block_addr(self,address) -> int:
        return int(address/self.block_size)
    
    def _index(self,block_addr) -> int:
        return block_addr%self.num_blocks  
    
    def _check_valid_bit(self,idx)-> bool:
        vb = self.cache.at[idx, 'index']

        if vb:
            return True
        else:
            self.misses += 1
            self.cache.at[idx, 'index'] = 1
            return False

    def _check_tag(self,idx,tag):
        actual_tag = self.cache.at[idx,'tag']
        if actual_tag == tag:
            self.hits += 1
        else:
            self.misses += 1
            self.cache.at[idx,'tag'] = tag

    def _find_tag(self,address)->int:
        return int(address/(self.num_blocks*self.block_size))
        

class associativity():
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
    block_size = args.block_size
    num_block = args.num_blocks
    associativity = args.associativity
    hit_time = args.hit_time
    miss_time = args.miss_time
    lru = args.lru
    isz=int(log(int(int(args.num_blocks)/int(args.associativity)),2))
    off = int(int(args.num_blocks)/int(args.block_size))
    tsz = 32 -isz -off
    address_data = read_addr_file(args.input_file)

    c = cache(16,2,isz,tsz,off,int(args.block_size),'LRU')
    print(c.cache)

if __name__ == "__main__":
    main(sys.argv[1:])
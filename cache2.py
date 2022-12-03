import pandas as pd
from math import log,pow
import numpy as np
import sys
import argparse

class cache:
    def __init__(self,num_blocks,associativity,isz,tsz,off,bsz):
        self.idx_sz = isz
        self.tag_sz = tsz
        self.off_sz = off
        self.block_sz = bsz
        df = self._init_df(num_blocks,associativity)
        self.cache = pd.DataFrame(df)
        #self.num_sets = int(num_blocks/associativity)
        
    def _check_validity(self,num_blocks,associativity,num_sets):
        if associativity*num_sets != num_blocks:
            print("invalid number of blocks")
            exit()

    def _init_df(self,num_blocks,associativity):
        df = {}

        if associativity == 1:
            df = {
              'index': [('0x'+hex(i)[2:].zfill(self.idx_sz)) for i in range(num_blocks)],
              'valid':[bin(0)[2:] for i in range(num_blocks)], 
              'tag': [('0x'+ hex(0)[2:].zfill(self.tag_sz)) for i in range(num_blocks)], 
              'data': [('0x' + hex(0)[2:].zfill(self.block_sz)) for i in range(num_blocks)],
             }
        else:
            tags=valid=LRU=data = [('0','0')] * int(num_blocks/associativity)
            df = {
              'index': [i for i in range(int(num_blocks/associativity))],
              'valid':valid, 
              'tag': tags, 
              'LRU': LRU,
              'data': data
             }
        return df

class direct_mapped():
    def __init__(self,block_size =1, num_blocks =16):
        self.offset = int(num_blocks/block_size)
        self.index = int(log(num_blocks,2))
        self.valid_bits = 1
        #address bits always 32
        addr_size = 32
        self.tag = addr_size - self.index - self.offset
    
    

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

    c = cache(16,1,isz,tsz,off,int(args.block_size))
    print(c.cache)

if __name__ == "__main__":
    main(sys.argv[1:])
import pandas as pd
from math import log,pow
from random import randint
import numpy as np
import sys
import argparse
import warnings
warnings.simplefilter(action='ignore',category=FutureWarning)

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
              'valid':[0 for i in range(num_blocks)], 
              'tag': [(bin(0)[2:].zfill(self.tag_sz)) for i in range(num_blocks)], 
              'data': [(bin(0)[2:].zfill(self.block_sz)) for i in range(num_blocks)],
             }
        elif associativity > 1 and replacement_policy == 'LRU':
            tags = [([None]*associativity) for _ in range(num_sets)]
            valid = [([0]*associativity) for _ in range(num_sets)] 
            data = [([(bin(0)[2:].zfill(self.block_sz))]*associativity) for _ in range(num_sets)] 
            LRU = [[0 for __ in range(associativity)] for _ in range (num_sets)]

            df = {
              'index': [(bin(i)[2:].zfill(self.idx_sz))for i in range(int(num_blocks/associativity))],
              'valid':valid, 
              'tag': tags, 
              'lru': LRU,
              'data': data
             }
        else:
            tags = [([(bin(0)[2:].zfill(self.tag_sz))]*associativity) for _ in range(num_sets)] 
            valid = [([(bin(0)[2:])]*associativity) for _ in range(num_sets)] 
            data = [([(bin(0)[2:].zfill(self.block_sz))]*associativity) for _ in range(num_sets)] 
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
        vb = self.cache.cache.at[idx, 'valid']

        if vb:
            return True
        else:
            self.misses += 1
            self.cache.cache.at[idx, 'valid'] = 1
            return False

    def _check_tag(self,idx,tag) -> bool:
        actual_tag = self.cache.cache.at[idx,'tag']

        tag2 = bin(tag)[2:].zfill(self.tag)
        if actual_tag == tag2:
            self.hits += 1
            return True
        else:
            self.misses += 1
            self.cache.cache.at[idx,'tag'] = tag2
            return False

    def _find_tag(self,address)->int:
        return int(address/(self.num_blocks*self.block_size))

    def _input_data(self,addr,idx):
        self.cache.cache.at[idx, 'data'] = addr
        
    def direct_read(self,address):
        block_addr = self._block_addr(address)
        index = int(self._index(block_addr))
        tag = int(self._find_tag(address))
        vb = self._check_valid_bit(index)

        if vb == 1:
            if not self._check_tag(index,tag):
                self._input_data(address,index)
        else:
            self._input_data(address,index)
    
    def read_all(self,addr_list):
        [self.direct_read(int(add,base=16)) for add in addr_list]

        cache_reads = len(addr_list)
        self.results(cache_reads)
    
    def results(self,cache_reads):
        hit_ratio = self.hits/cache_reads
        miss_ratio = 1 - hit_ratio

        print(f"cache size: {self.num_blocks*self.block_size} bytes")
        print(f"Reads: {cache_reads}")
        print(f"Hits: {self.hits}")
        print(f"Misses: {self.misses}")
        print(f"Hit rate: {(hit_ratio*100):.2f}%")
        print(f"Miss rate: {(miss_ratio*100):.2f}%")

        print(self.cache.cache)

class set_mapped():
    def __init__(self,block_size =1, num_blocks =16,associativity=2, LRU = None):
        self.size = num_blocks*block_size
        self.num_lines = int(self.size/int(associativity*block_size))
        self.offset = int(num_blocks/block_size)
        self.index = int(log(self.num_lines,2)) if not (associativity == num_blocks) else 0
        self.valid_bits = 1
        self.associativity = associativity
        self.replacement_policy = 'LRU' if self.associativity <= 4 or LRU == 1 else 'random'
        self.LRU_max = associativity + 1
        self.block_size = block_size
        self.num_blocks = num_blocks
        self.hits = 0
        self.misses = 0
        #address bits always 32
        addr_size = 32
        self.tag = addr_size - self.index - self.offset
        self.cache = cache(self.num_blocks,self.associativity,self.index,
                           self.tag,self.offset,self.block_size,replacement_policy =self.replacement_policy)
        
    def _block_addr(self,address) -> int:
        return int(address/self.block_size)
    
    def _index(self,block_addr) -> int:
        return block_addr%self.num_lines  
    
    def _check_valid_bit(self,idx)-> bool:
        vb_arr = self.cache.cache.at[idx, 'valid']
        idx_arr = np.where(np.array(vb_arr) == 1)[0]
        #if at least one row in the set is valid
        if len(idx_arr) > 0:
            return True,idx_arr
        else:
            self.misses += 1
            return False,idx_arr

    def _find_tag(self,address)->str:
        return bin(int(address/(self.num_lines*self.block_size)))[2:].zfill(self.tag)

    def _lru_inc(self,idx):
        lru_arr = self.cache.cache.at[idx,'lru']
        for id,_ in enumerate(lru_arr):
            inc = lru_arr[id]+1
            self.cache.cache.at[idx,'lru'][id] = inc if inc <= self.LRU_max else lru_arr[id]

    def lru(self,tag,idx,addr)->int:
        expired_idx = randint(0,self.associativity-1) if len(set(self.cache.cache.at[idx,'lru'])) == 1 else self.cache.cache.at[idx,'lru'].index(max(self.cache.cache.at[idx,'lru']))
        
        self.cache.cache.at[idx,'tag'][expired_idx] = tag
        self.cache.cache.at[idx,'lru'][expired_idx] = 0
        self._lru_inc(idx)
       
        self.cache.cache.at[idx,'data'][expired_idx] = addr

        return expired_idx

    #return the location in the block to replace
    def random(self,tag,idx,addr)->int:
        loc = randint(0,self.associativity-1)
        self.cache.cache.at[idx,'tag'][loc] = tag
        self.cache.cache.at[idx,'data'][loc] = addr
        return loc

    def replace(self,tag,idx,addr):

        new_vb_loc = 0
        if self.replacement_policy == 'LRU':
            new_vb_loc=self.lru(tag,idx,addr)
        else:
            new_vb_loc=self.random(tag,idx,addr)

        self.cache.cache.at[idx,'valid'][new_vb_loc] = 1

    def _check_match(self,valid_hits,tag_matches):
        var = False
        x=[]
        if len(tag_matches) > 0:
            x=[i for i in valid_hits if i in tag_matches]
            if len(x) > 0:
                var = True

        return var,x 
    
    def _check_tag(self,idx,tg,valid_locs,addr) -> bool:
        actual_tags = self.cache.cache.at[idx,'tag']        
        tag2 = tg
        idxs = np.where(np.array(actual_tags)==tag2)[0]
        var,loc_hit = self._check_match(valid_locs,idxs)
    
        if var:
            self.hits += 1
            if self.replacement_policy == 'LRU':
                self._lru_inc(idx)
            return True
        else:
            self.misses += 1
            #replacement policy here
            self.replace(tag2,idx,addr)

            return False
    
    def set_read(self,address):
        block_addr = self._block_addr(address)
        index = int(self._index(block_addr))
        tag = (self._find_tag(address))
        vb,idx_arr = self._check_valid_bit(index)

        if vb:
            self._check_tag(index,tag,idx_arr,address)
        else:
            #tag,idx,addr
            self.replace(tag,index,address)
    
    def read_all(self,addr_list):
        
        for addr in addr_list:
            self.set_read(int(addr,base=16))

        cache_reads = len(addr_list)
        self.results(cache_reads)

    def results(self,cache_reads):
        hit_ratio = self.hits/cache_reads
        miss_ratio = 1 - hit_ratio

        print(f"cache size: {self.num_blocks*self.block_size} bytes")
        print(f"Reads: {cache_reads}")
        print(f"Hits: {self.hits}")
        print(f"Misses: {self.misses}")
        print(f"Hit rate: {(hit_ratio*100):.2f}%")
        print(f"Miss rate: {(miss_ratio*100):.2f}%")

        print(self.cache.cache)

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
    block_size = int(args.block_size)
    num_block = int(args.num_blocks)
    associativity = int(args.associativity)
    hit_time = args.hit_time
    miss_time = args.miss_time
    lru = 0
    try: 
        lru = int(args.lru)
    except(TypeError):
        pass

    address_data = read_addr_file(args.input_file)

    if associativity == 1:
        dm = direct_mapped(block_size=block_size,num_blocks=num_block)
        dm.read_all(address_data)
    else:
        sm = set_mapped(block_size=block_size,num_blocks=num_block,associativity=associativity,LRU = lru)
        sm.read_all(address_data)

if __name__ == "__main__":
    main(sys.argv[1:])
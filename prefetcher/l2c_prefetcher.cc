#include "cache.h"
#include "temp.h"


long long int l2_access = 0;

void CACHE::l2c_prefetcher_initialize() 
{


  cout<<"--------- This is L2C prefetcher --------------"<<endl;

}

uint32_t CACHE::l2c_prefetcher_operate(uint64_t addr, uint64_t ip, uint8_t cache_hit, uint8_t type, uint32_t metadata_in, uint8_t critical_ip_flag)
{

  l2_access++;

  return metadata_in;
}

uint32_t CACHE::l2c_prefetcher_cache_fill(uint64_t addr, uint32_t set, uint32_t way, uint8_t prefetch, uint64_t evicted_addr, uint32_t metadata_in)
{
  return metadata_in;
}

void CACHE::l2c_prefetcher_final_stats()
{

}

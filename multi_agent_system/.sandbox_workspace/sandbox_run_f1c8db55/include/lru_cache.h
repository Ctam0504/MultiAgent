#ifndef LRU_CACHE_H
#define LRU_CACHE_H

#include <stddef.h>
#include <stdbool.h>

typedef struct Node Node;
typedef struct LRUCache LRUCache;

LRUCache* lru_cache_create(size_t capacity, void (*free_fn)(void*));
void lru_cache_put(LRUCache* cache, const char* key, void* value);
void* lru_cache_get(LRUCache* cache, const char* key);
void lru_cache_destroy(LRUCache* cache);

#endif // LRU_CACHE_H
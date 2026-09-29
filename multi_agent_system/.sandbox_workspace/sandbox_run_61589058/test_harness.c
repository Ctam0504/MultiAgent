#include "include/lru_cache.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

void test_memory_leak_free() {
    struct LRUCache* cache = lru_cache_create(2, free);
    lru_cache_put(cache, "key1", malloc(10));
    lru_cache_put(cache, "key2", malloc(20));
    lru_cache_destroy(cache);
}

void test_eviction_order() {
    struct LRUCache* cache = lru_cache_create(2, free);
    lru_cache_put(cache, "key1", malloc(10));
    lru_cache_put(cache, "key2", malloc(20));
    lru_cache_put(cache, "key3", malloc(30));
    assert(lru_cache_get(cache, "key1") == NULL);
    lru_cache_destroy(cache);
}

void test_cache_hit_miss() {
    struct LRUCache* cache = lru_cache_create(2, free);
    lru_cache_put(cache, "key1", malloc(10));
    assert(lru_cache_get(cache, "key1") != NULL);
    assert(lru_cache_get(cache, "key2") == NULL);
    lru_cache_destroy(cache);
}

int main() {
    test_memory_leak_free();
    test_eviction_order();
    test_cache_hit_miss();
    printf("[PASS] All tests passed.\n");
    return 0;
}
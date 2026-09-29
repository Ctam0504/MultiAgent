#include "include/lru_cache.h"
#include "src/doubly_linked_list.h"
#include "src/hash_map.h"
#include <stdlib.h>
#include <string.h>

struct LRUCache {
    struct HashMap* map;
    struct DoublyLinkedList* list;
    size_t capacity;
    void (*free_fn)(void*);
};

struct LRUCache* lru_cache_create(size_t capacity, void (*free_fn)(void*)) {
    struct LRUCache* cache = (struct LRUCache*)malloc(sizeof(struct LRUCache));
    cache->map = hash_map_create(capacity);
    cache->list = doubly_linked_list_create();
    cache->capacity = capacity;
    cache->free_fn = free_fn;
    return cache;
}

void lru_cache_put(struct LRUCache* cache, const char* key, void* value) {
    struct Node* node = hash_map_get(cache->map, key);
    if (node) {
        node->data = value;
        doubly_linked_list_remove(cache->list, node);
        doubly_linked_list_insert(cache->list, node);
    } else {
        if (cache->list->size == cache->capacity) {
            struct Node* tail = doubly_linked_list_remove(cache->list);
            hash_map_put(cache->map, (const char*)tail->data, NULL);
            cache->free_fn(tail->data);
            free(tail);
        }
        node = (struct Node*)malloc(sizeof(struct Node));
        node->data = value;
        hash_map_put(cache->map, key, node);
        doubly_linked_list_insert(cache->list, node);
    }
}

void* lru_cache_get(struct LRUCache* cache, const char* key) {
    struct Node* node = hash_map_get(cache->map, key);
    if (node) {
        doubly_linked_list_remove(cache->list, node);
        doubly_linked_list_insert(cache->list, node);
        return node->data;
    }
    return NULL;
}

void lru_cache_destroy(struct LRUCache* cache) {
    while (cache->list->size > 0) {
        struct Node* node = doubly_linked_list_remove(cache->list);
        hash_map_put(cache->map, (const char*)node->data, NULL);
        cache->free_fn(node->data);
        free(node);
    }
    hash_map_destroy(cache->map);
    doubly_linked_list_destroy(cache->list);
    free(cache);
}
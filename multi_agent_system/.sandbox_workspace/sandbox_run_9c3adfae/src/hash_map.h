#ifndef HASH_MAP_H
#define HASH_MAP_H

#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

struct Node;

struct HashMap {
    struct Node** buckets;
    int capacity;
    int size;
};

struct HashMap* hash_map_create(int capacity);
void hash_map_destroy(struct HashMap* map);
struct Node* hash_map_get(struct HashMap* map, const char* key);
void hash_map_put(struct HashMap* map, const char* key, struct Node* node);

#endif // HASH_MAP_H
graph [
  directed 1
  node [
    id 0
    label "file:main.c"
    type "file"
    path "main.c"
    lang "c"
  ]
  node [
    id 1
    label "import:include/lru_cache.h"
    type "import"
    name "include/lru_cache.h"
  ]
  node [
    id 2
    label "import:stdlib.h"
    type "import"
    name "stdlib.h"
  ]
  node [
    id 3
    label "import:string.h"
    type "import"
    name "string.h"
  ]
  node [
    id 4
    label "import:assert.h"
    type "import"
    name "assert.h"
  ]
  node [
    id 5
    label "func:main.c:test_memory_leak_free:6"
    type "function"
    name "test_memory_leak_free"
    file "main.c"
    lang "c"
    args "()"
    code "void test_memory_leak_free() {&#13;&#10;    struct LRUCache* cache = lru_cache_create(2, free);&#13;&#10;    lru_cache_put(cache, &#34;key1&#34;, malloc(10));&#13;&#10;    lru_cache_put(cache, &#34;key2&#34;, malloc(20));&#13;&#10;    lru_cache_destroy(cache);&#13;&#10;}"
  ]
  node [
    id 6
    label "call_ref:lru_cache_destroy"
  ]
  node [
    id 7
    label "call_ref:lru_cache_put"
  ]
  node [
    id 8
    label "call_ref:malloc"
  ]
  node [
    id 9
    label "call_ref:lru_cache_create"
  ]
  node [
    id 10
    label "func:main.c:test_eviction_order:13"
    type "function"
    name "test_eviction_order"
    file "main.c"
    lang "c"
    args "()"
    code "void test_eviction_order() {&#13;&#10;    struct LRUCache* cache = lru_cache_create(2, free);&#13;&#10;    lru_cache_put(cache, &#34;key1&#34;, malloc(10));&#13;&#10;    lru_cache_put(cache, &#34;key2&#34;, malloc(20));&#13;&#10;    lru_cache_put(cache, &#34;key3&#34;, malloc(30));&#13;&#10;    assert(lru_cache_get(cache, &#34;key1&#34;) == NULL);&#13;&#10;    lru_cache_destroy(cache);&#13;&#10;}"
  ]
  node [
    id 11
    label "call_ref:assert"
  ]
  node [
    id 12
    label "call_ref:lru_cache_get"
  ]
  node [
    id 13
    label "func:main.c:test_cache_hit_miss:22"
    type "function"
    name "test_cache_hit_miss"
    file "main.c"
    lang "c"
    args "()"
    code "void test_cache_hit_miss() {&#13;&#10;    struct LRUCache* cache = lru_cache_create(2, free);&#13;&#10;    lru_cache_put(cache, &#34;key1&#34;, malloc(10));&#13;&#10;    assert(lru_cache_get(cache, &#34;key1&#34;) != NULL);&#13;&#10;    assert(lru_cache_get(cache, &#34;key2&#34;) == NULL);&#13;&#10;    lru_cache_destroy(cache);&#13;&#10;}"
  ]
  node [
    id 14
    label "func:main.c:main:30"
    type "function"
    name "main"
    file "main.c"
    lang "c"
    args "()"
    code "int main() {&#13;&#10;    test_memory_leak_free();&#13;&#10;    test_eviction_order();&#13;&#10;    test_cache_hit_miss();&#13;&#10;    return 0;&#13;&#10;}"
  ]
  node [
    id 15
    label "call_ref:test_cache_hit_miss"
  ]
  node [
    id 16
    label "call_ref:test_eviction_order"
  ]
  node [
    id 17
    label "call_ref:test_memory_leak_free"
  ]
  node [
    id 18
    label "file:src\doubly_linked_list.c"
    type "file"
    path "src\doubly_linked_list.c"
    lang "c"
  ]
  node [
    id 19
    label "import:doubly_linked_list.h"
    type "import"
    name "doubly_linked_list.h"
  ]
  node [
    id 20
    label "func:src\doubly_linked_list.c:node_create:4"
    type "function"
    name "node_create"
    file "src\doubly_linked_list.c"
    lang "c"
    args "()"
    code "struct Node* node_create(void* value) {&#13;&#10;    struct Node* node = (struct Node*)malloc(sizeof(struct Node));&#13;&#10;    node->value = value;&#13;&#10;    node->prev = NULL;&#13;&#10;    node->next = NULL;&#13;&#10;    return node;&#13;&#10;}"
  ]
  node [
    id 21
    label "func:src\doubly_linked_list.c:node_destroy:12"
    type "function"
    name "node_destroy"
    file "src\doubly_linked_list.c"
    lang "c"
    args "()"
    code "void node_destroy(struct Node* node) {&#13;&#10;    free(node);&#13;&#10;}"
  ]
  node [
    id 22
    label "call_ref:free"
  ]
  node [
    id 23
    label "file:src\hash_map.c"
    type "file"
    path "src\hash_map.c"
    lang "c"
  ]
  node [
    id 24
    label "import:hash_map.h"
    type "import"
    name "hash_map.h"
  ]
  node [
    id 25
    label "func:src\hash_map.c:hash:3"
    type "function"
    name "hash"
    file "src\hash_map.c"
    lang "c"
    args "()"
    code "size_t hash(const char* key, size_t capacity) {&#13;&#10;    size_t hash_value = 0;&#13;&#10;    while (*key) {&#13;&#10;        hash_value = (hash_value * 31) + *key++;&#13;&#10;    }&#13;&#10;    return hash_value % capacity;&#13;&#10;}"
  ]
  node [
    id 26
    label "func:src\hash_map.c:evict_lru:11"
    type "function"
    name "evict_lru"
    file "src\hash_map.c"
    lang "c"
    args "()"
    code "void evict_lru(struct HashMap* map) {&#13;&#10;    // Implement LRU eviction logic here&#13;&#10;    // This is a placeholder function&#13;&#10;}"
  ]
  node [
    id 27
    label "file:src\lru_cache.c"
    type "file"
    path "src\lru_cache.c"
    lang "c"
  ]
  node [
    id 28
    label "import:src/doubly_linked_list.h"
    type "import"
    name "src/doubly_linked_list.h"
  ]
  node [
    id 29
    label "import:src/hash_map.h"
    type "import"
    name "src/hash_map.h"
  ]
  node [
    id 30
    label "struct:src\lru_cache.c:LRUCache"
    type "struct"
    name "LRUCache"
    file "src\lru_cache.c"
    lang "c"
    bases ""
  ]
  node [
    id 31
    label "struct:src\lru_cache.c:HashMap"
    type "struct"
    name "HashMap"
    file "src\lru_cache.c"
    lang "c"
    bases ""
  ]
  node [
    id 32
    label "struct:src\lru_cache.c:DoublyLinkedList"
    type "struct"
    name "DoublyLinkedList"
    file "src\lru_cache.c"
    lang "c"
    bases ""
  ]
  node [
    id 33
    label "func:src\lru_cache.c:lru_cache_create:12"
    type "function"
    name "lru_cache_create"
    file "src\lru_cache.c"
    lang "c"
    args "()"
    code "struct LRUCache* lru_cache_create(size_t capacity, void (*free_fn)(void*)) {&#13;&#10;    struct LRUCache* cache = (struct LRUCache*)malloc(sizeof(struct LRUCache));&#13;&#10;    cache->map = hash_map_create(capacity, free_fn);&#13;&#10;    cache->list = doubly_linked_list_create();&#13;&#10;    cache->capacity = capacity;&#13;&#10;    cache->free_fn = free_fn;&#13;&#10;    return cache;&#13;&#10;}"
  ]
  node [
    id 34
    label "call_ref:doubly_linked_list_create"
  ]
  node [
    id 35
    label "call_ref:hash_map_create"
  ]
  node [
    id 36
    label "func:src\lru_cache.c:lru_cache_put:21"
    type "function"
    name "lru_cache_put"
    file "src\lru_cache.c"
    lang "c"
    args "()"
    code "void lru_cache_put(struct LRUCache* cache, const char* key, void* value) {&#13;&#10;    struct Node* node = hash_map_get(cache->map, key);&#13;&#10;    if (node) {&#13;&#10;        doubly_linked_list_remove(cache->list, node);&#13;&#10;    } else {&#13;&#10;        if (cache->list->size == cache->capacity) {&#13;&#10;            struct Node* lru_node = cache->list->head;&#13;&#10;            hash_map_put(cache->map, lru_node->key, NULL);&#13;&#10;            doubly_linked_list_remove(cache->list, lru_node);&#13;&#10;            cache->free_fn(lru_node->value);&#13;&#10;            free(lru_node);&#13;&#10;        }&#13;&#10;        node = (struct Node*)malloc(sizeof(struct Node));&#13;&#10;        node->key = strdup(key);&#13;&#10;    }&#13;&#10;    node->value = value;&#13;&#10;    hash_map_put(cache->map, key, node);&#13;&#10;    doubly_linked_list_insert(cache->list, node);&#13;&#10;}"
  ]
  node [
    id 37
    label "call_ref:doubly_linked_list_insert"
  ]
  node [
    id 38
    label "call_ref:hash_map_put"
  ]
  node [
    id 39
    label "call_ref:strdup"
  ]
  node [
    id 40
    label "call_ref:free_fn"
  ]
  node [
    id 41
    label "call_ref:doubly_linked_list_remove"
  ]
  node [
    id 42
    label "call_ref:hash_map_get"
  ]
  node [
    id 43
    label "func:src\lru_cache.c:lru_cache_get:41"
    type "function"
    name "lru_cache_get"
    file "src\lru_cache.c"
    lang "c"
    args "()"
    code "void* lru_cache_get(struct LRUCache* cache, const char* key) {&#13;&#10;    struct Node* node = hash_map_get(cache->map, key);&#13;&#10;    if (node) {&#13;&#10;        doubly_linked_list_remove(cache->list, node);&#13;&#10;        doubly_linked_list_insert(cache->list, node);&#13;&#10;        return node->value;&#13;&#10;    }&#13;&#10;    return NULL;&#13;&#10;}"
  ]
  node [
    id 44
    label "func:src\lru_cache.c:lru_cache_destroy:51"
    type "function"
    name "lru_cache_destroy"
    file "src\lru_cache.c"
    lang "c"
    args "()"
    code "void lru_cache_destroy(struct LRUCache* cache) {&#13;&#10;    hash_map_destroy(cache->map);&#13;&#10;    doubly_linked_list_destroy(cache->list);&#13;&#10;    free(cache);&#13;&#10;}"
  ]
  node [
    id 45
    label "call_ref:doubly_linked_list_destroy"
  ]
  node [
    id 46
    label "call_ref:hash_map_destroy"
  ]
  node [
    id 47
    label "file:include\lru_cache.h"
    type "file"
    path "include\lru_cache.h"
    lang "c"
  ]
  node [
    id 48
    label "import:stddef.h"
    type "import"
    name "stddef.h"
  ]
  node [
    id 49
    label "struct:include\lru_cache.h:LRUCache"
    type "struct"
    name "LRUCache"
    file "include\lru_cache.h"
    lang "c"
    bases ""
  ]
  node [
    id 50
    label "file:src\doubly_linked_list.h"
    type "file"
    path "src\doubly_linked_list.h"
    lang "c"
  ]
  node [
    id 51
    label "struct:src\doubly_linked_list.h:Node"
    type "struct"
    name "Node"
    file "src\doubly_linked_list.h"
    lang "c"
    bases ""
  ]
  node [
    id 52
    label "struct:src\doubly_linked_list.h:DoublyLinkedList"
    type "struct"
    name "DoublyLinkedList"
    file "src\doubly_linked_list.h"
    lang "c"
    bases ""
  ]
  node [
    id 53
    label "func:src\doubly_linked_list.h:doubly_linked_list_create:18"
    type "function"
    name "doubly_linked_list_create"
    file "src\doubly_linked_list.h"
    lang "c"
    args "()"
    code "struct DoublyLinkedList* doubly_linked_list_create() {&#13;&#10;    struct DoublyLinkedList* list = (struct DoublyLinkedList*)malloc(sizeof(struct DoublyLinkedList));&#13;&#10;    list->head = NULL;&#13;&#10;    list->tail = NULL;&#13;&#10;    list->size = 0;&#13;&#10;    return list;&#13;&#10;}"
  ]
  node [
    id 54
    label "func:src\doubly_linked_list.h:doubly_linked_list_destroy:26"
    type "function"
    name "doubly_linked_list_destroy"
    file "src\doubly_linked_list.h"
    lang "c"
    args "()"
    code "void doubly_linked_list_destroy(struct DoublyLinkedList* list) {&#13;&#10;    struct Node* current = list->head;&#13;&#10;    while (current != NULL) {&#13;&#10;        struct Node* next = current->next;&#13;&#10;        free(current);&#13;&#10;        current = next;&#13;&#10;    }&#13;&#10;    free(list);&#13;&#10;}"
  ]
  node [
    id 55
    label "func:src\doubly_linked_list.h:doubly_linked_list_insert:36"
    type "function"
    name "doubly_linked_list_insert"
    file "src\doubly_linked_list.h"
    lang "c"
    args "()"
    code "void doubly_linked_list_insert(struct DoublyLinkedList* list, struct Node* node) {&#13;&#10;    if (list->head == NULL) {&#13;&#10;        list->head = node;&#13;&#10;        list->tail = node;&#13;&#10;    } else {&#13;&#10;        list->tail->next = node;&#13;&#10;        node->prev = list->tail;&#13;&#10;        list->tail = node;&#13;&#10;    }&#13;&#10;    list->size++;&#13;&#10;}"
  ]
  node [
    id 56
    label "func:src\doubly_linked_list.h:doubly_linked_list_remove:48"
    type "function"
    name "doubly_linked_list_remove"
    file "src\doubly_linked_list.h"
    lang "c"
    args "()"
    code "void doubly_linked_list_remove(struct DoublyLinkedList* list, struct Node* node) {&#13;&#10;    if (node->prev != NULL) {&#13;&#10;        node->prev->next = node->next;&#13;&#10;    } else {&#13;&#10;        list->head = node->next;&#13;&#10;    }&#13;&#10;    if (node->next != NULL) {&#13;&#10;        node->next->prev = node->prev;&#13;&#10;    } else {&#13;&#10;        list->tail = node->prev;&#13;&#10;    }&#13;&#10;    free(node);&#13;&#10;    list->size--;&#13;&#10;}"
  ]
  node [
    id 57
    label "file:src\hash_map.h"
    type "file"
    path "src\hash_map.h"
    lang "c"
  ]
  node [
    id 58
    label "struct:src\hash_map.h:Node"
    type "struct"
    name "Node"
    file "src\hash_map.h"
    lang "c"
    bases ""
  ]
  node [
    id 59
    label "struct:src\hash_map.h:HashMap"
    type "struct"
    name "HashMap"
    file "src\hash_map.h"
    lang "c"
    bases ""
  ]
  node [
    id 60
    label "func:src\hash_map.h:hash_map_create:17"
    type "function"
    name "hash_map_create"
    file "src\hash_map.h"
    lang "c"
    args "()"
    code "struct HashMap* hash_map_create(size_t capacity, void (*free_fn)(void*)) {&#13;&#10;    struct HashMap* map = (struct HashMap*)malloc(sizeof(struct HashMap));&#13;&#10;    map->capacity = capacity;&#13;&#10;    map->size = 0;&#13;&#10;    map->buckets = (struct Node**)calloc(capacity, sizeof(struct Node*));&#13;&#10;    map->free_fn = free_fn;&#13;&#10;    return map;&#13;&#10;}"
  ]
  node [
    id 61
    label "call_ref:calloc"
  ]
  node [
    id 62
    label "func:src\hash_map.h:hash_map_destroy:26"
    type "function"
    name "hash_map_destroy"
    file "src\hash_map.h"
    lang "c"
    args "()"
    code "void hash_map_destroy(struct HashMap* map) {&#13;&#10;    for (size_t i = 0; i < map->capacity; i++) {&#13;&#10;        struct Node* node = map->buckets[i];&#13;&#10;        while (node) {&#13;&#10;            struct Node* next = node->next;&#13;&#10;            map->free_fn(node->value);&#13;&#10;            free(node);&#13;&#10;            node = next;&#13;&#10;        }&#13;&#10;    }&#13;&#10;    free(map->buckets);&#13;&#10;    free(map);&#13;&#10;}"
  ]
  node [
    id 63
    label "func:src\hash_map.h:hash_map_get:40"
    type "function"
    name "hash_map_get"
    file "src\hash_map.h"
    lang "c"
    args "()"
    code "struct Node* hash_map_get(struct HashMap* map, const char* key) {&#13;&#10;    size_t index = hash(key, map->capacity);&#13;&#10;    struct Node* node = map->buckets[index];&#13;&#10;    while (node) {&#13;&#10;        if (strcmp(node->key, key) == 0) {&#13;&#10;            return node;&#13;&#10;        }&#13;&#10;        node = node->next;&#13;&#10;    }&#13;&#10;    return NULL;&#13;&#10;}"
  ]
  node [
    id 64
    label "call_ref:strcmp"
  ]
  node [
    id 65
    label "call_ref:hash"
  ]
  node [
    id 66
    label "func:src\hash_map.h:hash_map_put:52"
    type "function"
    name "hash_map_put"
    file "src\hash_map.h"
    lang "c"
    args "()"
    code "void hash_map_put(struct HashMap* map, const char* key, struct Node* node) {&#13;&#10;    size_t index = hash(key, map->capacity);&#13;&#10;    node->next = map->buckets[index];&#13;&#10;    map->buckets[index] = node;&#13;&#10;    map->size++;&#13;&#10;    if (map->size > map->capacity) {&#13;&#10;        evict_lru(map);&#13;&#10;    }&#13;&#10;}"
  ]
  node [
    id 67
    label "call_ref:evict_lru"
  ]
  edge [
    source 0
    target 1
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 2
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 3
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 4
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 5
    relation "DEFINES"
  ]
  edge [
    source 0
    target 10
    relation "DEFINES"
  ]
  edge [
    source 0
    target 13
    relation "DEFINES"
  ]
  edge [
    source 0
    target 14
    relation "DEFINES"
  ]
  edge [
    source 5
    target 6
    relation "CALLS"
  ]
  edge [
    source 5
    target 7
    relation "CALLS"
  ]
  edge [
    source 5
    target 8
    relation "CALLS"
  ]
  edge [
    source 5
    target 9
    relation "CALLS"
  ]
  edge [
    source 10
    target 6
    relation "CALLS"
  ]
  edge [
    source 10
    target 11
    relation "CALLS"
  ]
  edge [
    source 10
    target 12
    relation "CALLS"
  ]
  edge [
    source 10
    target 7
    relation "CALLS"
  ]
  edge [
    source 10
    target 8
    relation "CALLS"
  ]
  edge [
    source 10
    target 9
    relation "CALLS"
  ]
  edge [
    source 13
    target 6
    relation "CALLS"
  ]
  edge [
    source 13
    target 11
    relation "CALLS"
  ]
  edge [
    source 13
    target 12
    relation "CALLS"
  ]
  edge [
    source 13
    target 7
    relation "CALLS"
  ]
  edge [
    source 13
    target 8
    relation "CALLS"
  ]
  edge [
    source 13
    target 9
    relation "CALLS"
  ]
  edge [
    source 14
    target 15
    relation "CALLS"
  ]
  edge [
    source 14
    target 16
    relation "CALLS"
  ]
  edge [
    source 14
    target 17
    relation "CALLS"
  ]
  edge [
    source 18
    target 19
    relation "IMPORTS"
  ]
  edge [
    source 18
    target 2
    relation "IMPORTS"
  ]
  edge [
    source 18
    target 20
    relation "DEFINES"
  ]
  edge [
    source 18
    target 21
    relation "DEFINES"
  ]
  edge [
    source 20
    target 8
    relation "CALLS"
  ]
  edge [
    source 21
    target 22
    relation "CALLS"
  ]
  edge [
    source 23
    target 24
    relation "IMPORTS"
  ]
  edge [
    source 23
    target 25
    relation "DEFINES"
  ]
  edge [
    source 23
    target 26
    relation "DEFINES"
  ]
  edge [
    source 27
    target 1
    relation "IMPORTS"
  ]
  edge [
    source 27
    target 28
    relation "IMPORTS"
  ]
  edge [
    source 27
    target 29
    relation "IMPORTS"
  ]
  edge [
    source 27
    target 30
    relation "DEFINES"
  ]
  edge [
    source 27
    target 31
    relation "DEFINES"
  ]
  edge [
    source 27
    target 32
    relation "DEFINES"
  ]
  edge [
    source 27
    target 33
    relation "DEFINES"
  ]
  edge [
    source 27
    target 36
    relation "DEFINES"
  ]
  edge [
    source 27
    target 43
    relation "DEFINES"
  ]
  edge [
    source 27
    target 44
    relation "DEFINES"
  ]
  edge [
    source 33
    target 34
    relation "CALLS"
  ]
  edge [
    source 33
    target 35
    relation "CALLS"
  ]
  edge [
    source 33
    target 8
    relation "CALLS"
  ]
  edge [
    source 36
    target 37
    relation "CALLS"
  ]
  edge [
    source 36
    target 38
    relation "CALLS"
  ]
  edge [
    source 36
    target 39
    relation "CALLS"
  ]
  edge [
    source 36
    target 8
    relation "CALLS"
  ]
  edge [
    source 36
    target 22
    relation "CALLS"
  ]
  edge [
    source 36
    target 40
    relation "CALLS"
  ]
  edge [
    source 36
    target 41
    relation "CALLS"
  ]
  edge [
    source 36
    target 42
    relation "CALLS"
  ]
  edge [
    source 43
    target 37
    relation "CALLS"
  ]
  edge [
    source 43
    target 41
    relation "CALLS"
  ]
  edge [
    source 43
    target 42
    relation "CALLS"
  ]
  edge [
    source 44
    target 22
    relation "CALLS"
  ]
  edge [
    source 44
    target 45
    relation "CALLS"
  ]
  edge [
    source 44
    target 46
    relation "CALLS"
  ]
  edge [
    source 47
    target 48
    relation "IMPORTS"
  ]
  edge [
    source 47
    target 49
    relation "DEFINES"
  ]
  edge [
    source 50
    target 48
    relation "IMPORTS"
  ]
  edge [
    source 50
    target 51
    relation "DEFINES"
  ]
  edge [
    source 50
    target 52
    relation "DEFINES"
  ]
  edge [
    source 50
    target 53
    relation "DEFINES"
  ]
  edge [
    source 50
    target 54
    relation "DEFINES"
  ]
  edge [
    source 50
    target 55
    relation "DEFINES"
  ]
  edge [
    source 50
    target 56
    relation "DEFINES"
  ]
  edge [
    source 53
    target 8
    relation "CALLS"
  ]
  edge [
    source 54
    target 22
    relation "CALLS"
  ]
  edge [
    source 56
    target 22
    relation "CALLS"
  ]
  edge [
    source 57
    target 48
    relation "IMPORTS"
  ]
  edge [
    source 57
    target 3
    relation "IMPORTS"
  ]
  edge [
    source 57
    target 1
    relation "IMPORTS"
  ]
  edge [
    source 57
    target 58
    relation "DEFINES"
  ]
  edge [
    source 57
    target 59
    relation "DEFINES"
  ]
  edge [
    source 57
    target 60
    relation "DEFINES"
  ]
  edge [
    source 57
    target 62
    relation "DEFINES"
  ]
  edge [
    source 57
    target 63
    relation "DEFINES"
  ]
  edge [
    source 57
    target 66
    relation "DEFINES"
  ]
  edge [
    source 60
    target 61
    relation "CALLS"
  ]
  edge [
    source 60
    target 8
    relation "CALLS"
  ]
  edge [
    source 62
    target 22
    relation "CALLS"
  ]
  edge [
    source 62
    target 40
    relation "CALLS"
  ]
  edge [
    source 63
    target 64
    relation "CALLS"
  ]
  edge [
    source 63
    target 65
    relation "CALLS"
  ]
  edge [
    source 66
    target 67
    relation "CALLS"
  ]
  edge [
    source 66
    target 65
    relation "CALLS"
  ]
]

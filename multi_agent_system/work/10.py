import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"[Created] {path}")

# ==========================================
# 1. JAVA PROJECT (10 Files)
# ==========================================
java_files = {
    "java_project/src/model/Product.java": """
    package model;
    public class Product {
        private String id;
        private String name;
        private double price;
        public Product(String id, String name, double price) {
            this.id = id; this.name = name; this.price = price;
        }
        public String getId() { return id; }
        public String getName() { return name; }
        public double getPrice() { return price; }
    }
    """,
    "java_project/src/model/OrderItem.java": """
    package model;
    public class OrderItem {
        private Product product;
        private int quantity;
        public OrderItem(Product product, int quantity) {
            this.product = product; this.quantity = quantity;
        }
        public Product getProduct() { return product; }
        public int getQuantity() { return quantity; }
        public double getSubTotal() { return product.getPrice() * quantity; }
    }
    """,
    "java_project/src/model/Order.java": """
    package model;
    import java.util.List;
    public class Order {
        private String orderId;
        private List<OrderItem> items;
        private double totalAmount;
        public Order(String orderId, List<OrderItem> items) {
            this.orderId = orderId;
            this.items = items;
            this.totalAmount = items.stream().mapToDouble(OrderItem::getSubTotal).sum();
        }
        public String getOrderId() { return orderId; }
        public List<OrderItem> getItems() { return items; }
        public double getTotalAmount() { return totalAmount; }
    }
    """,
    "java_project/src/model/User.java": """
    package model;
    public class User {
        private String userId;
        private String email;
        public User(String userId, String email) {
            this.userId = userId; this.email = email;
        }
        public String getUserId() { return userId; }
        public String getEmail() { return email; }
    }
    """,
    "java_project/src/repository/ProductRepository.java": """
    package repository;
    import model.Product;
    import java.util.HashMap;
    import java.util.Map;
    public class ProductRepository {
        private final Map<String, Product> db = new HashMap<>();
        public void save(Product p) { db.put(p.getId(), p); }
        public Product findById(String id) { return db.get(id); }
    }
    """,
    "java_project/src/repository/OrderRepository.java": """
    package repository;
    import model.Order;
    import java.util.HashMap;
    import java.util.Map;
    public class OrderRepository {
        private final Map<String, Order> db = new HashMap<>();
        public void save(Order o) { db.put(o.getOrderId(), o); }
        public Order findById(String id) { return db.get(id); }
    }
    """,
    "java_project/src/repository/UserRepository.java": """
    package repository;
    import model.User;
    import java.util.HashMap;
    import java.util.Map;
    public class UserRepository {
        private final Map<String, User> db = new HashMap<>();
        public void save(User u) { db.put(u.getUserId(), u); }
        public User findById(String id) { return db.get(id); }
    }
    """,
    "java_project/src/service/PaymentService.java": """
    package service;
    import model.Order;
    public class PaymentService {
        public boolean processPayment(Order order, double amount) {
            System.out.println("Processing payment of $" + amount + " for order " + order.getOrderId());
            return true;
        }
    }
    """,
    "java_project/src/service/OrderService.java": """
    package service;
    import model.Order;
    import repository.OrderRepository;
    public class OrderService {
        private final OrderRepository orderRepository;
        private final PaymentService paymentService;
        public OrderService(OrderRepository orderRepository, PaymentService paymentService) {
            this.orderRepository = orderRepository;
            this.paymentService = paymentService;
        }
        public void checkout(Order order) {
            orderRepository.save(order);
            paymentService.processPayment(order, order.getTotalAmount());
        }
    }
    """,
    "java_project/src/Main.java": """
    import model.*;
    import repository.*;
    import service.*;
    import java.util.List;
    public class Main {
        public static void main(String[] args) {
            System.out.println("E-Commerce Engine Initialized.");
        }
    }
    """
}

# ==========================================
# 2. C PROJECT (10 Files)
# ==========================================
c_files = {
    "c_project/include/fs_types.h": """
    #ifndef FS_TYPES_H
    #define FS_TYPES_H
    #include <stddef.h>
    #include <stdint.h>
    typedef uint32_t node_id_t;
    typedef uint32_t block_id_t;
    #endif
    """,
    "c_project/include/block_store.h": """
    #ifndef BLOCK_STORE_H
    #define BLOCK_STORE_H
    #include "fs_types.h"
    void block_store_init(void);
    """,
    "c_project/src/block_store.c": """
    #include "block_store.h"
    #include <stdio.h>
    void block_store_init(void) {
        printf("Block store initialized.\\n");
    }
    """,
    "c_project/include/inode.h": """
    #ifndef INODE_H
    #define INODE_H
    #include "fs_types.h"
    typedef struct {
        node_id_t id;
        size_t size;
    } INode;
    INode* inode_create(node_id_t id, size_t size);
    void inode_free(INode *inode);
    #endif
    """,
    "c_project/src/inode.c": """
    #include "inode.h"
    #include <stdlib.h>
    INode* inode_create(node_id_t id, size_t size) {
        INode *node = (INode*)malloc(sizeof(INode));
        if (!node) return NULL;
        node->id = id;
        node->size = size;
        return node;
    }
    void inode_free(INode *inode) {
        if (inode) free(inode);
    }
    """,
    "c_project/include/directory.h": """
    #ifndef DIRECTORY_H
    #define DIRECTORY_H
    #include "fs_types.h"
    void directory_init(void);
    #endif
    """,
    "c_project/src/directory.c": """
    #include "directory.h"
    #include <stdio.h>
    void directory_init(void) {
        printf("Directory subsystem initialized.\\n");
    }
    """,
    "c_project/include/vfs.h": """
    #ifndef VFS_H
    #define VFS_H
    #include "fs_types.h"
    int vfs_read(node_id_t id, char *buf, size_t len);
    int vfs_write(node_id_t id, const char *buf, size_t len);
    #endif
    """,
    "c_project/src/vfs.c": """
    #include "vfs.h"
    #include "inode.h"
    #include <string.h>
    int vfs_read(node_id_t id, char *buf, size_t len) {
        (void)id; (void)buf; (void)len;
        return 0;
    }
    int vfs_write(node_id_t id, const char *buf, size_t len) {
        (void)id; (void)buf; (void)len;
        return 0;
    }
    """,
    "c_project/src/main.c": """
    #include "block_store.h"
    #include "directory.h"
    #include <stdio.h>
    int main(void) {
        block_store_init();
        directory_init();
        printf("VFS Running successfully.\\n");
        return 0;
    }
    """
}

# ==========================================
# 3. PYTHON PROJECT (11 Files)
# ==========================================
python_files = {
    "python_project/task_engine/__init__.py": "# Task Engine Package",
    "python_project/task_engine/config.py": """
    MAX_RETRIES = 3
    TIMEOUT = 30
    """,
    "python_project/task_engine/exceptions.py": """
    class TaskError(Exception):
        pass
    """,
    "python_project/task_engine/models/__init__.py": "# Models Package",
    "python_project/task_engine/models/task.py": """
    from dataclasses import dataclass
    @dataclass
    class Task:
        task_id: str
        payload: dict
        status: str = "PENDING"
    """,
    "python_project/task_engine/models/result.py": """
    from dataclasses import dataclass
    @dataclass
    class TaskResult:
        task_id: str
        success: bool
        output: any = None
    """,
    "python_project/task_engine/storage/__init__.py": "# Storage Package",
    "python_project/task_engine/storage/memory_store.py": """
    class MemoryStore:
        def __init__(self):
            self.storage = {}
        def save(self, key, value):
            self.storage[key] = value
        def get(self, key):
            return self.storage.get(key)
    """,
    "python_project/task_engine/broker.py": """
    import asyncio
    class TaskBroker:
        def __init__(self):
            self.queue = asyncio.Queue()
        async def enqueue(self, task):
            await self.queue.put(task)
        async def dequeue(self):
            return await self.queue.get()
    """,
    "python_project/task_engine/worker.py": """
    class Worker:
        def __init__(self, broker, store):
            self.broker = broker
            self.store = store
        async def run_task(self, task):
            print(f"Executing task {task.task_id}")
            task.status = "COMPLETED"
            self.store.save(task.task_id, task)
    """,
    "python_project/main.py": """
    import asyncio
    from task_engine.broker import TaskBroker
    from task_engine.worker import Worker
    from task_engine.storage.memory_store import MemoryStore
    from task_engine.models.task import Task

    async def main():
        broker = TaskBroker()
        store = MemoryStore()
        worker = Worker(broker, store)
        task = Task("1", {"data": "test"})
        await broker.enqueue(task)
        t = await broker.dequeue()
        await worker.run_task(t)

    if __name__ == "__main__":
        asyncio.run(main())
    """
}

# Run generation
for path, code in java_files.items():
    create_file(path, code)

for path, code in c_files.items():
    create_file(path, code)

for path, code in python_files.items():
    create_file(path, code)

print("\\n[SUCCESS] All base repositories generated successfully!")
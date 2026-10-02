import os

files = {
    "src/model/TransactionType.java": """package model;

public enum TransactionType {
    PAYMENT,
    REFUND
}
""",
    "src/model/Transaction.java": """package model;

public class Transaction {
    private String id;
    private double amount;
    private TransactionType type;

    public Transaction(String id, double amount, TransactionType type) {
        this.id = id;
        this.amount = amount;
        this.type = type;
    }

    public String getId() { return id; }
    public double getAmount() { return amount; }
    public TransactionType getType() { return type; }
}
""",
    "src/exception/PaymentException.java": """package exception;

public class PaymentException extends Exception {
    public PaymentException(String message) {
        super(message);
    }
}
""",
    "src/service/IPaymentService.java": """package service;

import model.Transaction;
import exception.PaymentException;

public interface IPaymentService {
    Transaction processPayment(String id, double amount) throws PaymentException;
}
""",
    "src/service/PaymentServiceImpl.java": """package service;

import model.Transaction;
import model.TransactionType;
import exception.PaymentException;
import java.util.HashMap;
import java.util.Map;

public class PaymentServiceImpl implements IPaymentService {
    private final Map<String, Transaction> storage = new HashMap<>();

    @Override
    public Transaction processPayment(String id, double amount) throws PaymentException {
        if (amount <= 0) {
            throw new PaymentException("Số tiền thanh toán phải lớn hơn 0");
        }
        Transaction tx = new Transaction(id, amount, TransactionType.PAYMENT);
        storage.put(id, tx);
        return tx;
    }
}
""",
    "src/Main.java": """import service.IPaymentService;
import service.PaymentServiceImpl;
import model.Transaction;
import exception.PaymentException;

public class Main {
    public static void main(String[] args) {
        IPaymentService service = new PaymentServiceImpl();
        try {
            Transaction tx = service.processPayment("TX100", 250.0);
            System.out.println("Thanh toán thành công: " + tx.getId());
        } catch (PaymentException e) {
              System.err.println("Lỗi thanh toán: " + e.getMessage());
        }
    }
}
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("[SUCCESS] Đã khởi tạo thành công 6 files Java Base Repo!")
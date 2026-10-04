import os

files = {
    "src/model/Currency.java": """package model;

public enum Currency {
    USD,
    VND
}
""",
    "src/model/PaymentRequest.java": """package model;

public class PaymentRequest {
    private String requestId;
    private double amount;
    private Currency currency;

    public PaymentRequest(String requestId, double amount, Currency currency) {
        this.requestId = requestId;
        this.amount = amount;
        this.currency = currency;
    }

    public String getRequestId() { return requestId; }
    public double getAmount() { return amount; }
    public Currency getCurrency() { return currency; }
}
""",
    "src/exception/GatewayException.java": """package exception;

public class GatewayException extends Exception {
    public GatewayException(String message) {
        super(message);
    }
}
""",
    "src/strategy/IPaymentStrategy.java": """package strategy;

import model.PaymentRequest;
import exception.GatewayException;

public interface IPaymentStrategy {
    boolean pay(PaymentRequest request) throws GatewayException;
}
""",
    "src/strategy/CreditCardStrategy.java": """package strategy;

import model.PaymentRequest;
import exception.GatewayException;

public class CreditCardStrategy implements IPaymentStrategy {
    @Override
    public boolean pay(PaymentRequest request) throws GatewayException {
        if (request.getAmount() <= 0) {
            throw new GatewayException("CreditCard: Số tiền không hợp lệ");
        }
        System.out.println("Thanh toán CreditCard thành công cho request " + request.getRequestId());
        return true;
    }
}
""",
    "src/strategy/PaypalStrategy.java": """package strategy;

import model.PaymentRequest;
import exception.GatewayException;

public class PaypalStrategy implements IPaymentStrategy {
    @Override
    public boolean pay(PaymentRequest request) throws GatewayException {
        if (request.getAmount() <= 0) {
            throw new GatewayException("Paypal: Số tiền không hợp lệ");
        }
        System.out.println("Thanh toán Paypal thành công cho request " + request.getRequestId());
        return true;
    }
}
""",
    "src/service/PaymentProcessor.java": """package service;

import strategy.IPaymentStrategy;
import model.PaymentRequest;
import exception.GatewayException;

public class PaymentProcessor {
    private IPaymentStrategy strategy;

    public PaymentProcessor(IPaymentStrategy strategy) {
        this.strategy = strategy;
    }

    public void setStrategy(IPaymentStrategy strategy) {
        this.strategy = strategy;
    }

    public boolean execute(PaymentRequest request) throws GatewayException {
        return strategy.pay(request);
    }
}
""",
    "src/Main.java": """import model.*;
import strategy.*;
import service.*;
import exception.GatewayException;

public class Main {
    public static void main(String[] args) {
        PaymentRequest request = new PaymentRequest("REQ_001", 100.0, Currency.USD);
        PaymentProcessor processor = new PaymentProcessor(new CreditCardStrategy());

        try {
            processor.execute(request);
        } catch (GatewayException e) {
            System.err.println("Lỗi: " + e.getMessage());
        }
    }
}
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("[SUCCESS] Đã khởi tạo Nấc 2 (8 Files Strategy Pattern) thành công!")
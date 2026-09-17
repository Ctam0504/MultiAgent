package com.example.service;

public class PaymentProcessor {

    public boolean processPayment(String userId, double amount) {
        if (amount <= 0) {
            return false;
        }
        return verifyAccount(userId);
    }

    private boolean verifyAccount(String userId) {
        return userId != null && !userId.isEmpty();
    }
}
package com.example.service;

import java.util.List;
import java.util.ArrayList;

public class TicketBookingService extends BaseService {

    private PaymentProcessor paymentProcessor;

    public TicketBookingService() {
        this.paymentProcessor = new PaymentProcessor();
    }

    @Override
    public boolean validateRequest(Object request) {
        logActivity("validateRequest");
        return request != null;
    }

    public String bookTicket(String userId, String movieId, double price) {
        logActivity("bookTicket");

        if (!validateRequest(movieId)) {
            return "INVALID_REQUEST";
        }

        boolean isPaid = paymentProcessor.processPayment(userId, price);
        if (isPaid) {
            return generateTicketId(userId, movieId);
        }

        return "PAYMENT_FAILED";
    }

    private String generateTicketId(String userId, String movieId) {
        return "TICKET_" + userId + "_" + movieId;
    }
}
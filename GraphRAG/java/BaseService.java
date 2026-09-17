package com.example.service;

import java.util.logging.Logger;

public abstract class BaseService {
    protected Logger logger = Logger.getLogger(BaseService.class.getName());

    public void logActivity(String action) {
        logger.info("Executing action: " + action);
    }

    public abstract boolean validateRequest(Object request);
}
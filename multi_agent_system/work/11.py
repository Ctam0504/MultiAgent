import os

files = {
    "src/model/User.java": """package model;

public class User {
    private String id;
    private String username;

    public User(String id, String username) {
        this.id = id;
        this.username = username;
    }
    public String getId() { return id; }
    public String getUsername() { return username; }
}
""",
    "src/model/EventType.java": """package model;

public enum EventType {
    USER_CREATED
}
""",
    "src/event/BaseEvent.java": """package event;

import model.EventType;

public abstract class BaseEvent {
    private final String eventId;
    private final EventType type;

    public BaseEvent(String eventId, EventType type) {
        this.eventId = eventId;
        this.type = type;
    }
    public String getEventId() { return eventId; }
    public EventType getType() { return type; }
}
""",
    "src/event/UserCreatedEvent.java": """package event;

import model.User;
import model.EventType;

public class UserCreatedEvent extends BaseEvent {
    private final User user;

    public UserCreatedEvent(String eventId, User user) {
        super(eventId, EventType.USER_CREATED);
        this.user = user;
    }
    public User getUser() { return user; }
}
""",
    "src/exception/SystemException.java": """package exception;

public class SystemException extends Exception {
    public SystemException(String message) {
        super(message);
    }
}
""",
    "src/observer/IObserver.java": """package observer;

import event.BaseEvent;
import exception.SystemException;

public interface IObserver<T extends BaseEvent> {
    void onEvent(T event) throws SystemException;
}
""",
    "src/observer/EmailNotifier.java": """package observer;

import event.UserCreatedEvent;
import exception.SystemException;

public class EmailNotifier implements IObserver<UserCreatedEvent> {
    @Override
    public void onEvent(UserCreatedEvent event) throws SystemException {
        System.out.println("[EMAIL] Gửi email chào mừng đến: " + event.getUser().getUsername());
    }
}
""",
    "src/observer/AuditLogger.java": """package observer;

import event.UserCreatedEvent;
import exception.SystemException;

public class AuditLogger implements IObserver<UserCreatedEvent> {
    @Override
    public void onEvent(UserCreatedEvent event) throws SystemException {
        System.out.println("[AUDIT] Log user creation: " + event.getUser().getId());
    }
}
""",
    "src/engine/EventDispatcher.java": """package engine;

import event.BaseEvent;
import observer.IObserver;
import exception.SystemException;
import java.util.ArrayList;
import java.util.List;

public class EventDispatcher {
    @SuppressWarnings("rawtypes")
    private final List<IObserver> observers = new ArrayList<>();

    public void register(IObserver<?> observer) {
        observers.add(observer);
    }

    @SuppressWarnings("unchecked")
    public void dispatch(BaseEvent event) throws SystemException {
        for (IObserver observer : observers) {
            observer.onEvent(event);
        }
    }
}
""",
    "src/service/UserService.java": """package service;

import model.User;
import event.UserCreatedEvent;
import engine.EventDispatcher;
import exception.SystemException;

public class UserService {
    private final EventDispatcher dispatcher;

    public UserService(EventDispatcher dispatcher) {
        this.dispatcher = dispatcher;
    }

    public User registerUser(String id, String username) throws SystemException {
        User user = new User(id, username);
        UserCreatedEvent event = new UserCreatedEvent("EVT_" + id, user);
        dispatcher.dispatch(event);
        return user;
    }
}
""",
    "src/Main.java": """import service.UserService;
import engine.EventDispatcher;
import observer.EmailNotifier;
import observer.AuditLogger;
import exception.SystemException;

public class Main {
    public static void main(String[] args) {
        EventDispatcher dispatcher = new EventDispatcher();
        dispatcher.register(new EmailNotifier());
        dispatcher.register(new AuditLogger());

        UserService userService = new UserService(dispatcher);
        try {
            userService.registerUser("U001", "dev_user");
        } catch (SystemException e) {
            System.err.println("Lỗi hệ thống: " + e.getMessage());
        }
    }
}
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("[SUCCESS] Đã khởi tạo Nấc 3 (11 Files Event-Driven Framework) thành công!")
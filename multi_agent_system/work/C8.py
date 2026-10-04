import os

files_c = {
    "include/payment_types.h": """#ifndef PAYMENT_TYPES_H
#define PAYMENT_TYPES_H

typedef enum {
    CURRENCY_USD,
    CURRENCY_VND
} Currency;

typedef struct {
    char request_id[32];
    double amount;
    Currency currency;
} PaymentRequest;

#endif
""",
    "include/gateway_exception.h": """#ifndef GATEWAY_EXCEPTION_H
#define GATEWAY_EXCEPTION_H

typedef struct {
    int error_code;
    char message[256];
} GatewayError;

#endif
""",
    "include/payment_strategy.h": """#ifndef PAYMENT_STRATEGY_H
#define PAYMENT_STRATEGY_H

#include "payment_types.h"
#include "gateway_exception.h"

typedef struct PaymentStrategy {
    const char* name;
    int (*pay)(const PaymentRequest* request, GatewayError* error);
} PaymentStrategy;

#endif
""",
    "src/credit_card_strategy.c": """#include <stdio.h>
#include <string.h>
#include "payment_strategy.h"

int credit_card_pay(const PaymentRequest* request, GatewayError* error) {
    if (request->amount <= 0) {
        error->error_code = 400;
        snprintf(error->message, sizeof(error->message), "CreditCard: So tien khong hop le");
        return 0;
    }
    printf("Thanh toan CreditCard thanh cong cho request %s\\n", request->request_id);
    return 1;
}

PaymentStrategy create_credit_card_strategy() {
    PaymentStrategy s;
    s.name = "CreditCard";
    s.pay = credit_card_pay;
    return s;
}
""",
    "src/paypal_strategy.c": """#include <stdio.h>
#include <string.h>
#include "payment_strategy.h"

int paypal_pay(const PaymentRequest* request, GatewayError* error) {
    if (request->amount <= 0) {
        error->error_code = 400;
        snprintf(error->message, sizeof(error->message), "Paypal: So tien khong hop le");
        return 0;
    }
    printf("Thanh toan Paypal thanh cong cho request %s\\n", request->request_id);
    return 1;
}

PaymentStrategy create_paypal_strategy() {
    PaymentStrategy s;
    s.name = "Paypal";
    s.pay = paypal_pay;
    return s;
}
""",
    "include/payment_processor.h": """#ifndef PAYMENT_PROCESSOR_H
#define PAYMENT_PROCESSOR_H

#include "payment_strategy.h"

typedef struct {
    PaymentStrategy strategy;
} PaymentProcessor;

PaymentProcessor create_processor(PaymentStrategy strategy);
int processor_execute(PaymentProcessor* processor, const PaymentRequest* request, GatewayError* error);

#endif
""",
    "src/payment_processor.c": """#include "payment_processor.h"

PaymentProcessor create_processor(PaymentStrategy strategy) {
    PaymentProcessor p;
    p.strategy = strategy;
    return p;
}

int processor_execute(PaymentProcessor* processor, const PaymentRequest* request, GatewayError* error) {
    return processor->strategy.pay(request, error);
}
""",
    "src/main.c": """#include <stdio.h>
#include "payment_types.h"
#include "payment_processor.h"

extern PaymentStrategy create_credit_card_strategy();

int main() {
    PaymentRequest req = {"REQ_001", 100.0, CURRENCY_USD};
    PaymentStrategy card_strat = create_credit_card_strategy();
    PaymentProcessor processor = create_processor(card_strat);

    GatewayError err;
    if (!processor_execute(&processor, &req, &err)) {
        printf("Loi [%d]: %s\\n", err.error_code, err.message);
    }
    return 0;
}
"""
}

for path, content in files_c.items():
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("[SUCCESS] Đã khởi tạo Nấc 2 (8 Files C Language) thành công!")
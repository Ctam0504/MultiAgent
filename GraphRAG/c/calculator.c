#include "calculator.h"

void log_operation(const char* op_name) {
    printf("[LOG] Executing operation: %s\n", op_name);
}

void init_calculator(CalculatorState *calc) {
    if (calc != NULL) {
        calc->last_result = 0.0;
        calc->operation_count = 0;
    }
}

double add(CalculatorState *calc, double a, double b) {
    log_operation("ADD");
    double res = a + b;
    if (calc != NULL) {
        calc->last_result = res;
        calc->operation_count++;
    }
    return res;
}

double divide(CalculatorState *calc, double a, double b) {
    log_operation("DIVIDE");
    if (b == 0.0) {
        printf("[ERROR] Division by zero!\n");
        return 0.0;
    }
    double res = a / b;
    if (calc != NULL) {
        calc->last_result = res;
        calc->operation_count++;
    }
    return res;
}
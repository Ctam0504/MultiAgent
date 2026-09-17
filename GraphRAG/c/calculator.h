#ifndef CALCULATOR_H
#define CALCULATOR_H

#include <stdio.h>

// Định nghĩa Struct lưu trữ kết quả tính toán
typedef struct {
    double last_result;
    int operation_count;
} CalculatorState;

// Khai báo các hàm API
void init_calculator(CalculatorState *calc);
double add(CalculatorState *calc, double a, double b);
double divide(CalculatorState *calc, double a, double b);

#endif // CALCULATOR_H
#include <stdio.h>
#include "calculator.h"

int main() {
    CalculatorState calc;
    
    // Gọi hàm khởi tạo
    init_calculator(&calc);
    
    // Gọi các phép tính toán
    double sum = add(&calc, 10.5, 4.5);
    double quotient = divide(&calc, sum, 3.0);
    
    printf("Final Result: %.2f (Total Operations: %d)\n", 
           calc.last_result, calc.operation_count);
           
    return 0;
}
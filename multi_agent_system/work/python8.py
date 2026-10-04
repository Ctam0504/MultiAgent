import os

files_py = {
    "models/currency.py": """from enum import Enum

class Currency(Enum):
    USD = "USD"
    VND = "VND"
""",
    "models/payment_request.py": """from models.currency import Currency

class PaymentRequest:
    def __init__(self, request_id: str, amount: float, currency: Currency):
        self.request_id = request_id
        self.amount = amount
        self.currency = currency
""",
    "exceptions/gateway_exception.py": """class GatewayException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
""",
    "strategies/base_strategy.py": """from abc import ABC, abstractmethod
from models.payment_request import PaymentRequest

class IPaymentStrategy(ABC):
    @abstractmethod
    def pay(self, request: PaymentRequest) -> bool:
        pass
""",
    "strategies/credit_card_strategy.py": """from strategies.base_strategy import IPaymentStrategy
from models.payment_request import PaymentRequest
from exceptions.gateway_exception import GatewayException

class CreditCardStrategy(IPaymentStrategy):
    def pay(self, request: PaymentRequest) -> bool:
        if request.amount <= 0:
            raise GatewayException("CreditCard: Số tiền không hợp lệ")
        print(f"Thanh toán CreditCard thành công cho request {request.request_id}")
        return True
""",
    "strategies/paypal_strategy.py": """from strategies.base_strategy import IPaymentStrategy
from models.payment_request import PaymentRequest
from exceptions.gateway_exception import GatewayException

class PaypalStrategy(IPaymentStrategy):
    def pay(self, request: PaymentRequest) -> bool:
        if request.amount <= 0:
            raise GatewayException("Paypal: Số tiền không hợp lệ")
        print(f"Thanh toán Paypal thành công cho request {request.request_id}")
        return True
""",
    "services/payment_processor.py": """from strategies.base_strategy import IPaymentStrategy
from models.payment_request import PaymentRequest

class PaymentProcessor:
    def __init__(self, strategy: IPaymentStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: IPaymentStrategy) -> None:
        self.strategy = strategy

    def execute(self, request: PaymentRequest) -> bool:
        return self.strategy.pay(request)
""",
    "main.py": """from models.currency import Currency
from models.payment_request import PaymentRequest
from strategies.credit_card_strategy import CreditCardStrategy
from services.payment_processor import PaymentProcessor
from exceptions.gateway_exception import GatewayException

def main():
    request = PaymentRequest("REQ_001", 100.0, Currency.USD)
    processor = PaymentProcessor(CreditCardStrategy())

    try:
        processor.execute(request)
    except GatewayException as e:
        print(f"Lỗi: {e.message}")

if __name__ == "__main__":
    main()
"""
}

for path, content in files_py.items():
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("[SUCCESS] Đã khởi tạo Nấc 2 (8 Files Python) thành công!")
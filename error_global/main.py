# LỖI GIỮA CÁC FILE: Vẫn import và gọi tên hàm cũ `process_payment`
from payment_service import process_payment

def checkout():
    total_price = 150
    if total_price > 0:
        process_payment(total_price)

if __name__ == "__main__":
    checkout()
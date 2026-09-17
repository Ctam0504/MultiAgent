from payment_service import process_payment

def checkout():
    total_price = 150
    # LỖI NỘI BỘ: Thừa dấu ngoặc vuông đóng sai vị trí / sai cú pháp
    if total_price > 0]:
        process_payment(total_price)

if __name__ == "__main__":
    checkout()
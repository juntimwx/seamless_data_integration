def abbreviate_number(num):
    """
    ฟังก์ชันย่อจำนวนให้เป็นรูปแบบ K, M, B, ...
    เช่น 2500 => 2.5K, 1,230,000 => 1.2M
    """
    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000:
            return f"{num:3.1f}{unit}"
        num /= 1000.0
    return f"{num:3.1f}P"  # เกิน T ก็ใส่เป็น P (Petabyte scale) ไปเลย

# Add Trimester column based on the month
def get_trimester(month):
    if month in [10, 11, 12]:
        return 'Trimester 1'
    elif month in [1, 2, 3]:
        return 'Trimester 2'
    elif month in [4, 5, 6]:
        return 'Trimester 3'
    else:
        return 'Trimester 4'
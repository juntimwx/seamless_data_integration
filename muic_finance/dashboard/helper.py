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

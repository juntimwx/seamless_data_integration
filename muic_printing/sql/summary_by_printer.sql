SELECT 
    tpul.printer_id,
    tp.printer_name,
    
    -- ดึงวันที่และเวลาในรูปแบบ YYYY-MM-DD HH24:00
    TO_CHAR(tpul.usage_date, 'YYYY-MM-DD HH24:00') AS usage_datetime,
    
    -- ดึงชื่อวันในสัปดาห์เป็นภาษาไทย เช่น จันทร์, อังคาร เป็นต้น
    CASE 
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Monday   ' THEN 'จันทร์'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Tuesday  ' THEN 'อังคาร'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Wednesday' THEN 'พุธ'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Thursday ' THEN 'พฤหัสบดี'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Friday   ' THEN 'ศุกร์'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Saturday' THEN 'เสาร์'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Sunday' THEN 'อาทิตย์'
        ELSE TO_CHAR(tpul.usage_date, 'Day')
    END AS day_of_week,
    
    -- ระบุช่วงเวลาว่าเป็น เช้า สาย บ่าย หรือ เย็น
    CASE 
        WHEN EXTRACT(HOUR FROM tpul.usage_date) BETWEEN 6 AND 10 THEN 'เช้า'
        WHEN EXTRACT(HOUR FROM tpul.usage_date) BETWEEN 11 AND 13 THEN 'สาย'
        WHEN EXTRACT(HOUR FROM tpul.usage_date) BETWEEN 14 AND 17 THEN 'บ่าย'
        WHEN EXTRACT(HOUR FROM tpul.usage_date) BETWEEN 18 AND 21 THEN 'เย็น'
        ELSE 'อื่นๆ'
    END AS time_period,
    
    -- สรุปจำนวนหน้าที่พิมพ์ในแต่ละชั่วโมง
    SUM(tpul.total_pages) AS total_pages_per_hour,
    
    -- นับจำนวนผู้ใช้ที่ใช้เครื่องพิมพ์ในแต่ละชั่วโมง โดยนับเฉพาะผู้ใช้ที่ไม่ซ้ำกัน
    COUNT(DISTINCT tpul.used_by_user_id) AS user_count
FROM tbl_printer_usage_log tpul
LEFT JOIN tbl_printer tp ON tpul.printer_id = tp.printer_id
WHERE 
    tpul.printer_id = 9009
    AND tpul.usage_date >= DATE '2024-10-01'
GROUP BY
    tpul.printer_id,
    tp.printer_name,
    TO_CHAR(tpul.usage_date, 'YYYY-MM-DD HH24:00'),
    CASE 
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Monday   ' THEN 'จันทร์'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Tuesday  ' THEN 'อังคาร'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Wednesday' THEN 'พุธ'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Thursday ' THEN 'พฤหัสบดี'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Friday   ' THEN 'ศุกร์'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Saturday' THEN 'เสาร์'
        WHEN TO_CHAR(tpul.usage_date, 'Day') = 'Sunday' THEN 'อาทิตย์'
        ELSE TO_CHAR(tpul.usage_date, 'Day')
    END,
    CASE 
        WHEN EXTRACT(HOUR FROM tpul.usage_date) BETWEEN 6 AND 10 THEN 'เช้า'
        WHEN EXTRACT(HOUR FROM tpul.usage_date) BETWEEN 11 AND 13 THEN 'สาย'
        WHEN EXTRACT(HOUR FROM tpul.usage_date) BETWEEN 14 AND 17 THEN 'บ่าย'
        WHEN EXTRACT(HOUR FROM tpul.usage_date) BETWEEN 18 AND 21 THEN 'เย็น'
        ELSE 'อื่นๆ'
    END
ORDER BY
    usage_datetime;

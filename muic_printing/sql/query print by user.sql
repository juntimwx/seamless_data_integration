SELECT 
    usr.user_name, 
    usr.full_name, 
    usr.department, 
    usr.office, 
    printlog.job_type,
    printlog.total_color_pages AS color_pages,
    CASE
        WHEN printlog.gray_scale = 'Y' THEN printlog.total_pages - printlog.total_color_pages
        ELSE 0
    END AS grayscale_pages,
    printlog.total_pages AS total_printed_pages,
    printlog.total_color_pages * 4.82 AS ColorPage_Cost,
    (CASE
        WHEN printlog.gray_scale = 'Y' THEN (printlog.total_pages - printlog.total_color_pages)
        ELSE 0
    END) * 0.48 AS Grayscale_Cost,
    (printlog.total_color_pages * 4.82) +
    ((CASE
        WHEN printlog.gray_scale = 'Y' THEN (printlog.total_pages - printlog.total_color_pages)
        ELSE 0
    END) * 0.48) AS "Total Printed Cost",
    --TO_CHAR(printlog.usage_day, 'YYYY-MM-DD') AS usage_day,
    TO_CHAR(printlog.usage_day, 'YYYY') AS year,
    TO_CHAR(printlog.usage_day, 'Month') AS month,
    case
    	when TO_CHAR(printlog.usage_day, 'Month') = 'October' then '1'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'November' then '2'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'December' then '3'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'January' then '4'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'February' then '5'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'March' then '6'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'April' then '7'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'May' then '8'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'June' then '9'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'July' then '10'
    	when TO_CHAR(printlog.usage_day, 'Month') = 'August' then '11'
    	--when TO_CHAR(printlog.usage_day, 'Month') = 'September' then '12'
    	else '12'
    end as num_month
FROM
    tbl_printer_usage_log printlog
JOIN
    tbl_user usr
    ON printlog.used_by_user_id = usr.user_id
WHERE
    printlog.usage_day > TO_DATE('2023-09-30', 'YYYY-MM-DD')
ORDER BY
    usr.user_name, printlog.usage_day;

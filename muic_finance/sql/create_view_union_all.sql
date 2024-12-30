CREATE view erp_clean AS
SELECT * FROM erp_2022_clean
UNION ALL
SELECT * FROM erp_2023_clean
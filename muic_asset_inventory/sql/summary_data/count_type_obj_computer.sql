SELECT
    t.type_name AS asset_type_name,
    obj.objective_name,
    COUNT(*) AS total_count
FROM dbo.items AS i
    LEFT JOIN master.master_item_types t
        ON i.asset_type = t.id
    LEFT JOIN master.master_item_objectives obj
        ON i.objective = obj.id
    -- เชื่อมตารางอื่น ๆ ตามต้องการ
--WHERE obj.id IN ('2','3','4','8','15')
where i.asset_type in  ('1','2','6','10','22')
GROUP BY
    t.type_name,
    obj.objective_name
ORDER BY
    t.type_name,
    obj.objective_name
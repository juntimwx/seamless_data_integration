SELECT
    t.type_name AS asset_type_name,
    obj.objective_name,
    --room.building_name,
    'building 1-3' as building_name,
    COUNT(*) AS total_count
FROM dbo.items AS i
    LEFT JOIN master.master_item_types t
        ON i.asset_type = t.id
    LEFT JOIN master.master_item_objectives obj
        ON i.objective = obj.id
    left join master.master_rooms room
        on i.location = room.id
-- เชื่อมตารางอื่น ๆ ตามต้องการ
--WHERE obj.id IN ('2','3','4','8','15')
where i.asset_type in  ('1','2','6','10','22') AND room.building_name != 'aditayathorn'
GROUP BY
    t.type_name,
    --room.building_name,
    obj.objective_name
ORDER BY
    t.type_name,
    --room.building_name,
    obj.objective_name
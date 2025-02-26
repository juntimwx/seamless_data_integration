SELECT
    t.type_name AS [ประเภทเครื่องคอมพิวเตอร์],
    b.brand_name AS [ยี่ห้อ],
    COUNT(*) AS [จำนวน]
FROM dbo.items AS i
LEFT JOIN master.master_item_types AS t
    ON i.asset_type = t.id
LEFT JOIN master.master_item_brands AS b
    ON i.brand = b.id
where i.asset_type in  ('1','2','6','10','22')
GROUP BY
    t.type_name,
    b.brand_name
ORDER BY
    t.type_name,
    COUNT(*) DESC;

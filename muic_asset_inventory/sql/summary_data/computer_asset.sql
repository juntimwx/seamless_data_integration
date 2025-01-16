select item.id,
    asset_number,
    serial_number,
    asset_name,
    asset_status,
    asset_group,
    asset_date,
    objective as objective_id,
    obj.objective_name as objective_name,
    project_service as project_id,
    project.project_name as project_name,
    owner as staff_id,
    profile.name_thai + ' ' + profile.surname_thai as full_name,
    department_owner as department_owner_id,
    department.name_thai as department_owner_name,
    location as location_id,
    room.building_name as location_building,
    room.room_number as location_room_number,
    room.room_name as location_room_name,
    asset_type as asset_type_id,
    type.type_name as asset_type_name,
    brand as asset_brand_id,
    masterBrand.brand_name as asset_brand_name,
    generation,
    ram_type,
    ram_unit,
    asset_os as operating_system_id,
    os.os_name as operating_system_name,
    harddisk
from dbo.items item
left join master.master_item_objectives obj on item.objective = obj.id
left join master.master_item_projects project on item.project_service = project.id
left join master.master_staff_profiles profile on item.owner = profile.code
left join master.master_departments department on item.department_owner = department.id
left join master.master_rooms room on item.location = room.id
left join master.master_item_types type on item.asset_type = type.id
left join master.master_item_brands masterBrand on item.brand = masterBrand.id
left join master.master_item_operating_systems os on item.asset_os = os.id
where asset_type in  ('1','2','4','6','7','22') --AND room.building_name IS NULL
--where room.building_name != 'aditayathorn'
CREATE SCHEMA master

CREATE TABLE master.master_item_brands(
    id INT PRIMARY KEY NOT NULL,
    brand_name VARCHAR(100) NOT NULL
)

CREATE TABLE master.master_item_harddisk_types(
    id INT PRIMARY KEY NOT NULL,
    harddisk_type VARCHAR(100) NULL,
    harddisk_unit VARCHAR(100) NULL,
)

CREATE TABLE master.master_item_objectives(
    id INT PRIMARY KEY NOT NULL,
    objective_name VARCHAR(100) NOT NULL
)

CREATE TABLE master.master_item_operating_systems(
    id INT PRIMARY KEY NOT NULL,
    os_name VARCHAR(100) NULL,
    os_group VARCHAR(100) NOT NULL
)

CREATE TABLE master.master_item_projects(
    id INT PRIMARY KEY NOT NULL,
    project_name VARCHAR(100) NULL,
)

CREATE TABLE master.master_item_types(
    id INT PRIMARY KEY NOT NULL,
    type_name VARCHAR(100) NOT NULL,
)

CREATE TABLE master.master_rooms(
    id INT PRIMARY KEY NOT NULL,
    building_name VARCHAR(200) NULL,
    room_name VARCHAR(200) NULL,
    room_number VARCHAR(200) NULL,
    floor INT NULL,
    normal_seat INT NULL,
    max_seat INT NULL,
    exam_seat INT NULL,
    room_type VARCHAR(100) NULL,
    use_group VARCHAR(100) NULL,
    remark VARCHAR(MAX) NULL,
    status VARCHAR(10) NULL
)

CREATE TABLE master.master_departments(
    id INT PRIMARY KEY NOT NULL,
    name_thai VARCHAR(200) NOT NULL,
    name_eng VARCHAR(200) NOT NULL,
    shortness  VARCHAR(100) NULL,
    group_eng VARCHAR(200) NULL,
    group_thai VARCHAR(200) NULL,
    under INT NOT NULL,
    level INT NOT NULL,
)

CREATE TABLE dbo.items(
    id INT NOT NULL,
    asset_number VARCHAR(MAX) NULL,
    serial_number VARCHAR(MAX) NULL,
    asset_name VARCHAR(MAX) NULL,
    asset_status VARCHAR(MAX) NULL,
    asset_group VARCHAR(MAX) NULL,
    asset_date DATE,
    objective INT NULL,
    project_service INT NULL,
    owner INT NULL,
    department_owner INT NULL,
    location INT NULL,
    asset_type INT NULL,
    brand INT NULL,
    generation VARCHAR(MAX) NULL,
    ram_type VARCHAR(100) NULL,
    ram_unit INT NULL,
    asset_os INT NULL,
    harddisk VARCHAR(MAX) NULL,
)

CREATE TABLE master.master_staff_profiles(
    code VARCHAR(50) PRIMARY KEY  NOT NULL,
    name_thai VARCHAR(100) NOT NULL,
    surname_thai VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NULL,
    position_thai VARCHAR(100) NULL,
    position VARCHAR(100) NOT NULL,
    department INT NOT NULL,
)
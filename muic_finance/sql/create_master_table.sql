CREATE SCHEMA master

CREATE TABLE master.master_cost_center (
    id VARCHAR(50) PRIMARY KEY NOT NULL,
    description VARCHAR(MAX) NOT NULL,
	name_en varchar(MAX) NULL,
	name_th varchar(MAX) NULL
    -- CostCtr_Id	CostCtr_Description	CostCtr_Eng	CostCtr_TH
)

CREATE TABLE master.master_funds (
    id INT PRIMARY KEY NOT NULL,
    description VARCHAR(MAX) NOT NULL
    -- Fund_Id	Fund_Description
    -- มี * ช่องหลังสุดด้วย
)

-- file name master_gl
CREATE TABLE master.master_general_ledger (
    id BIGINT PRIMARY KEY NOT NULL, -- must use big integer because INT: Ranges from -2,147,483,648 to 2,147,483,647
    description VARCHAR(MAX) NOT NULL,
    group_id VARCHAR(50) NOT NULL,
    group_description VARCHAR(MAX) NOT NULL
    -- Group	Id	Description	Group_Description
)

CREATE TABLE master.master_ic_strategy (
    id VARCHAR(100) PRIMARY KEY NOT NULL,
    year_start INT NOT NULL,
    year_end INT NOT NULL,
    name VARCHAR(MAX) NOT NULL,
    description VARCHAR(MAX) NULL,
    status TINYINT NOT NULL
    -- ID_ICST	Year_start	Year_end	Name	Description	status
)


CREATE TABLE master.master_mu_strategy (
    id VARCHAR(100) PRIMARY KEY NOT NULL,
    year_start INT NOT NULL,
    year_end INT NOT NULL,
    name VARCHAR(MAX) NOT NULL,
    description VARCHAR(MAX) NULL,
    status TINYINT NOT NULL
    -- ID_MUST	Year_start	Year_end	Name	Description	status
)

CREATE TABLE master.master_io_activities (
    id INT PRIMARY KEY NOT NULL,
    description VARCHAR(MAX) NULL
    --IO_Activity_Id	IO_Activity_Description
)

CREATE TABLE master.master_io_goods (
    id BIGINT PRIMARY KEY NOT NULL,
    description VARCHAR(MAX) NULL
    -- IO_Goods_Id	IO_Goods_Description
)

CREATE TABLE master.mater_io_projects (
    id BIGINT PRIMARY KEY, -- Unique identifier for the project
    description VARCHAR(MAX),
    cost_ctr_id VARCHAR(50), -- Foreign key reference for cost center => master_cost_center
    ic_strategy_id VARCHAR(100), -- Foreign key reference for IC Strategy  master_ic_strategy
    mu_strategy_id VARCHAR(100), -- Foreign key reference for IC Strategy  master_ic_strategy
    CONSTRAINT fk_cost_ctr FOREIGN KEY (cost_ctr_id) REFERENCES master.master_cost_center(id), -- Assuming a table 'master.master_cost_center' with 'id' column
    CONSTRAINT fk_ic_strategy FOREIGN KEY (ic_strategy_id) REFERENCES master.master_ic_strategy(id), -- Assuming a table 'master.master_ic_strategy' with id column
    CONSTRAINT fk_mu_strategy FOREIGN KEY (mu_strategy_id) REFERENCES master.master_mu_strategy(id),
    -- IO_Project	IO_Project_Description	CostCtr	ID_ICST	ID_MUST
)

CREATE TABLE master.master_io_works (
    id INT,
    description VARCHAR(MAX),
    -- IO_Work_Id	IO_Work_Description
)

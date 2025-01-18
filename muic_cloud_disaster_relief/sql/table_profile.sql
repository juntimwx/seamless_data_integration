CREATE TABLE staff_profiles(
    code VARCHAR(50) PRIMARY KEY  NOT NULL,
    email VARCHAR(200) NULL,
    groupmail VARCHAR(100) NULL,
    muic_account VARCHAR(100) NULL,
    title INT NOT NULL,
    title_base INT NOT NULL,
    name_thai VARCHAR(100) NOT NULL,
    surname_thai VARCHAR(100) NOT NULL,
    user_type INT NULL,
    contract INT NULL,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NULL,
    position_thai VARCHAR(100) NULL,
    position VARCHAR(100) NULL,
    department INT NOT NULL,
    gender INT NOT NULL,
    [group] INT NOT NULL,
    degree INT NULL,
    status INT NOT NULL,
    resign VARCHAR(100) NULL,
)
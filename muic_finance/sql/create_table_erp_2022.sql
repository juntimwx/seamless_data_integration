CREATE TABLE erp_2022 (
    year INT NOT NULL,
    trimester TINYINT NOT NULL CHECK (trimester BETWEEN 1 AND 4),
    day TINYINT NOT NULL CHECK (day BETWEEN 1 AND 31),
    month TINYINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    doc_no BIGINT NOT NULL,
    doc_date DATE NOT NULL,
    funds_center INT NOT NULL,
    cost_center_id VARCHAR(50) NOT NULL,
    cost_centralize VARCHAR(50) NULL,
    io_good_id BIGINT NULL,
    io_work_id VARCHAR(100) NULL,
    io_activity_id INT NULL,
    io_project_id BIGINT NULL,
    order_description VARCHAR(MAX) NULL,
    hrot VARCHAR(MAX) NULL,
    general_ledger_id BIGINT NULL,
    general_ledger_description VARCHAR(MAX) NULL,
    amount FLOAT NOT NULL CHECK (amount >= 0),
    detail VARCHAR(MAX) NULL,
    mu_strategy_id VARCHAR(100) NULL,
    ic_strategy_id VARCHAR(100) NULL,
    -- Use a NEW name for the day check constraint:
    CONSTRAINT ck_erp_2022_validate_day CHECK (
        (
            month IN (1,3,5,7,8,10,12)
            AND day <= 31
        )
        OR (
            month IN (4,6,9,11)
            AND day <= 30
        )
        OR (
            month = 2
            AND day <= 29
            AND (
                (year % 4 = 0 AND year % 100 != 0)
                OR (year % 400 = 0)
            )
        )
        OR (
            month = 2
            AND day <= 28
            AND NOT (
                (year % 4 = 0 AND year % 100 != 0)
                OR (year % 400 = 0)
            )
        )
    ),
    CONSTRAINT fk_erp_2022_cost_center
        FOREIGN KEY (cost_center_id)
        REFERENCES master.master_cost_center (id),
    CONSTRAINT fk_erp_2022_io_good
        FOREIGN KEY (io_good_id)
        REFERENCES master.master_io_goods (id),
    CONSTRAINT fk_erp_2022_io_work_id
        FOREIGN KEY (io_work_id)
        REFERENCES master.master_io_works (id) ON DELETE SET NULL,
    CONSTRAINT fk_erp_2022_io_activity
        FOREIGN KEY (io_activity_id)
        REFERENCES master.master_io_activities (id),
    CONSTRAINT fk_erp_2022_io_project
        FOREIGN KEY (io_project_id)
        REFERENCES master.master_io_projects (id),
    CONSTRAINT fk_erp_2022_general_ledger
        FOREIGN KEY (general_ledger_id)
        REFERENCES master.master_general_ledger (id),
    CONSTRAINT fk_erp_2022_mu_strategy
        FOREIGN KEY (mu_strategy_id)
        REFERENCES master.master_mu_strategy (id),
    CONSTRAINT fk_erp_2022_ic_strategy
        FOREIGN KEY (ic_strategy_id)
        REFERENCES master.master_ic_strategy (id)
);

create table sa_student_disciplinary(
    academic_year INT,
    term INT,
    disciplinary_date DATE,
    disciplinary_time_start TIME,
    disciplinary_time_end TIME,
    student_id INT,
    gender CHAR(1),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    major VARCHAR(100),
    subject_code VARCHAR(100),
    subject_name VARCHAR(100),
    lecturer_name VARCHAR(100),
    type_of_issue VARCHAR(100),
    type_other VARCHAR(100),
    type_of_exam VARCHAR(100),
    regulation_number VARCHAR(100),
    issue_level TEXT,
    punishment_level TEXT,
    details TEXT,
    location TEXT,
    educational_sanctions TEXT,
    disciplinary_sanctions TEXT,
    appeal TEXT,
    appeal_result TEXT,
    remark TEXT,
)

-- old version
-- create table sa_student_disciplinary(
--     academic_year varchar(100),
--     term int,
--     date date,
--     time varchar(100),
--     student_id varchar(10),
--     gender varchar(1),
--     first_name varchar(100),
--     last_name varchar(100),
--     major varchar(100),
--     subject_code varchar(100),
--     subject_name varchar(100),
--     lecturer_name varchar(100),
--     type_of_issue varchar(100),
--     type_other varchar(100),
--     type_of_exam varchar(100),
--     regulation_number varchar(100),
--     issue_level varchar(max),
--     punishment_level varchar(max),
--     details varchar(max),
--     location varchar(max),
--     educational_sanctions varchar(max),
--     disciplinary_sanctions varchar(max),
--     appeal varchar(max),
--     appeal_result varchar(max),
--     remark varchar(max),
-- )
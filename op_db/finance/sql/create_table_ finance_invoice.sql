CREATE TABLE finance_invoice_20250131(
    invoiceId VARCHAR(30) NOT NULL, 
    acaYear VARCHAR(4) NOT NULL, 
    semester INT NOT NULL CHECK(semester BETWEEN 1 AND 4),
    invoiceNo VARCHAR(20) NOT NULL, 
    regisType VARCHAR(5) NOT NULL, 
    invoiceAmount DECIMAL NOT NULL, 
    paidDate DATETIME NULL,
--     paidDate VARCHAR(100) NOT NULL,
    paidAmount DECIMAL NOT NULL, 
    paidStatus VARCHAR(1) NOT NULL, 
    invoiceType VARCHAR(30) NOT NULL, 
    schNameTh VARCHAR(200) NULL, 
    remark VARCHAR(100) NULL, 
    studentCode VARCHAR(15) NOT NULL
)
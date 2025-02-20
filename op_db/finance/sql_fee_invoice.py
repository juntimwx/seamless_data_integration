import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote
from dotenv import load_dotenv
import os

# load variable form .env file.
load_dotenv()

sky_engine = create_engine(f"mssql+pyodbc://{os.getenv('SKY_USERNAME')}:{quote(os.getenv('SKY_PASSWORD'))}@{os.getenv('SKY_HOST')}/{os.getenv('SKY_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
# engine = create_engine(f"mssql+pyodbc://{os.getenv('LOCAL_USERNAME')}:{quote(os.getenv('LOCAL_PASSWORD'))}@{os.getenv('LOCAL_HOST')}/{os.getenv('OP_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")
engine = create_engine(f"mssql+pyodbc://{os.getenv('DATA_USERNAME')}:{quote(os.getenv('DATA_PASSWORD'))}@{os.getenv('DATA_HOST')}/{os.getenv('OP_DATABASE')}?driver=ODBC+Driver+17+for+SQL+Server")

data = pd.read_sql('''
SELECT invoice.Id invoiceId,
	term.AcademicYear acaYear, 
	term.AcademicTerm semester,
	invoice.Number invoiceNo,
    CASE WHEN invoice.[Type] = 'r' THEN 'N'
        WHEN invoice.[Type] = 'a' THEN 'A'
        WHEN invoice.[Type] = 'cr' THEN 'A'
        WHEN invoice.[Type] = 'au' THEN 'E'
    END regisType,
	invoice.Amount invoiceAmount,
    CASE WHEN invoice.IsPaid = 0 THEN NULL -- ใช้ N เพื่อรองรับ Unicode
        ELSE FORMAT(invoice.UpdatedAt, 'yyyy-MM-dd HH:mm:ss') -- แปลงวันที่เป็นสตริง
        --ELSE invoice.UpdatedAt
    END paidDate,
	invoice.TotalAmount paidAmount,
	CASE WHEN invoice.IsPaid = 0 THEN 'N'
		ELSE 'Y' END paidStatus,
	CASE WHEN invoiceItem.FeeItemName LIKE 'Lump sum%' THEN N'เหมาจ่าย' -- การใส่ N เป็นการบอก SQL Server ว่าสตริงนี้เป็น Unicode ซึ่งรองรับอักขระภาษาไทย
		ELSE N'หน่วยกิต' END AS invoiceType,
	NULL schNameTh,
	NULL remark,
	student.Code studentCode
FROM  fee.Invoices invoice
LEFT JOIN dbo.Terms term ON invoice.TermId = term.Id 
LEFT JOIN student.Students student ON invoice.StudentId = student.Id 
LEFT JOIN fee.InvoiceItems invoiceItem ON invoiceItem.InvoiceId = invoice.Id
--WHERE invoice.Number  = '24010012'
''', sky_engine)

df = pd.DataFrame(data)

print(df)
df.to_sql('finance_invoice_20250220', engine, index=False, chunksize=500, if_exists='append')
# df.to_sql('finance_invoice_20250214', engine, index=False, chunksize=500, if_exists='append')
# df.to_sql('finance_invoice_20250131', engine, index=False, chunksize=500, if_exists='append')
# df.to_sql('finance_invoice_20250124', engine, index=False, chunksize=500, if_exists='append')  #replace
# df.to_sql('finance_invoice_20250118', engine, index=False, chunksize=500, if_exists='append')  #replace
# df.to_sql('finance_invoice_20250106', engine, index=False, chunksize=500, if_exists='append')  #replace
# df.to_sql('finance_invoice', engine, index=False, chunksize=500, if_exists='append')  #replace
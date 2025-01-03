SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


ALTER VIEW [dbo].[Finance_invoice]
AS
SELECT  invoiceId, acaYear, semester, invoiceNo, 

CASE 
WHEN [regisType] = 'Registration' THEN 'N' 
WHEN [regisType] = 'Add/Drop' THEN 'A' 
END AS regisType, 

invoiceAmount, paidDate, 
CAST(paidAmount AS DECIMAL(10, 2)) AS paidAmount,
                         
CASE 
WHEN [paidStatus] = 'Paid' THEN 'Y' 
WHEN [paidStatus] = 'Unpaid' THEN 'N' END AS paidStatus, 

CASE
WHEN remark = 'ICCT' THEN 'Credit' 
ELSE 'Credit' END AS invoiceType, 

schNameTh, remark, studentCode

--FROM   dbo.FIN_Invoice_2066
FROM dbo.finance_invoice_2025_01_03
WHERE (regisType IN ('Add/Drop', 'Registration')) AND (paidAmount > 0)
GO

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
    CASE WHEN invoice.IsPaid = 0 THEN N'-' -- ใช้ N เพื่อรองรับ Unicode
        ELSE FORMAT(invoice.UpdatedAt, 'yyyy-MM-dd HH:mm:ss') -- แปลงวันที่เป็นสตริง
        --ELSE invoice.UpdatedAt
    END paidDate,
	invoice.TotalAmount paidAmount,
	CASE WHEN invoice.IsPaid = 0 THEN 'N'
		ELSE 'Y' END paidStatus,
	CASE WHEN invoiceItem.FeeItemName LIKE 'Lump sum%' THEN N'เหมาจ่าย' -- การใส่ N เป็นการบอก SQL Server ว่าสตริงนี้เป็น Unicode ซึ่งรองรับอักขระภาษาไทย
		ELSE N'หน่วยกิต' END AS invoiceType,
	'' schNameTh,
	'' remark,
	student.Code studentCode
FROM  fee.Invoices invoice
LEFT JOIN dbo.Terms term ON invoice.TermId = term.Id 
LEFT JOIN student.Students student ON invoice.StudentId = student.Id 
LEFT JOIN fee.InvoiceItems invoiceItem ON invoiceItem.InvoiceId = invoice.Id
--WHERE invoice.Number  = '24010012'
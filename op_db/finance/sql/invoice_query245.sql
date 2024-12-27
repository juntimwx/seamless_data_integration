SELECT invoice.Id invoiceId,
	term.AcademicYear acaYear, 
	term.AcademicTerm semester,
	invoice.Number invoiceNo,
	invoice.Amount invoiceAmount,
	invoice.TotalAmount paidAmount,
	CASE WHEN invoice.IsPaid = 0 THEN 'N'
		ELSE 'Y' END paidStatus,
	CASE WHEN invoiceItem.FeeItemName LIKE 'Lump sum%' THEN 'เหมาจ่าย'
		ELSE 'Credit' END AS invoiceType,
	'' schNameTh,
	'' remark,
	student.Code 
FROM  fee.Invoices invoice
LEFT JOIN dbo.Terms term ON invoice.TermId = term.Id 
LEFT JOIN student.Students student ON invoice.StudentId = student.Id 
LEFT JOIN fee.InvoiceItems invoiceItem ON invoiceItem.InvoiceId = invoice.Id
--WHERE invoice.Number  = '24010012'
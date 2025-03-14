select
	case when student.prefix = 'Mrs.' then '002'
		when student.prefix = 'Ms.' then '003'
	else '001' end 'รหัสคำนำหน้าชื่อ'
	,student.prefix 'คำนำหน้าชื่อ'
	,case when student.name_th LIKE '%นาย%' THEN TRIM(SUBSTRING(student.name_th, CHARINDEX('นาย', student.name_th) + 3, LEN(student.name_th)))
		when student.name_th LIKE '%นางสาว%' THEN TRIM(SUBSTRING(student.name_th, CHARINDEX('นางสาว', student.name_th) + 6, LEN(student.name_th)))
		when student.name_th IS NULL then UPPER(TRIM(student.name_en))
	else TRIM(student.name_th) end 'ชื่อ(ภาษาไทย)'
	,NULL 'ชื่อกลาง(ภาษาไทย)'
	,case when student.lastname_th IS NULL then UPPER(TRIM(student.lastname_en))
	else TRIM(student.lastname_th) end 'สกุล(ภาษาไทย)'
	,UPPER(TRIM(student.name_en)) 'ชื่อ(ภาษาอังกฤษ)'
	,NULL 'ชื่อกลาง(ภาษาอังกฤษ)'
	,UPPER(TRIM(student.lastname_en)) 'สกุล(ภาษาอังกฤษ)'
	,case when student.prefix = 'Mr.' then 'M'
	else 'F' end 'เพศ'
	,case when LEN(student.citizen_number) >= 13 then REPLACE(REPLACE(student.citizen_number, '-', ''), ' ', '')
	else NULL end 'เลขประจำตัวประชาชน'
	,case when LEN(student.citizen_number) < 13 then student.citizen_number
	else NULL end 'เลขหนังสือเดินทาง'
	,CONVERT(VARCHAR(10), DATEADD(YEAR, 543, TRY_CONVERT(DATE, RIGHT(CONVERT(VARCHAR(50), student.birthday), 8))), 103) 'วันเดือนปีเกิด'
	,LEFT(student.student_id,6) 'รหัสนักศึกษา'
	,'PC' 'รหัสคณะ'
	,pcMajor.major_code 'รหัสหลักสูตร'
	,pcMajor.major_name 'ชื่อหลักสูตร'
	,NULL 'รหัสสาขา'
	,'0' 'ระดับการศึกษา' --no degree
	,student.student_level 'กลุ่ม'
	,student.student_status 'สถานภาพนักศึกษา'
from (
	select * from PC_StudentPC_20250314 
	union all 
	select * from PC_StudentMP_20250314
) student
left join PC_Major pcMajor on student.major_id = pcMajor.major_id
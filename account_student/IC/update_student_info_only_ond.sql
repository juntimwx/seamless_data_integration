--กรณีจะ update ข้อมูลสถานะ หรือ ข้อมูลอื่นๆ ต้อง select ข้อมูลมาตรวจสอบก่อนว่าเดิมเป็นอะไร

select * from UpdateStudentStatus_20250226 where [รหัสนักศึกษา] = '6580880'
-- where [สถานภาพนักศึกษา] = 'dismissed'

-- update status
update UpdateStudentStatus_20250226 set [สถานภาพนักศึกษา] = 'dismissed' where [รหัสนักศึกษา] = '6580880'

-- update information firstname middle name and lastname
-- update UpdateStudentStatus_20250226
--     set [ชื่อ(ภาษาไทย)] = 'Edrick Dean'
--     ,[ชื่อกลาง(ภาษาไทย)] = ''
--     ,[สกุล(ภาษาไทย)] = 'WOODHEAD'
--     ,[ชื่อ(ภาษาอังกฤษ)] = 'Edrick Dean'
--     ,[ชื่อกลาง(ภาษาอังกฤษ)] = ''
--     ,[สกุล(ภาษาอังกฤษ)] = 'WOODHEAD'
-- where [รหัสนักศึกษา] = '6580561'
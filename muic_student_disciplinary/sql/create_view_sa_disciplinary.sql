USE [MUIC_StudentDisciplinary]
GO

create view sa_disciplinary as
SELECT 
    -- แปลงวันที่จาก "3 เม.ย. 2567" เป็น "2024-04-03"
    CONVERT(DATE, CONCAT(
        CONVERT(INT, SUBSTRING([Date], LEN([Date]) - 3, 4)) - 543, '-', -- ปี (พ.ศ. แปลงเป็น ค.ศ.)
        CASE 
            WHEN CHARINDEX('ม.ค.', [Date]) > 0 THEN '01'
            WHEN CHARINDEX('ก.พ.', [Date]) > 0 THEN '02'
            WHEN CHARINDEX('มี.ค.', [Date]) > 0 THEN '03'
            WHEN CHARINDEX('เม.ย.', [Date]) > 0 THEN '04'
            WHEN CHARINDEX('พ.ค.', [Date]) > 0 THEN '05'
            WHEN CHARINDEX('มิ.ย.', [Date]) > 0 THEN '06'
            WHEN CHARINDEX('ก.ค.', [Date]) > 0 THEN '07'
            WHEN CHARINDEX('ส.ค.', [Date]) > 0 THEN '08'
            WHEN CHARINDEX('ก.ย.', [Date]) > 0 THEN '09'
            WHEN CHARINDEX('ต.ค.', [Date]) > 0 THEN '10'
            WHEN CHARINDEX('พ.ย.', [Date]) > 0 THEN '11'
            WHEN CHARINDEX('ธ.ค.', [Date]) > 0 THEN '12'
        END, '-',
        RIGHT('0' + SUBSTRING([Date], 1, CHARINDEX(' ', [Date]) - 1), 2) -- วัน
    )) AS Date,
    [Time],
    LEFT([Student ID], 2) AS StudentYear,
    [Student ID],
    CASE	
        WHEN Gender = 'M' THEN 'Mr.'
        WHEN Gender = 'F' THEN 'Ms.'
    END as 'Title'
    ,[Gender]
    ,CONCAT('Y', TRIM(SUBSTRING([Academic Year], 1, CHARINDEX('-', [Academic Year]) - 1)), 'T1') AS Trimester
    ,SUBSTRING([Level_of_Issue], 1, CHARINDEX(' ', [Level_of_Issue]) - 1) as Level
    ,[Type_of_Issue] as Type
    ,[Location]
    ,[Details]
FROM [dbo].[sa_disciplinary_20240520] sa

--ORDER BY Date
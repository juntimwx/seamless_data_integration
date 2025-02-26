USE [MUIC_StudentDisciplinary]
GO

create view sa_disciplinary as
SELECT 
    -- �ŧ�ѹ���ҡ "3 ��.�. 2567" �� "2024-04-03"
    CONVERT(DATE, CONCAT(
        CONVERT(INT, SUBSTRING([Date], LEN([Date]) - 3, 4)) - 543, '-', -- �� (�.�. �ŧ�� �.�.)
        CASE 
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '01'
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '02'
            WHEN CHARINDEX('��.�.', [Date]) > 0 THEN '03'
            WHEN CHARINDEX('��.�.', [Date]) > 0 THEN '04'
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '05'
            WHEN CHARINDEX('��.�.', [Date]) > 0 THEN '06'
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '07'
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '08'
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '09'
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '10'
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '11'
            WHEN CHARINDEX('�.�.', [Date]) > 0 THEN '12'
        END, '-',
        RIGHT('0' + SUBSTRING([Date], 1, CHARINDEX(' ', [Date]) - 1), 2) -- �ѹ
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
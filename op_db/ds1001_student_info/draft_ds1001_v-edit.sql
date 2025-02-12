SELECT 
    c.RegistrationCredit AS total_regis_credits
    ,rc.GradeName
    ,term.AcademicYear
    ,term.AcademicTerm
FROM [registration].[RegistrationCourses] AS rc
JOIN [dbo].[Courses]          AS c     ON c.id = rc.CourseId
JOIN [dbo].[Terms]            AS t     ON t.Id = rc.TermId
JOIN [student].[Students]     AS std   ON std.Id = rc.StudentId
JOIN [dbo].[Terms]            AS term  ON term.Id = rc.TermId
WHERE 
    rc.Status <> 'd'
    AND rc.GradeName NOT IN ('S','U')          -- ตัดเกรด S, U, W
    AND std.Code = '6280117'
    
    -- 1) ระบุชุดปี/เทอมที่ต้องการด้วย OR
    AND 
    (
        (term.AcademicYear = '2019' AND term.AcademicTerm IN ('1','2','3'))
        OR (term.AcademicYear = '2020' AND term.AcademicTerm IN ('1','2','3'))
        OR (term.AcademicYear = '2021' AND term.AcademicTerm IN ('1','2','3'))
		OR (term.AcademicYear = '2022' AND term.AcademicTerm IN ('1'))
        --OR (term.AcademicYear = '2024' AND term.AcademicTerm IN ('1'))
    )
    
    -- 2) กรณีให้เกรด F เฉพาะ 2024/1
    --    เขียนเป็น เงื่อนไข “ถ้าเป็น (2024,1) ให้เอา F ได้” OR “อย่างอื่นต้องไม่ใช่ F”
    AND 
    (
        (term.AcademicYear = '2022' AND term.AcademicTerm = '1' AND rc.GradeName IN ('F','w'))
        OR (rc.GradeName not in ('F','w'))
    )
    
ORDER BY 
    term.AcademicYear
    ,term.AcademicTerm;

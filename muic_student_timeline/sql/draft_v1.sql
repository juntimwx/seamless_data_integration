SELECT distinct
    std.Code AS student_id,
    registerCourse.Status AS register_status,
    term.AcademicYear AS academic_year,
    term.AcademicTerm AS academic_term,
    course.Code AS course_code,
    course.NameEn AS course_name,
--     courseGroup.Id AS courseGroup_id,
    courseGroup.NameEn AS course_group,
    courseGroupParent.NameEn AS course_group_level2,
--     courseGroupGrandParent.Id AS courseGroupGrandParent_id,
    courseGroupGrandParent.NameEn AS course_group_level3,
    major.major_name,
    major.division_name
FROM student.Students std
LEFT JOIN registration.RegistrationCourses registerCourse
    ON std.Id = registerCourse.StudentId
LEFT JOIN dbo.Terms term
    ON registerCourse.TermId = term.Id
LEFT JOIN dbo.Courses course
    ON registerCourse.CourseId = course.Id
-- สำหรับกลุ่มวิชา
INNER JOIN curriculum.CurriculumCourses curriculumCourse
    ON registerCourse.CourseId = curriculumCourse.CourseId
INNER JOIN curriculum.CourseGroups courseGroup
    ON curriculumCourse.CourseGroupId = courseGroup.Id
LEFT JOIN curriculum.CourseGroups courseGroupParent
    ON courseGroup.CourseGroupId = courseGroupParent.Id
LEFT JOIN curriculum.CourseGroups courseGroupGrandParent
    ON courseGroupParent.CourseGroupId = courseGroupGrandParent.Id
-- สำหรับ major และ division
LEFT JOIN dbo.StagingStudent stagingStudent
    ON std.Code = stagingStudent.studentCode
LEFT JOIN (
    SELECT
        curriculum.AbbreviationEn AS major_code,
        curriculum.NameEn AS major_name,
        faculty.ShortNameEn AS short_division_name,
        faculty.NameEn AS division_name
    FROM curriculum.Curriculums curriculum
    LEFT JOIN master.Faculties faculty
        ON faculty.Id = curriculum.FacultyId
) major
    ON SUBSTRING(stagingStudent.programCode, 1, 4) = major.major_code
WHERE
    std.StudentStatus IN ('s', 'la', 'ex')
    AND std.Code = '6681035'
    AND registerCourse.Status <> 'd'
ORDER BY
    student_id,
    academic_year,
    academic_term;

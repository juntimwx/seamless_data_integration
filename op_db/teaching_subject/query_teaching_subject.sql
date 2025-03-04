select
    term.AcademicYear
    ,term.AcademicTerm Semester
    ,N'ปริญญาตรี' [Degree Level (Thai)]
    ,'Bachelor' [Degree Level (English)]
    ,N'วิทยาลัยนานาชาติ' [Faculty (Thai)]
    ,'International College' [Faculty (English)]
    ,course.Code [Subject Code]
    ,course.NameTh [Subject Name (Thai)]
    ,course.NameEn [Subject Name (English)]
    ,course.Credit
    ,title.NameTh [Prefix (Thai)]
    ,instructor.FirstNameTh [First Name (Thai)]
    ,NULL [Middle Name (Thai)]
    ,instructor.LastNameTh [Last Name (Thai)]
    ,title.NameEn [Prefix (English)]
    ,instructor.FirstNameEn [First Name (English)]
    ,NULL [Middle Name (English)]
    ,instructor.LastNameEn [Last Name (English)]
    ,N'วิทยาลัยนานาชาติ' [Instructor Faculty (Thai)]
    ,'International College' [Instructor Faculty (English)]
    ,instructor.Email
    ,FORMAT(GETDATE(), 'yyyy-MM-dd HH:mm:ss') UpdatedAt
from dbo.InstructorSections instructorSec
join dbo.Instructors instructor on instructorSec.InstructorId = instructor.Id
join master.Titles title on instructor.TitleId = title.Id
join dbo.SectionDetails sectionDetail on instructorSec.SectionDetailId = sectionDetail.Id
join dbo.Sections section on sectionDetail.SectionId = section.Id
join dbo.Courses course on section.CourseId = course.Id
join dbo.Terms term on section.TermId = term.Id
order by AcademicYear, AcademicTerm
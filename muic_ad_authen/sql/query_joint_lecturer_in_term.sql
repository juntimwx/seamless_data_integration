SELECT DISTINCT mainInstructor.Code MainInstructorId,
	term.AcademicYear,
	term.AcademicTerm
	--course.Code,
	--course.NameEn 
FROM Sections section
LEFT JOIN dbo.Courses course ON section.CourseId = course.Id
LEFT JOIN dbo.Instructors mainInstructor ON section.MainInstructorId = mainInstructor.Id --level 1
LEFT JOIN dbo.Terms term ON section.TermId = term.Id --level 1
WHERE term.AcademicYear = 2024 AND term.AcademicTerm = 2 --AND s.ParentSectionId != ''
--AND mainInstructor.code = 'nahum'
--WHERE TermId > 137
--ORDER BY MainInstructorId 

UNION

SELECT DISTINCT sectionInstructor.Code sectionInstructor,
	term.AcademicYear,
	term.AcademicTerm
	--course.Code courseId,
	--course.NameEn nameCourse
FROM Sections section
LEFT JOIN dbo.Courses course ON section.CourseId = course.Id
LEFT JOIN dbo.SectionDetails sectionDetail ON section.Id = sectionDetail.SectionId --level 2
LEFT JOIN dbo.Instructors sectionInstructor ON sectionDetail.InstructorId = sectionInstructor.Id --level 2
LEFT JOIN dbo.Terms term ON section.TermId = term.Id --level 1
WHERE term.AcademicYear = 2024 AND term.AcademicTerm = 2 --AND s.ParentSectionId != ''
--AND sectionInstructor.code = 'nahum'
--WHERE TermId > 137
--ORDER BY MainInstructorId 

UNION

SELECT DISTINCT sectionSlotInstructor.Code sectionSlotInstructorId,
	term.AcademicYear,
	term.AcademicTerm
	--course.Code,
	--course.NameEn 
FROM Sections section
LEFT JOIN dbo.Courses course ON section.CourseId = course.Id
LEFT JOIN slot.SectionSlots sectionSlot ON section.Id = sectionSlot.SectionId --level 3
LEFT JOIN dbo.Instructors sectionSlotInstructor ON sectionSlot.InstructorId = sectionSlotInstructor.Id --level 3
LEFT JOIN dbo.Terms term ON section.TermId = term.Id --level 1
WHERE term.AcademicYear = 2024 AND term.AcademicTerm = 2 --AND s.ParentSectionId != ''
--AND sectionSlotInstructor.code = 'nahum'
--WHERE TermId > 137
--ORDER BY sectionSlotInstructorId
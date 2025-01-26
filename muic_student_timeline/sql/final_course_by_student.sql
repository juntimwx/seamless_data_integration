select std.Code student_id,
	term.AcademicYear academic_year,
	term.AcademicTerm academic_term,
	--curriculumVersion.NameEn version_name,
	courseGroup.courseGroupGrandParent_name,
	courseGroup.courseGroupParent_name,
	courseGroup.couseGroup_name,
	course.Code course_code,
	course.NameEn course_name
from student.Students std
inner join student.AdmissionInformations admissionInfo 
	ON std.Id = admissionInfo.StudentId

left join registration.RegistrationCourses registrationCourse 
	on std.Id = registrationCourse.StudentId
left join dbo.Terms term 
	on registrationCourse.TermId = term.Id
left join dbo.Courses course
	on registrationCourse.CourseId = course.Id

inner join curriculum.CurriculumVersions curriculumVersion
	on admissionInfo.CurriculumVersionId = curriculumVersion.Id
outer apply (
	select top 1 
	courseGroup.NameEn couseGroup_name, 
	courseGroupParent.NameEn courseGroupParent_name,
	courseGroupGrandParent.NameEn courseGroupGrandParent_name
	from curriculum.CurriculumCourses curriculumCourse
	left join curriculum.CourseGroups courseGroup
		on curriculumCourse.CourseGroupId = courseGroup.Id
	left join curriculum.CourseGroups courseGroupParent
		on courseGroupParent.Id = courseGroup.CourseGroupId
	left join curriculum.CourseGroups courseGroupGrandParent
		on courseGroupGrandParent.Id = courseGroupParent.CourseGroupId
	where curriculumCourse.CourseId = registrationCourse.CourseId
		and courseGroup.CurriculumVersionId = curriculumVersion.Id
) courseGroup
where registrationCourse.Status <> 'd'
	and std.Code = '6681035'
order by student_id, academic_year, academic_term, course_code
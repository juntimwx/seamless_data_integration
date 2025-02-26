select std.Code student_id,
	term.AcademicYear academic_year,
	term.AcademicTerm academic_term,
	--curriculumVersion.NameEn version_name,
	case when curriculum_structure.courseGroupGrandParent_name = 'Elective Courses' then 'Major Courses'
        when curriculum_structure.courseGroupGrandParent_name is not null then curriculum_structure.courseGroupGrandParent_name
	    else curriculum_structure.courseGroupParent_name
	end main_course_group,
    case when curriculum_structure.courseGroupGrandParent_name = 'Elective Courses' then curriculum_structure.courseGroupGrandParent_name
        when curriculum_structure.courseGroupGrandParent_name is null then curriculum_structure.couseGroup_name
        --when curriculum_structure.courseGroupParent_name is not null then curriculum_structure.courseGroupParent_name
        else curriculum_structure.courseGroupParent_name
    end course_group,
    case when curriculum_structure.courseGroupGrandParent_name = 'Elective Courses' then curriculum_structure.courseGroupParent_name
    end course_concentration,
    case when curriculum_structure.courseGroupGrandParent_name is null then null
        else curriculum_structure.couseGroup_name
    end course_ability,
	--curriculum_structure.courseGroupGrandParent_name,
	--curriculum_structure.courseGroupParent_name,
	--curriculum_structure.couseGroup_name,
	course.Code course_code,
	course.NameEn course_name,
	course.Credit
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
) curriculum_structure
where registrationCourse.Status <> 'd'
	and std.Code = '6681035'
--order by student_id, academic_year, academic_term, course_code
order by student_id, main_course_group, course_group, course_ability, academic_year, academic_term, course_code
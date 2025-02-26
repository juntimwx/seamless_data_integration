select std.Code student_id,
	-- term.AcademicYear academic_year,
	-- term.AcademicTerm academic_term,
	-- curriculumVersion.NameEn version_name,
	main_course_group,
    -- case when curriculum_structure.courseGroupGrandParent_name is null then curriculum_structure.couseGroup_name
    --     when curriculum_structure.courseGroupParent_name is not null then curriculum_structure.courseGroupParent_name
    --     else curriculum_structure.courseGroupParent_name
    -- end course_group,
    -- case when curriculum_structure.courseGroupGrandParent_name is null then null
    --     else curriculum_structure.couseGroup_name
    -- end course_track,
	--curriculum_structure.courseGroupParent_name,
	--curriculum_structure.couseGroup_name,
	--course.Code course_code,
	--course.NameEn course_name,
	--course.Credit


	SUM(course.Credit) total_credits,
    
    -- เงื่อนไขสำหรับ GenEd และ major
    -- case 
    --     when major.major_name = 'Intercultural Studies and Languages' then 38
    --     else null -- หรือค่าอื่นที่ต้องการเมื่อไม่ตรงเงื่อนไข
    -- end as general_education_course,
    -- case 
    --     when major.major_name = 'Intercultural Studies and Languages' then 100
    --     else null -- หรือค่าอื่นที่ต้องการเมื่อไม่ตรงเงื่อนไขs
    -- end as major_courses,
    -- case 
    --     when major.major_name = 'Intercultural Studies and Languages' then 20
    --     else null -- หรือค่าอื่นที่ต้องการเมื่อไม่ตรงเงื่อนไข
    -- end as i_design_elective,
    -- case 
    --     when major.major_name = 'Intercultural Studies and Languages' then 8
    --     else null -- หรือค่าอื่นที่ต้องการเมื่อไม่ตรงเงื่อนไข
    -- end as free_elective_course,

    -- เงื่อนไขสำหรับ GenEd และ major
    -- CASE 
    --     WHEN major.major_name = 'Intercultural Studies and Languages' THEN 38 - SUM(course.Credit)
    --     ELSE 0
    -- END AS remaining_general_education,
    case when major.major_name = 'Intercultural Studies and Languages' then (
        case 
            when main_course_group = 'General Education Courses' then 38
            when main_course_group = 'Major Courses' then 100
            else 0
        end
    ) else null
    end curriculum_structure_credit,
    case when major.major_name = 'Intercultural Studies and Languages' then (
        case 
            when main_course_group = 'General Education Courses' then 38 - SUM(course.Credit)
            when main_course_group = 'Major Courses' then 100 - SUM(course.Credit)
            else 0
        end
    ) else null
    end remaining_credit
    -- major.major_name
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
outer apply (
    select
        curriculum.AbbreviationEn major_code,
        curriculum.NameEn major_name,
        faculty.ShortNameEn short_division_name,
        faculty.NameEn division_name
    from dbo.StagingStudent stagingStudent
    left join curriculum.Curriculums curriculum
        on SUBSTRING(stagingStudent.programCode, 1, 4) = curriculum.AbbreviationEn
    left join master.Faculties faculty
        on faculty.Id = curriculum.FacultyId
    where std.Code = stagingStudent.studentCode
) major
outer apply (
    select case when curriculum_structure.courseGroupGrandParent_name = 'Elective Courses' then 'Major Courses'
        when curriculum_structure.courseGroupGrandParent_name is not null then curriculum_structure.courseGroupGrandParent_name
	    else curriculum_structure.courseGroupParent_name
	end main_course_group
) main_course_group
where registrationCourse.Status <> 'd'
	and std.Code = '6681035'
group by std.Code,
    -- term.AcademicYear,
    -- term.AcademicTerm,
    main_course_group,
    -- case when curriculum_structure.courseGroupGrandParent_name is null then curriculum_structure.couseGroup_name
    --     when curriculum_structure.courseGroupParent_name is not null then curriculum_structure.courseGroupParent_name
    --     else curriculum_structure.courseGroupParent_name
    -- end,
    major.major_name
--order by student_id, academic_year, academic_term, course_code
-- order by student_id, main_course_group, course_group, course_track, academic_year, academic_term, course_code
order by student_id, main_course_group
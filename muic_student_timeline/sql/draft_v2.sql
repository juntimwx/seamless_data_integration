select std.Code student_id,
    term.AcademicYear academic_year,
    term.AcademicTerm academic_term,
    course.Code,
    course.NameEn,
    case when curriculumStructure.courseGroupGrandParent_name = 'Elective Courses' then 'Major Courses'
        when curriculumStructure.courseGroupGrandParent_name is not null then curriculumStructure.courseGroupGrandParent_name
	    else curriculumStructure.courseGroupParent_name
	end main_course_group,
    case when curriculumStructure.courseGroupGrandParent_name = 'Elective Courses' then curriculumStructure.courseGroupGrandParent_name
        when curriculumStructure.courseGroupGrandParent_name is null then curriculumStructure.couseGroup_name
        --when curriculumStructure.courseGroupParent_name is not null then curriculumStructure.courseGroupParent_name
        else curriculumStructure.courseGroupParent_name
    end course_group,
    specialInformation.specialGroupNameEn
from student.Students std
-- นักศึกษาลงเรียนวิชาไหนบ้าง
left join registration.RegistrationCourses registrationCourse
	on std.Id = registrationCourse.StudentId
-- เอารายชื่อวิชาที่ลงทะเบียนมาแสดง -> ใน registrationCourse มี CourseId
left join dbo.Courses course
    on registrationCourse.CourseId = course.Id
-- เทอมที่นักศึกษาลงทะเบียน
left join dbo.Terms term
	on registrationCourse.TermId = term.Id

-- join ข้อมูลสำหรับ course group, special information
left join student.AdmissionInformations admissionInfo
	on std.Id = admissionInfo.StudentId
left join curriculum.CurriculumVersions curriculumVersion
	on admissionInfo.CurriculumVersionId = curriculumVersion.Id

-- ต้องการรู้ว่า อยู่ใน course group ใด
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
	where courseGroup.CurriculumVersionId = curriculumVersion.Id 
		and curriculumCourse.CourseId = registrationCourse.CourseId
) curriculumStructure

-- ต้องการรู้ว่า นักศึกษามี special information อะไรบ้าง
outer apply (
    select specialGroup.NameEn specialGroupNameEn
    from curriculum.CurriculumSpecializationGroups curriculumSpecialGroup 
    left join master.SpecializationGroups specialGroup on curriculumSpecialGroup.SpecializationGroupId = SpecialGroup.Id
    where curriculumSpecialGroup.CurriculumVersionId = curriculumVersion.Id
) specialInformation

-- เงื่อนไขคือ ไม่เอาวิชาที่นักศึกษา drop
-- นักศึกษาต้องอยู่ในปี 66-67 เท่านั้น เนื่องจากเป็น catalog คนละแบบ
-- ต้องการเฉพาะนักศึกษาที่กำลังศึกษา แลกเปลี่ยน และรักษาสภาพ
where registrationCourse.Status <> 'd'
    and std.Code LIKE '66%' or std.Code LIKE '67%'
    and std.StudentStatus in ('s','ex','la')
-- เรียงตามรหัสนักศึกษา, ปี และเทอมที่ลงทะเบียนเรียน
order by student_id, academic_year, academic_term

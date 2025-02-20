select  std.Code Code,
        title.NameEn as Title,
        std.FirstNameEn FirstNameEn,
        std.LastNameEn LastNameEn,
        case when std.Gender = 1 then 'male'
             when std.Gender = 2 then 'female'
             else 'not specified' end as Gender,
        case when nationality.NameEn = 'Myanmar' then 'Burmese'
             when nationality.NameEn = 'Myanmarian' then 'Burmese'
             when nationality.NameEn = 'Other' then 'Not Specified'
             when nationality.NameEn = 'TO_CONFIRM' then 'Not Specified'
             when nationality.NameEn = 'passed_all_required_courses' then 'Not Specified'
             else nationality.NameEn end as Nationality,
        residentType.NameEn as ResidentTypes,
        studentFeeType.NameEn as StudentFeeTypes,
        term.AcademicYear as AcademicYear,
        term.AcademicTerm as AcademicTerm,
        admissionType.NameTh as AdmissionType,
        case when admissionType.Id = 1 then 'Full-time' /* IC + Outbound*/
             when admissionType.Id = 2 then 'Exchange'  /*Inbound*/
             when admissionType.Id = 3 then 'Exchange'  /*Inbound*/
             when admissionType.Id = 4 then 'Exchange'  /*Inbound*/
             when admissionType.Id = 5 then 'Full-time' /* PC */
             when admissionType.Id = 6 then 'Full-time' /* PC */
             when admissionType.Id = 7 then 'Summer'
             else 'External' end as StudentType,
        case when std.StudentStatus = 'prc'	then 'passed_all_required_course'
             when std.StudentStatus = 'pa'	then 'passed_away'
             when std.StudentStatus = 'rs'	then 'resign'
             when std.StudentStatus = 'dm'	then 'dismissed'
             when std.StudentStatus = 's'	then 'studying'
             when std.StudentStatus = 'la'	then 'leave_of_absence'
             when std.StudentStatus = 'ex'	then 'exchange'
             when std.StudentStatus = 'g'	then 'graduated'
             when std.StudentStatus = 'np'	then 'no_report'
             when std.StudentStatus = 'd'	then 'deleted'
             when std.StudentStatus = 'b'	then 'blacklist'
             when std.StudentStatus = 'tr'	then 'transferred_to_other_university'
             when std.StudentStatus = 're'	then 'reenter'
             when std.StudentStatus = 'ra'	then 're_admission'
             else 'Unknown' end as StudentStatus,
--         case when std.StudentStatus = 'prc'	then 'Inactive'
--              when std.StudentStatus = 'pa'	then 'Inactive'
--              when std.StudentStatus = 'rs'	then 'Inactive'
--              when std.StudentStatus = 'dm'	then 'Inactive'
--              when std.StudentStatus = 's'	then 'Active'
--              when std.StudentStatus = 'la'	then 'Active'
--              when std.StudentStatus = 'ex'	then 'Active'
--              when std.StudentStatus = 'g'	then 'Inactive'
--              when std.StudentStatus = 'np'	then 'Inactive'
--              when std.StudentStatus = 'd'	then 'Inactive'
--              when std.StudentStatus = 'b'	then 'Inactive'
--              when std.StudentStatus = 'tr'	then 'Inactive'
--             --when std.StudentStatus = 're'	then 'reenter'
--             --when std.StudentStatus = 'ra'	then 're_admission'
--              else 'Unknown' end as student_status_2,
        SUBSTRING(stagingStudent.programCode,1,4) as major,
        major.NameEn as major_name,
        major.Division as division,
        major.DivisionName as division_name,
        case when std.IsActive = 'true' then '1'
            else '0' end as IsActive
from student.Students std
         left join master.Titles title on std.TitleId = title.Id
         left join master.Nationalities nationality on std.NationalityId = nationality.Id
         left join master.ResidentTypes residentType on std.ResidentTypeId = residentType.Id
         left join master.StudentFeeTypes studentFeeType on std.StudentFeeTypeId = studentFeeType.Id
         left join student.AdmissionInformations admissionInfo on std.Id = admissionInfo.StudentId
         left join dbo.Terms term on admissionInfo.AdmissionTermId = term.Id
         left join master.AdmissionTypes admissionType on admissionInfo.AdmissionTypeId = admissionType.Id
         left join dbo.StagingStudent stagingStudent on std.Code = stagingStudent.studentCode
         left join dbo.ALLMajor major on SUBSTRING(stagingStudent.programCode,1,4) = major.Major
where std.StudentStatus in ('dm','ex','g','la','np','prc','pa', 'rs','s')
    and term.AcademicYear >= '2016'
order by AcademicYear, AcademicTerm
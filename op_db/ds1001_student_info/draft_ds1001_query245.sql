select distinct
	'2567' ACADEMIC_YEAR
	,'2' SEMESTER
	,'00600' UNIV_ID
	,case when CitizenNumber is not null and CitizenNumber <> '' then CitizenNumber
	else Passport end CITIZEN_ID
	,std.Code STD_ID
	,case when std.TitleId = '12' then '004'
	when std.TitleId = '14' then '003'
	end PREFIX_NAME_ID
	,std.FirstNameTh STD_FNAME
	,std.MidNameTh STD_MNAME
	,std.LastNameTh STD_LNAME
	,UPPER(LEFT(std.FirstNameEn, 1)) + LOWER(SUBSTRING(std.FirstNameEn, 2, LEN(std.FirstNameEn))) STD_FNAME_EN
	,UPPER(LEFT(std.MidNameEn, 1)) + LOWER(SUBSTRING(std.MidNameEn, 2, LEN(std.MidNameEn))) STD_MNAME_EN
	,UPPER(LEFT(std.LastNameEn, 1)) + LOWER(SUBSTRING(std.LastNameEn, 2, LEN(std.LastNameEn))) STD_LNAME_EN
	,std.Gender GENDER_ID
	,CONVERT(varchar(10), DATEADD(YEAR, 543, std.BirthDate), 23) AS BIRTHDAY_TH
	,''SUB_DISTRICT_ID
	,case when nationality.NameEn = 'Thai' then 'TH'
		when nationality.NameEn = 'Indian' then 'IN'
		when nationality.NameEn = 'Myanmar' then 'MM'
		when nationality.NameEn = 'American' then 'US'
		when nationality.NameEn = 'Bangladeshi' then 'BD'
		when nationality.NameEn = 'Nepalese' then 'NP'
		when nationality.NameEn = 'Singaporean' then 'SG'
		when nationality.NameEn = 'Polish' then 'PL'
		when nationality.NameEn = 'Chinese' then 'CN'
		when nationality.NameEn = 'Russian' then 'RU'
		when nationality.NameEn = 'Bhutanese' then 'BT'
		when nationality.NameEn = 'Taiwanese' then 'TW'
		when nationality.NameEn = 'Sudanese' then 'SD'
		when nationality.NameEn = 'Korean' then 'KR'
		when nationality.NameEn = 'Canadian' then 'CA'
		when nationality.NameEn = 'Malaysian' then 'MY'
		when nationality.NameEn = 'Japanese' then 'JP'
		when nationality.NameEn = 'Cambodian' then 'KH'
		when nationality.NameEn = 'Spanish' then 'ES'
		when nationality.NameEn = 'South Korean' then 'KP'
		when nationality.NameEn = 'British' then 'GB'
		when nationality.NameEn = 'Filipino' then 'FI'
		when nationality.NameEn = 'Belgian' then 'BE'
		when nationality.NameEn = 'German' then 'DE'
		when nationality.NameEn = 'French' then 'FR'
		when nationality.NameEn = 'Zimbabwean' then 'ZW'
		when nationality.NameEn = 'Myanmarian' then 'MM'
		when nationality.NameEn = 'Swedish' then 'SE'
		when nationality.NameEn = 'Emirati' then 'AE'
		when nationality.NameEn = 'Norwegian' then 'NO'
		when nationality.NameEn = 'Dutch' then 'NL'
		when nationality.NameEn = 'Italian' then 'IT'
		when nationality.NameEn = 'Latvian' then 'LV'
		when nationality.NameEn = 'Indonesian' then 'ID'
		when nationality.NameEn = 'Gabonese' then 'GA'
		when nationality.NameEn = 'Swiss' then 'CH'
		when nationality.NameEn = 'New Zeland' then 'NZ'
		when nationality.NameEn = 'Guinean' then 'GN'
		when nationality.NameEn = 'Maldivian' then 'MV'
		when nationality.NameEn = 'Danish' then 'DK'
		when nationality.NameEn = 'Bruneian' then 'BN'
		when nationality.NameEn = 'Australian' then 'AU'
		when nationality.NameEn = 'Turkish' then 'TR'
		when nationality.NameEn = 'Pakistani' then 'PK'
		when nationality.NameEn = 'Malagasy' then 'MG'
		when nationality.NameEn = 'Vietnamese' then 'VN'
		when nationality.NameEn = 'Austrian' then 'AT'
		when nationality.NameEn = 'Salvadoran' then 'SV'
		when nationality.NameEn = 'Nigerian' then 'NG'
		when nationality.NameEn = 'Moroccan' then 'MA'
		when nationality.NameEn = 'Beninese' then 'BJ'
		when nationality.NameEn = 'Zambian' then 'ZM'
		when nationality.NameEn = 'Philippines' then 'PH'
		when nationality.NameEn = 'South African' then 'ZA'
		when nationality.NameEn = 'Ukrainian' then 'UA'
		when nationality.NameEn = 'Israeli' then 'IL'
		when nationality.NameEn = 'Irish' then 'IE'
		when nationality.NameEn = 'Laotian' then 'LA'
		else nationality.NameEn
	end NATIONALITY_ID
	,term.AcademicYear + 543 ADMIT_YEAR
	,'00137' FAC_ID
	,major_code
	,case when major_code = 'ICIR' then '25290061100177' --หลักสูตรศิลปศาสตรบัณฑิต สาขาวิชาความสัมพันธ์ระหว่างประเทศและกิจการทั่วโลก (หลักสูตรนานาชาติ)
		when major_code = 'ICBI' then '25520061103841' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์ชีวภาพ (หลักสูตรนานาชาติ) มหาวิทยาลัยมหิดล
		when major_code = 'ICBE' then '25500061102072' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาเศรษฐศาสตร์ธุรกิจ (หลักสูตรนานาชาติ)  
		when major_code = 'ICMF' then '25450061100862' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาการเงิน (หลักสูตรนานาชาติ) 
		when major_code = 'ICMI' then '25450061100783' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาธุรกิจระหว่างประเทศ (หลักสูตรนานาชาติ)
		when major_code = 'ICMK' then '25450061100772' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาการตลาด(หลักสูตรนานาชาติ)
		when major_code = 'ICCU' then '25570061103047' --หลักสูตรศิลปศาสตรบัณฑิต สาขาวิชาวัฒนธรรมนานาชาติศึกษาและภาษา (หลักสูตรนานาชาติ)
		when major_code = 'ICCS' then '25450061100895' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาการคอมพิวเตอร์ (หลักสูตรนานาชาติ)
		when major_code = 'ICMC' then '25580061100607' --หลักสูตรนิเทศศาสตรบัณฑิต สาขาวิชาสื่อและการสื่อสาร (หลักสูตรนานาชาติ)
		when major_code = 'ICAM' then '25520061103896' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาคณิตศาสตร์ประยุกต์ (หลักสูตรนานาชาติ)
		when major_code = 'ICCI' then '25510061100363' --หลักสูตรวิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ (หลักสูตรนานาชาติ)
		when major_code = 'ICTB' then '25510061103636' --หลักสูตรการจัดการบัณฑิต สาขาวิชาผู้ประกอบการด้านธุรกิจการเดินทางและธุรกิจบริการ (หลักสูตรนานาชาติ)
		when major_code = 'ICCD' then '25520061100735' --หลักสูตรศิลปกรรมศาสตรบัณฑิต สาขาวิชาการออกแบบนิเทศศิลป์ (หลักสูตรนานาชาติ) มหาวิทยาลัยมหิดล
		when major_code = 'ICCT' then '25630064005206' --หลักสูตรศิลปศาสตรและวิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีสร้างสรรค์ (หลักสูตรนานาชาติ)
		when major_code = 'ICPY' then '25520061103828' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาฟิสิกส์ (หลักสูตรนานาชาติ)
		when major_code = 'ICCH' then '25500061102421' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาเคมี (หลักสูตรนานาชาติ)
		when major_code = 'ICFS' then '25350061100163' --หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์และเทคโนโลยีการอาหาร (หลักสูตรนานาชาติ)
		when major_code = 'ICTH' then '25661924002001' --หลักสูตรบริหารธุรกิจบัณฑิต สาขาวิชาการจัดการการท่องเที่ยวและบริการนานาชาติ (หลักสูตรนานาชาติ)
	end CURR_ID
	,'1' STUDY_TYPE_ID
	,'1' STUDY_TIME_ID
	,'1' STUDY_REG_ID
	,'1' CLASS
	,'0' GRAD_STATUS_ID
	,case when std.StudentStatus = 's' then '1'
		when std.StudentStatus = 'la' then '2'
		when std.StudentStatus = 'dm' then '3'
		when std.StudentStatus = 'rs' then '4'
		else std.StudentStatus end STD_STATUS_ID
	,case when std.StudentStatus = 'rs' then N'ลาออก'
		else '-' end TERMINATE_STUDY_CAUSE
	,case when gpa is null then '0.00'
		else gpa end GPA
	,case when gpax is null then '0.00'
		else gpax end GPAX
	,case when term_credit.total_regis_credits is null then 0
		else term_credit.total_regis_credits
	end NUM_CREDIT
	,case when total_credit.total_regis_credits is null then 0
		else total_credit.total_regis_credits
	end ACC_CREDIT
	,'0' DEFORM_ID
	,'0' FUND_STATUS_ID
	,'-' FUND_NAME
	,'-' TALENT_ID
	,case when std.Passport is null then '-'
		when std.Passport = '' then '-'
		else std.Passport
	end PASSPORT_NUMBER
	,'-' PASSPORT_STARTDATE
	,'-' PASSPORT_ENDDATE
	,'1' DEGREE_NUM
from student.Students std
join student.StudentAddresses stdAddress on std.Id = stdAddress.StudentId
join master.Titles title on std.TitleId = title.Id
join master.Nationalities nationality on std.NationalityId = nationality.Id
join student.AdmissionInformations admissionInfo on admissionInfo.StudentId = std.Id
join master.AdmissionTypes admissionType on admissionType.Id = admissionInfo.AdmissionTypeId
join dbo.Terms term on term.Id = admissionInfo.AdmissionTermId
join dbo.StagingStudent stagingStudent on std.Code = stagingStudent.studentCode
join(
    select
        curriculum.AbbreviationEn as major_code,
        curriculum.NameEn as major_name,
        faculty.ShortNameEn as short_division_name,
        faculty.NameEn as division_name
    from curriculum.Curriculums curriculum
    left join master.Faculties faculty on faculty.Id = curriculum.FacultyId
) major on SUBSTRING(stagingStudent.programCode, 1, 4) = major.major_code
outer apply (
	SELECT 
		StudentId,
		AVG(
			CASE 
				WHEN registrationCourse.GradeName = 'A'  THEN 4.00
				WHEN registrationCourse.GradeName = 'B'  THEN 3.00
				WHEN registrationCourse.GradeName = 'B+' THEN 3.50
				WHEN registrationCourse.GradeName = 'C'  THEN 2.00
				WHEN registrationCourse.GradeName = 'C+' THEN 2.50
				WHEN registrationCourse.GradeName = 'D'  THEN 1.00
				WHEN registrationCourse.GradeName = 'D+' THEN 1.50
				WHEN registrationCourse.GradeName = 'F'  THEN 0.00
			END
		) AS gpa
	FROM registration.RegistrationCourses registrationCourse
	WHERE registrationCourse.TermId = '151'
	  AND registrationCourse.GradeName NOT IN ('AU', 'I', 'S', 'T', 'U', 'W', 'X', 't', 'O')
	  AND registrationCourse.StudentId = std.Id
	GROUP BY StudentId
) gpa
outer apply (
	SELECT 
		StudentId,
		AVG(
			CASE 
				WHEN registrationCourse.GradeName = 'A'  THEN 4.00
				WHEN registrationCourse.GradeName = 'B'  THEN 3.00
				WHEN registrationCourse.GradeName = 'B+' THEN 3.50
				WHEN registrationCourse.GradeName = 'C'  THEN 2.00
				WHEN registrationCourse.GradeName = 'C+' THEN 2.50
				WHEN registrationCourse.GradeName = 'D'  THEN 1.00
				WHEN registrationCourse.GradeName = 'D+' THEN 1.50
				WHEN registrationCourse.GradeName = 'F'  THEN 0.00
			END
		) AS gpax
	FROM registration.RegistrationCourses registrationCourse
	WHERE registrationCourse.GradeName NOT IN ('AU', 'I', 'S', 'T', 'U', 'W', 'X', 't', 'O')
	  AND registrationCourse.StudentId = std.Id
	GROUP BY StudentId
) gpax
outer apply(
	select sum(c.RegistrationCredit) as total_regis_credits
	from  [registration].[RegistrationCourses] rc
		join [dbo].[Courses] c on c.id = rc.CourseId
		join [dbo].[Terms] t on t.Id = rc.TermId
	where rc.Status <> 'd'
		and t.AcademicYear = '2024' and t.AcademicTerm = '2'
		and std.Id = rc.StudentId
) term_credit
outer apply(
	select sum(c.RegistrationCredit) as total_regis_credits
	from  [registration].[RegistrationCourses] rc
		join [dbo].[Courses] c on c.id = rc.CourseId
		join [dbo].[Terms] t on t.Id = rc.TermId
	where rc.Status <> 'd'
		--and t.AcademicYear = '2024' and t.AcademicTerm = '2'
		and std.Id = rc.StudentId
) total_credit
where 
	--std.Code >= '6081175' and 
	--std.Code >= '6780921' and 
	--std.Code < '9000000'
	std.Code = '6280117'
	and std.StudentStatus in ('s','la','ex','np','rs','dm')
	--std.Code = '6681035'
	and admissionType.NameEn not in ('Exchange inbound','Visiting direct application','Visiting agency')
order by std.Code

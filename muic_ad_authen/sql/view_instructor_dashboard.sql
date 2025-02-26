SELECT	DISTINCT di.Id AS ID, 
		di.Code , 
		mt.NameEn AS Title, 
		di.FirstNameEn, 
		di.LastNameEn, 
		di.FirstNameTh, 
		di.LastNameTh,
	CASE	WHEN	di.Gender = 1 THEN 'Male'
			WHEN	di.Gender = 2 THEN 'Female'
			ELSE	'Not Specified' END AS 'Gender',
	mn.NameEn AS Nationality,
	mit.NameEn AS InstructorTypes,
	dt.AcademicYear , dt.AcademicTerm,
	--dc.Code, 
	--dc.NameEn AS NameCourse,
	di.IsActive
FROM dbo.Instructors di 
LEFT JOIN master.Nationalities mn ON di.NationalityId = mn.Id 
LEFT JOIN master.Titles mt ON di.TitleId = mt.Id 
INNER JOIN dbo.InstructorWorkStatuses miws ON di.Id = miws.InstructorId 
INNER JOIN master.InstructorTypes mit ON miws.InstructorTypeId  = mit.Id 
LEFT JOIN dbo.InstructorSections dis ON di.Id = dis.InstructorId 
LEFT JOIN dbo.SectionDetails dsd ON dis.SectionDetailId = dsd.Id 
LEFT JOIN dbo.Sections ds ON dsd.SectionId = ds.Id 
--LEFT JOIN dbo.Courses dc ON ds.CourseId = dc.Id 
LEFT JOIN dbo.Terms dt ON ds.TermId = dt.Id 
WHERE dt.AcademicYear = 2024 AND dt.AcademicTerm = 2
--WHERE di.Code = 'athapol'
ORDER BY di.Id, dt.AcademicYear DESC;

select std.Code, specialGroup.NameTh from student.Students std
left join student.CurriculumInformations curriculumInformation
	on std.Id = curriculumInformation.StudentId
left join student.SpecializationGroupInformations SpecializationGroupInformation
	on curriculumInformation.Id = SpecializationGroupInformation.CurriculumInformationId
left join master.SpecializationGroups specialGroup
	on SpecializationGroupInformation.SpecializationGroupId = specialGroup.Id
where std.Code = '6480922'
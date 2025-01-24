# ExportADData.ps1

# กำหนดไฟล์ที่ต้องการบันทึกข้อมูลผู้ใช้และ DC
$outputUserFile = "C:\Users\juntima.nuc\Desktop\script_clean_ad\ExportedADUsers.csv"
$outputDCFile = "C:\Users\juntima.nuc\Desktop\script_clean_ad\ExportedADDomainControllers.csv"

# Export ข้อมูลผู้ใช้
Get-ADUser -Filter * -Property UserPrincipalName, EmailAddress, Department, DistinguishedName | 
    Select-Object Name, SamAccountName, UserPrincipalName, EmailAddress, Department, DistinguishedName | 
    Export-Csv -Path $outputUserFile -NoTypeInformation -Encoding UTF8

Write-Host "Exported AD user data to $outputUserFile"

# Export ข้อมูล Domain Controllers
Get-ADDomainController -Filter * | 
    Select-Object Name, IPv4Address, OperatingSystem, Site, DistinguishedName | 
    Export-Csv -Path $outputDCFile -NoTypeInformation -Encoding UTF8

Write-Host "Exported AD Domain Controllers data to $outputDCFile"

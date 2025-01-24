Import-Module ActiveDirectory

# กำหนดชื่อโดเมนใหม่
$newDomain = "muic.io"

# กำหนดชื่อโดเมนเดิม
$oldDomain = "sky.local"

# แจ้งให้ผู้ใช้ทราบเกี่ยวกับการรับข้อมูลรับรอง
Write-Host "กรุณาใส่ข้อมูลรับรองที่มีสิทธิ์เข้าร่วมโดเมน $newDomain" -ForegroundColor Cyan
$newDomainCred = Get-Credential

# ตัวเลือกเพิ่มเติม: หากต้องการระบุชื่อผู้ใช้และรหัสผ่านสำหรับการออกจากโดเมนเดิม
# Write-Host "กรุณาใส่ข้อมูลรับรองที่มีสิทธิ์ลบคอมพิวเตอร์ออกจากโดเมน $oldDomain" -ForegroundColor Cyan
# $removeDomainCred = Get-Credential

try {
    # ตรวจสอบว่าเครื่องอยู่ในโดเมนปัจจุบันหรือไม่
    $currentDomain = (Get-WmiObject Win32_ComputerSystem).Domain
    if ($currentDomain -ieq $oldDomain) {
        Write-Output "เครื่องอยู่ในโดเมน $oldDomain จะดำเนินการเปลี่ยนเป็นโดเมน $newDomain"
    }
    else {
        Write-Output "เครื่องไม่อยู่ในโดเมน $oldDomain ปัจจุบันอยู่ในโดเมน $currentDomain"
        # คุณสามารถเลือกที่จะหยุดสคริปต์หรือดำเนินการต่อได้ตามต้องการ
    }

    # เข้าร่วมโดเมนใหม่ (ขั้นตอนนี้จะลบเครื่องออกจากโดเมนเดิมโดยอัตโนมัติ)
    Add-Computer -DomainName $newDomain -Credential $newDomainCred -Force -Restart
}
catch {
    Write-Error "เกิดข้อผิดพลาดในการเข้าร่วมโดเมนใหม่: $_"
}
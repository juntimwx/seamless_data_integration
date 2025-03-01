### 1. **บีบอัดโฟลเดอร์ `data`**

บีบอัดโฟลเดอร์ก่อนเข้ารหัส:

```bash
tar -czf data.tar.gz data/
```

- ไฟล์ที่ได้คือ `data.tar.gz`

---

### 2. **เข้ารหัสไฟล์บีบอัด**

ใช้ GPG เพื่อเข้ารหัสไฟล์ `data.tar.gz`:

```bash
gpg --output data.tar.gz.gpg --encrypt --recipient "juntima.nuc@mahidol.edu" data.tar.gz
```

**คำอธิบายคำสั่ง:**

- `-output data.tar.gz.gpg` คือไฟล์ที่เข้ารหัสแล้ว
- `-encrypt` ใช้คำสั่งเข้ารหัส
- `-recipient "juntima.nuc@mahidol.edu"` กำหนดอีเมลของ Public Key ที่จะใช้เข้ารหัส

**ตรวจสอบไฟล์ที่เข้ารหัสเสร็จ:**

```bash
ls -lh data.tar.gz.gpg
```

---

### 3. **เพิ่มไฟล์เข้ารหัสลงใน Git**

ลบไฟล์ต้นฉบับ (`dataset` และ `dataset.tar.gz`) เพื่อความปลอดภัย:

```bash
rm -rf data data.tar.gz
```

เพิ่มไฟล์เข้ารหัสลงใน Git:

```bash
git add data.tar.gz.gpg
git commit -m "Add encrypted dataset"
git push
```

---

### 4. **ถอดรหัสไฟล์**

เมื่อคุณหรือทีมงานดึงไฟล์ `data.tar.gz.gpg` จาก Git และต้องการถอดรหัส:

```bash
gpg --output data.tar.gz --decrypt data.tar.gz.gpg
```

แตกไฟล์บีบอัด:

```bash
tar -xzf data.tar.gz
```

---

### 5. **ตั้งค่า `.gitignore`**

เพื่อป้องกันการอัปโหลดไฟล์ต้นฉบับที่ยังไม่ได้เข้ารหัส:

```bash
echo "data/" >> .gitignore
echo "data.tar.gz" >> .gitignore
```

---
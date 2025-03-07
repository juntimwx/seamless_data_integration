function logEmailsToSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const threads = GmailApp.search('is:unread'); // ดึงเฉพาะอีเมลที่ยังไม่ได้อ่าน

  threads.forEach(thread => {
    const messages = thread.getMessages();
    messages.forEach(message => {
      const subject = message.getSubject();
      const body = message.getPlainBody();
      const sender = message.getFrom();
      const date = message.getDate();
      
      // บันทึกข้อมูลอีเมลลง Google Sheets เสมอ
      sheet.appendRow([date, sender, subject, body]);

      // ตรวจสอบเฉพาะอีเมลที่มีคำว่า "Paper Misfeed" หรือ "Toner Empty"
      if (subject.includes('Paper Misfeed') || subject.includes('Toner Empty') || 
          body.includes('Paper Misfeed') || body.includes('Toner Empty')) {

        // ส่งการแจ้งเตือนไปที่ Microsoft Teams
        sendToMSTeams(sender, subject, body, date);
      }

      // ตั้งค่าให้อีเมลนี้เป็นอีเมลที่อ่านแล้ว
      message.markRead();
      
      // ลบอีเมลออกไปหลังจากประมวลผลเสร็จ
      message.moveToTrash();
    });
  });
}

function checkForSpecialContent(body) {
  if (body.includes('10.27.24.101')) {
    return 'สถานที่ : ห้อง B114 กลุ่มงานอทิตยาทร (AB) CSGN57911';
  } else if (body.includes('10.27.24.106')) {
    return 'สถานที่ : งานวิเทศสัมพันธ์ (Chiba office) CSGN57984';
  } else if (body.includes('10.27.24.131')) {
    return 'สถานที่ : สำนักงาน IT อาคารอทิตยาทร ข้างห้อง A225 CSGN57918';
  } else if (body.includes('10.27.24.102')) {
    return 'สถานที่ : ห้องปฏิบัติการคอมพิวเตอร์ ชั้น 2 เครื่องสี CSGN57997';
  } else if (body.includes('10.27.24.103')) {
    return 'สถานที่ : ห้องปฏิบัติการคอมพิวเตอร์ ชั้น 2 เครื่องสี CSGN57985 ';
  } else if (body.includes('10.27.24.104')) {
    return 'สถานที่ : ห้องปฏิบัติการคอมพิวเตอร์ ชั้น 2 เครื่องขาวดำ CTEN45021';
  } else if (body.includes('10.27.24.105')) {
    return 'สถานที่ : ห้องปฏิบัติการคอมพิวเตอร์ ชั้น 2 เครื่องขาวดำ CTEN44978';
  } else if (body.includes('10.27.24.107')) {
    return 'สถานที่ : Co-Working Space ชั้น 3 CSGN57915';
  } else if (body.includes('10.27.24.108')) {
    return 'สถานที่ : Office of Academic Affair (OAA) ชั้น 3 CSGN57929';
  } else if (body.includes('10.27.24.109')) {
    return 'สถานที่ : Office of Academic Affair (OAA) ชั้น 3 CSGN57953';
  } else if (body.includes('10.27.24.110')) {
    return 'สถานที่ : หน่วยสนับสนุนวิชาการบัณฑิตศึกษา (MBA) ชั้น 4 CSGN57927';
  } else if (body.includes('10.27.24.111')) {
    return 'สถานที่ : กลุ่มสาขาวิชาการจัดการท่องเที่ยว (THM) ชั้น 4 CSGN57919';
  } else if (body.includes('10.27.24.112')) {
    return 'สถานที่ : กลุ่มสาขาวิชาบริหารธุรกิจ (BA) ชั้น 4 ZoneA CSGN57956';
  } else if (body.includes('10.27.24.113')) {
    return 'สถานที่ : กลุ่มสาขาวิชาบริหารธุรกิจ (BA) ชั้น 4 ZoneD CSFN50069';
  } else if (body.includes('10.27.24.114')) {
    return 'สถานที่ : กลุ่มสาขาวิชาจิตรกรรมและศิลปกรรม (FAA) ชั้น 6 CSFN50062';
  } else if (body.includes('10.27.24.115')) {
    return 'สถานที่ : งานกิจการนักศึกษา (SA) CSFN50063';
  } else if (body.includes('10.27.24.116')) {
    return 'สถานที่ : ห้อง 1103 งานปฏิบัติการและสิ่งแวดล้อม (OE อาคาร 1) CSFN50067';
  } else if (body.includes('10.27.24.117')) {
    return 'สถานที่ : ห้อง 2102 งานศูนย์เตรียมความพร้อม (PC) (สำนักงาน) CSFN50071';
  } else if (body.includes('10.27.24.118')) {
    return 'สถานที่ : ห้อง 1110 หน่วยสื่อสารองค์กร ชั้น 1 CSFN50072';
  } else if (body.includes('10.27.24.119')) {
    return 'สถานที่ : ห้อง 2120 กลุ่มวิชาสังคมศาสตร์ ชั้น 1 CSFN50073';
  } else if (body.includes('10.27.24.120')) {
    return 'สถานที่ : ห้อง 2203 กลุ่มสาขาวิชามนุษยศาสตร์และภาษาต่างประเทศ (HLD) CSFN50074';
  } else if (body.includes('10.27.24.121')) {
    return 'สถานที่ : ห้อง 2208 กลุ่มสาขาวิชามนุษยศาสตร์และภาษาต่างประเทศ (HLD) CSFN50075';
  } else if (body.includes('10.27.24.122')) {
    return 'สถานที่ : ห้อง 1211 ศูนย์เตรียมความพร้อม (PC) ห้องพักครู CTEN44981';
  } else if (body.includes('10.27.24.123')) {
    return 'สถานที่ : ห้อง 1203 งานการเงิน บัญชี และพัสดุ ชั้น 2 CSFN50076';
  } else if (body.includes('10.27.24.124')) {
    return 'สถานที่ : ห้อง 1307 หน่วยพัฒนาและผลิตสื่อ ชั้น 3 CSFN50081';
  } else if (body.includes('10.27.24.125')) {
    return 'สถานที่ : ห้อง 2306 กลุ่มสาขาวิชามนุษยศาสตร์และภาษาต่างประเทศ (HLD) CSFN50084';
  } else if (body.includes('10.27.24.126')) {
    return 'สถานที่ : สำนักงาน HR ชั้น 6 CSGN57931';
  } else if (body.includes('10.27.24.127')) {
    return 'สถานที่ : ห้อง 3402 สำนักงาน EdTech (อาคาร 3) ชั้น 4 CSGN57959';
  } else if (body.includes('10.27.24.128')) {
    return 'สถานที่ : ห้องปฏิบัติการคอมพิวเตอร์ ชั้น 5 เครื่องขาวดำ CTEN45012';
  } else if (body.includes('10.27.24.129')) {
    return 'สถานที่ : ห้องปฏิบัติการคอมพิวเตอร์ ชั้น 5 เครื่องขาวดำ CTEN45033';
  } else if (body.includes('10.27.24.130')) {
    return 'สถานที่ : ห้องปฏิบัติการคอมพิวเตอร์ ชั้น 5 เครื่องสี CSGN57965';
  } else if (body.includes('10.27.24.132')) {
    return 'สถานที่ : ห้อง 1515 สำนักงาน IT (อาคาร 1) ชั้น 5 CSGN57996';
  } else if (body.includes('10.27.24.133')) {
    return 'สถานที่ : ห้อง 1603 กลุ่มสาขาวิทยาศาสตร์ ชั้น 6 CSGN58005';
  } else {
    return '';
  }
}



function sendToMSTeams(sender, subject, body, date) {
  const webhookUrl = 'webhook_ms_team'; // ใส่ URL Webhook ของคุณ

  // ตรวจสอบเนื้อหาอีเมลสำหรับข้อความพิเศษ
  const location = checkForSpecialContent(body);
  const formattedDate = Utilities.formatDate(date, Session.getScriptTimeZone(), "dd-MM-yyyy HH:mm");

  const payload = {
    "type": "MessageCard",
    "context": "http://schema.org/extensions",
    "summary": "New Email Notification",
    "sections": [
      {
        "activityTitle": "📣 Printer แจ้งเตือนใหม่",
        "facts": [
          {
            "name": "Date วันที่: ",
            "value": formattedDate
          },
          {
            "name": "From ผู้ส่ง: ",
            "value": sender
          },
          {
            "name": "Topic หัวข้อ: ",
            "value": subject
          },
          {
            "name": "สถานที่: ",
            "value": location
          },
          {
            "name": "Message: ",
            "value": body
          }
        ],
        "markdown": true
      }
    ]
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload)
  };

  UrlFetchApp.fetch(webhookUrl, options);
}

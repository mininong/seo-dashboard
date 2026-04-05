import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ==========================================
# 1. ตั้งค่าเว็บไซต์ของคุณที่นี่
# หากเป็น Domain property ให้เขียน 'sc-domain:yourwebsite.com'
# หากเป็น URL Prefix ให้เขียน 'https://www.yourwebsite.com/'
# ==========================================
SITE_URL = 'https://www.bangkokeyehospital.com/'

def main():
    # โหลด Credentials จาก GitHub Secrets
    creds_json = os.environ.get("GSC_CREDENTIALS")
    if not creds_json:
        raise ValueError("No GSC_CREDENTIALS found in environment variables")
    
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    # สร้าง Service สำหรับเรียก GSC API
    service = build('searchconsole', 'v1', credentials=credentials)
    
    # คำนวณวันที่ (ย้อนหลัง 90 วัน)
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    end_date = (today - datetime.timedelta(days=2)).strftime('%Y-%m-%d') # ข้อมูล GSC มักจะดีเลย์ 2 วัน
    
    # Request ข้อมูลภาพรวม (KPIs)
    request_kpi = {
        'startDate': start_date,
        'endDate': end_date,
    }
    
    response_kpi = service.searchanalytics().query(siteUrl=SITE_URL, body=request_kpi).execute()
    
    # ดึงค่ามาจัดรูปแบบ
    try:
        totals = response_kpi['rows'][0]
        clicks = totals['clicks']
        impressions = totals['impressions']
        position = round(totals['position'], 1)
    except KeyError:
        clicks, impressions, position = 0, 0, 0

    # สร้างโครงสร้างข้อมูล JSON เพื่อส่งให้หน้าเว็บ (อ้างอิงโครงสร้างจาก index.html เดิม)
    # *หมายเหตุ: เพื่อความเรียบง่ายของโค้ดตัวอย่างนี้ ส่วนของกราฟจะใช้ข้อมูลจำลองไปก่อน 
    # คุณสามารถเขียน Python เพิ่มเติมเพื่อ query แบบแบ่งรายวัน (dimensions: ['date']) ได้ในอนาคต
    output_data = {
        "kpi": {
            "clicks": f"{clicks:,}",
            "impressions": f"{impressions:,}",
            "position": str(position)
        },
        "charts": {
            "clicksTrend": [99, 87, 120, 115, 90, int(clicks/2), int(clicks)], # ตัวเลขจำลองประยุกต์
            "positionTrend": [7.2, 6.7, 6.6, 6.7, 7.1, 6.2, float(position)],
            "devices": [250, 85, 10]
        },
        "lastUpdated": today.strftime('%Y-%m-%d %H:%M')
    }
    
    # บันทึกเป็นไฟล์ data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print("Successfully fetched data and saved to data.json")

if __name__ == '__main__':
    main()

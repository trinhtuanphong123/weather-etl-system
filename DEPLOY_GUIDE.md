# 🚀 Weather ETL System - Deployment Guide

## 📋 Quy trình triển khai

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: GitHub Setup (15 phút)                       │
│  → Push code lên GitHub                                 │
│  → Kiểm tra CI/CD pass                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: AWS Setup (30 phút)                          │
│  → Tạo S3 Bucket                                        │
│  → Tạo IAM Roles                                        │
│  → Launch EC2                                           │
│  → Tạo Lambda Functions                                 │
│  → Setup EventBridge Schedule                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: Testing (10 phút)                            │
│  → Test thủ công                                        │
│  → Kiểm tra S3 data                                     │
└─────────────────────────────────────────────────────────┘
```

---

## PHASE 1: GitHub Setup (Code Repository)

### Bước 1.1: Chuẩn bị Repository

```bash
# Tạo repository mới trên GitHub
# Tên: weather-etl-system
# Visibility: Public hoặc Private

# Clone về máy
git clone https://github.com/YOUR_USERNAME/weather-etl-system.git
cd weather-etl-system
```

### Bước 1.2: Copy các files vào repository

**Cấu trúc cần tạo:**

```
weather-etl-system/
├── .github/workflows/ci-test.yml
├── aws/
│   ├── ec2_user_data.template.sh
│   ├── lambda_start_ec2.py
│   └── lambda_stop_ec2.py
├── app.py
├── requirements.txt
├── Dockerfile
├── test_app.py
├── .gitignore
├── .env.example
└── README.md
```

### Bước 1.3: Push lên GitHub

```bash
git add .
git commit -m "Initial commit: Weather ETL System"
git push origin main
```

### Bước 1.4: Kiểm tra GitHub Actions

1. Vào repository trên GitHub
2. Click tab **Actions**
3. Xem workflow "CI Pipeline - Weather ETL"
4. **Đợi cho đến khi thấy ✅ (Pass)**

**Nếu PASS:**
- ✅ Code không có lỗi
- ✅ Tests pass
- ✅ Docker build thành công
- ✅ Sẵn sàng deploy lên AWS

**Nếu FAIL:**
- ❌ Xem logs để fix lỗi
- ❌ Commit và push lại

---

## PHASE 2: AWS Setup

### Bước 2.1: Lấy API Key

**Visual Crossing Weather API:**

1. Truy cập: https://www.visualcrossing.com/weather-api
2. Sign up (miễn phí)
3. Copy API key (dạng: `pk.abc123xyz456...`)
4. **Lưu lại để dùng sau**

---

### Bước 2.2: Tạo S3 Bucket

**AWS Console → S3 → Create bucket:**

```yaml
Bucket name: weather-data-bucket-YOUR_NAME
  (VD: weather-data-bucket-john)
  
Region: Asia Pacific (Singapore) ap-southeast-1

Block Public Access: ✓ Block all public access

Bucket Versioning: Disabled

Encryption: Enable (SSE-S3)
```

**Click "Create bucket"**

**Tạo folder structure:**

Vào bucket vừa tạo → **Create folder** → Tạo 4 folders:

```
- raw/weather/
- raw/electricity/
- processed/
- models/
```

**✅ Lưu lại:** `weather-data-bucket-YOUR_NAME`

---

### Bước 2.3: Tạo IAM Roles

#### **Role 1: EC2-Weather-ETL-Role**

**IAM Console → Roles → Create role:**

```yaml
Trusted entity type: AWS service
Use case: EC2
```

**Click "Next"**

**Attach policies:**
- ✓ `AmazonS3FullAccess`
- ✓ `CloudWatchAgentServerPolicy`

**Click "Next"**

```yaml
Role name: EC2-Weather-ETL-Role
Description: Role for EC2 to access S3 and CloudWatch
```

**Click "Create role"**

#### **Role 2: Lambda-EC2-Control-Role**

**Create role:**

```yaml
Trusted entity type: AWS service
Use case: Lambda
```

**Attach policies:**
- ✓ `AmazonEC2FullAccess`
- ✓ `CloudWatchLogsFullAccess`

```yaml
Role name: Lambda-EC2-Control-Role
Description: Role for Lambda to start/stop EC2
```

**Click "Create role"**

---

### Bước 2.4: Launch EC2 Instance

**EC2 Console → Launch Instance:**

#### **Step 1: Name and OS**

```yaml
Name: weather-etl-instance
Application and OS Images (AMI): Ubuntu Server 22.04 LTS
Architecture: 64-bit (x86)
```

#### **Step 2: Instance type**

```yaml
Instance type: t2.micro (Free tier) hoặc t3.small
```

#### **Step 3: Key pair**

```yaml
Create new key pair:
  Name: weather-etl-key
  Type: RSA
  Format: .pem
```

**→ Download file `weather-etl-key.pem` và lưu an toàn**

```bash
# Trên máy local, set quyền cho key
chmod 400 weather-etl-key.pem
```

#### **Step 4: Network settings**

**Create security group:**

```yaml
Security group name: weather-etl-sg

Inbound rules:
  Rule 1:
    Type: SSH
    Port: 22
    Source: My IP
  
  Rule 2:
    Type: HTTP
    Port: 80
    Source: 0.0.0.0/0 (Anywhere)
```

#### **Step 5: Storage**

```yaml
Size: 8-20 GB
Volume type: gp3
```

#### **Step 6: Advanced details**

**IAM instance profile:**
```yaml
Select: EC2-Weather-ETL-Role
```

**User data:**

1. Mở file `aws/ec2_user_data.template.sh` từ GitHub repo
2. Copy toàn bộ nội dung
3. **THAY THẾ 3 giá trị:**

```bash
# Line ~48: Thay GitHub username
GITHUB_USERNAME="john_doe"  # ← Thay YOUR_USERNAME

# Line ~84-85: Thay API key và bucket name
WEATHER_API_KEY=pk.abc123xyz456...  # ← Thay YOUR_VISUAL_CROSSING_API_KEY
S3_BUCKET_NAME=weather-data-bucket-john  # ← Thay YOUR_S3_BUCKET_NAME
```

4. Paste vào ô **User data**

#### **Step 7: Launch**

**Click "Launch instance"**

**Đợi ~3-5 phút** để instance khởi động

#### **Step 8: Lấy thông tin Instance**

```yaml
Instance ID: i-0abc123def456789  # ← LƯU LẠI cho Lambda
Public IPv4: 54.123.45.67        # ← Để truy cập web
```

#### **Step 9: Kiểm tra deployment**

**Option A: SSH vào EC2**

```bash
ssh -i weather-etl-key.pem ubuntu@54.123.45.67

# Xem logs deployment
sudo tail -f /var/log/user-data.log

# Kiểm tra Docker
sudo docker ps

# Xem logs app
sudo docker logs weather-app
```

**Option B: Truy cập web**

```
http://54.123.45.67
```

Bạn sẽ thấy: **"🌤️ Weather Data Collection System"**

**✅ Nếu thấy web → EC2 deployment thành công!**

---

### Bước 2.5: Tạo Lambda Functions

#### **Lambda 1: Start EC2**

**Lambda Console → Create function:**

```yaml
Function name: StartWeatherEC2
Runtime: Python 3.12
Architecture: x86_64
Execution role: Use an existing role
  → Select: Lambda-EC2-Control-Role
```

**Click "Create function"**

**Code:**

1. Mở file `aws/lambda_start_ec2.py` từ GitHub
2. Copy toàn bộ code
3. Paste vào Lambda code editor
4. **Click "Deploy"**

**Configuration → Environment variables:**

```yaml
Key: INSTANCE_ID
Value: i-0abc123def456789  # ← Instance ID từ bước 2.4
```

**Configuration → General configuration → Edit:**

```yaml
Timeout: 30 seconds
```

**Click "Save"**

**Test:**

1. Tab "Test" → "Test"
2. Xem response:
   ```json
   {
     "statusCode": 200,
     "body": "Successfully started EC2: ['i-0abc123...']"
   }
   ```
3. Kiểm tra EC2 Console → Instance state = "running"

#### **Lambda 2: Stop EC2**

**Làm tương tự:**

```yaml
Function name: StopWeatherEC2
Runtime: Python 3.12
Role: Lambda-EC2-Control-Role
Code: Copy từ aws/lambda_stop_ec2.py
Environment: INSTANCE_ID = i-0abc123...
Timeout: 30 seconds
```

**Test → EC2 sẽ stop**

---

### Bước 2.6: Setup EventBridge Schedule

#### **Schedule 1: Start EC2 mỗi sáng**

1. Lambda **StartWeatherEC2** → **Add trigger**
2. **EventBridge (CloudWatch Events)**
3. **Create new rule:**

```yaml
Rule name: StartWeatherEC2Daily
Rule type: Schedule expression
Schedule: cron(0 1 * * ? *)
```

**Giải thích:** `1:00 UTC = 8:00 AM Vietnam time`

4. **Add**

#### **Schedule 2: Stop EC2 mỗi tối**

1. Lambda **StopWeatherEC2** → **Add trigger**
2. **Create new rule:**

```yaml
Rule name: StopWeatherEC2Daily
Rule type: Schedule expression
Schedule: cron(0 11 * * ? *)
```

**Giải thích:** `11:00 UTC = 6:00 PM Vietnam time`

3. **Add**

---

## PHASE 3: Testing

### Test 1: Manual Start/Stop

```bash
# Start EC2
Lambda Console → StartWeatherEC2 → Test
→ Check EC2 state = running

# Truy cập web
http://[EC2_PUBLIC_IP]

# Stop EC2
Lambda Console → StopWeatherEC2 → Test
→ Check EC2 state = stopped
```

### Test 2: Thu thập dữ liệu

1. **Start EC2** (nếu đang stopped)
2. Truy cập `http://[EC2_PUBLIC_IP]`
3. Click **"🚀 Bắt đầu thu thập dữ liệu"**
4. Đợi ~1 phút
5. **Kiểm tra S3:**

```bash
# AWS Console → S3 → Bucket → raw/weather/
# Sẽ có file: weather_raw_20241219_103045.csv

# S3 → processed/
# Sẽ có file: weather_processed_20241219_103045.csv
```

### Test 3: Scheduled Automation

- Đợi đến 8:00 AM → EC2 tự động start
- Login và chạy thu thập dữ liệu
- Đợi đến 6:00 PM → EC2 tự động stop

---

## ✅ Deployment Checklist

### GitHub:
- [ ] Code pushed lên GitHub
- [ ] GitHub Actions CI pass ✅

### AWS:
- [ ] S3 bucket created với folders
- [ ] IAM roles created (EC2 + Lambda)
- [ ] EC2 instance launched
- [ ] Web accessible: `http://[IP]`
- [ ] Lambda Start/Stop created
- [ ] EventBridge schedules set

### Testing:
- [ ] Manual start/stop works
- [ ] Data collection works
- [ ] S3 có files mới
- [ ] Scheduled automation set

---

## 🔒 Security Notes

**Files KHÔNG push lên GitHub:**
- ✅ `.env` (blocked by .gitignore)
- ✅ `aws/ec2_user_data.sh` (blocked by .gitignore)
- ✅ `*.pem` key files (blocked by .gitignore)

**API Key chỉ xuất hiện:**
- ✅ Trong User Data khi launch EC2 (paste 1 lần)
- ✅ Trong file `.env` trên EC2 (được tạo tự động)

**Không bao giờ:**
- ❌ Commit API key vào Git
- ❌ Share key files công khai
- ❌ Hardcode credentials trong code

---

## 💰 Chi phí ước tính

| Service | Usage | Cost/month |
|---------|-------|------------|
| EC2 t2.micro | 10h/day × 30 days | $3.48 |
| S3 Storage | 1 GB | $0.023 |
| Lambda | 60 invocations | Free |
| Data Transfer | Minimal | ~$0.10 |
| **TOTAL** | | **~$3.60/month** |

---

## 🆘 Troubleshooting

### EC2 không truy cập được web

```bash
# 1. Check Security Group port 80
# 2. SSH vào EC2:
ssh -i weather-etl-key.pem ubuntu@[IP]

# 3. Check Docker:
sudo docker ps
sudo docker logs weather-app

# 4. Check User Data logs:
sudo tail -f /var/log/user-data.log
```

### Không upload S3 được

```bash
# 1. Check IAM role của EC2
# 2. Check bucket name trong .env
# 3. Check logs:
sudo docker logs weather-app
```

### Lambda không start EC2

```bash
# 1. Check Instance ID đúng chưa
# 2. Check Lambda role có EC2FullAccess
# 3. Check CloudWatch Logs:
CloudWatch → Logs → /aws/lambda/StartWeatherEC2
```

---

## 📞 Support

- GitHub Issues: Create issue trong repo
- Visual Crossing API: https://www.visualcrossing.com/support
- AWS Documentation: https://docs.aws.amazon.com

---

## 🎉 Hoàn thành!

Hệ thống của bạn đã sẵn sàng tự động:
- ✅ Start EC2 lúc 8h sáng
- ✅ Thu thập dữ liệu thời tiết
- ✅ Upload lên S3
- ✅ Stop EC2 lúc 6h chiều
- ✅ Tiết kiệm chi phí tối đa
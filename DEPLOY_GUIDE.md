# 🚀 Hướng dẫn Triển khai Weather ETL System

## 📋 Checklist chuẩn bị

- [ ] Tài khoản AWS
- [ ] Visual Crossing API Key (free tier: https://www.visualcrossing.com/weather-api)
- [ ] GitHub account
- [ ] AWS CLI đã cài đặt (optional)

---

## Bước 1: Tạo GitHub Repository

### 1.1. Tạo repo mới trên GitHub

```bash
# Tạo repo tên: weather-etl-system
# Visibility: Public hoặc Private
```

### 1.2. Clone và push code

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/weather-etl-system.git
cd weather-etl-system

# Copy tất cả files từ artifacts vào thư mục này
# - app.py
# - requirements.txt
# - Dockerfile
# - .gitignore
# - .env.example
# - test_app.py
# - README.md
# - .github/workflows/ci-test.yaml

# Push code
git add .
git commit -m "Initial commit: Weather ETL System"
git push origin main
```

### 1.3. Kiểm tra GitHub Actions

- Vào tab **Actions** trên GitHub
- Kiểm tra CI pipeline có chạy và pass không
- Nếu PASS → Tiếp tục bước 2

---

## Bước 2: Tạo S3 Bucket

### 2.1. Tạo bucket qua AWS Console

1. **Vào S3 Console** → Click **"Create bucket"**

2. **Cấu hình:**
   ```
   Bucket name: weather-data-bucket-YOUR_NAME
   Region: Asia Pacific (Singapore) ap-southeast-1
   
   Block Public Access: ✓ Block all public access
   
   Versioning: Disabled (hoặc Enable nếu muốn)
   
   Encryption: Enable (Server-side encryption với S3 managed keys)
   ```

3. **Create bucket**

### 2.2. Tạo folder structure

Vào bucket vừa tạo → **Create folder**:

```
- raw/weather/
- raw/electricity/
- processed/
- models/
```

### 2.3. Lưu bucket name

```
Bucket name: weather-data-bucket-YOUR_NAME
```

---

## Bước 3: Tạo IAM Roles

### 3.1. Role cho EC2

1. **IAM Console** → **Roles** → **Create role**

2. **Trusted entity type:** AWS service

3. **Use case:** EC2

4. **Permissions policies:**
   - ✓ `AmazonS3FullAccess`
   - ✓ `CloudWatchAgentServerPolicy`

5. **Role name:** `EC2-Weather-ETL-Role`

6. **Create role**

### 3.2. Role cho Lambda

1. **Create role** → **AWS service** → **Lambda**

2. **Permissions policies:**
   - ✓ `AmazonEC2FullAccess`
   - ✓ `CloudWatchLogsFullAccess`

3. **Role name:** `Lambda-EC2-Control-Role`

4. **Create role**

---

## Bước 4: Launch EC2 Instance

### 4.1. EC2 Console → Launch Instance

**Basic settings:**
```
Name: weather-etl-instance
AMI: Ubuntu Server 22.04 LTS
Architecture: 64-bit (x86)
Instance type: t2.micro (free tier) hoặc t3.small
```

**Key pair:**
```
Create new key pair
Name: weather-etl-key
Type: RSA
Format: .pem
→ Download và lưu file
```

**Network settings:**
```
Create security group
Name: weather-etl-sg

Inbound rules:
- Type: SSH, Port: 22, Source: My IP
- Type: HTTP, Port: 80, Source: 0.0.0.0/0
```

**Configure storage:**
```
Size: 8-20 GB
Type: gp3
```

**Advanced details:**

**IAM instance profile:**
```
Select: EC2-Weather-ETL-Role
```

**User data:**

```bash
#!/bin/bash
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=== Weather ETL Deployment Started at $(date) ==="

# Update system
apt update -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Install Git and AWS CLI
apt install -y git awscli

# Clone repository
cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/YOUR_USERNAME/weather-etl-system.git app
cd app

# Create .env file
cat > .env << 'EOF'
WEATHER_API_KEY=YOUR_VISUAL_CROSSING_API_KEY_HERE
S3_BUCKET_NAME=weather-data-bucket-YOUR_NAME
AWS_REGION=ap-southeast-1
EOF

chown ubuntu:ubuntu .env

# Build and run Docker
docker build -t weather-app .
docker run -d -p 80:8501 --name weather-app --env-file .env weather-app

echo "=== Deployment Completed at $(date) ==="
docker ps
```

**⚠️ QUAN TRỌNG:** Thay thế:
- `YOUR_USERNAME` → GitHub username của bạn
- `YOUR_VISUAL_CROSSING_API_KEY_HERE` → API key thật
- `weather-data-bucket-YOUR_NAME` → Tên S3 bucket của bạn

### 4.2. Launch instance

- Click **"Launch instance"**
- Đợi ~2-3 phút để instance khởi động

### 4.3. Lấy thông tin instance

```
Instance ID: i-0xxxxxxxxxxxxx (lưu lại cho Lambda)
Public IPv4: xx.xx.xx.xx (để truy cập web)
```

### 4.4. Kiểm tra deployment

**SSH vào EC2:**
```bash
chmod 400 weather-etl-key.pem
ssh -i weather-etl-key.pem ubuntu@[PUBLIC_IP]

# Xem logs
sudo tail -f /var/log/user-data.log

# Xem Docker
sudo docker ps
sudo docker logs weather-app
```

**Truy cập web:**
```
http://[PUBLIC_IP]
```

Bạn sẽ thấy giao diện Weather Data Collection System!

---

## Bước 5: Tạo Lambda Functions

### 5.1. Lambda START EC2

1. **Lambda Console** → **Create function**

2. **Cấu hình:**
   ```
   Function name: StartWeatherEC2
   Runtime: Python 3.12
   Architecture: x86_64
   Execution role: Use existing role → Lambda-EC2-Control-Role
   ```

3. **Create function**

4. **Code:** Copy code từ artifact `lambda_start_ec2.py`

5. **Deploy**

6. **Configuration → Environment variables:**
   ```
   Key: INSTANCE_ID
   Value: i-0xxxxxxxxxxxxx (Instance ID của bạn)
   ```

7. **Configuration → General configuration:**
   ```
   Timeout: 30 seconds
   ```

8. **Test:**
   - Tab Test → Configure test event
   - Event name: TestStart
   - Click Test
   - Xem EC2 có start không

### 5.2. Lambda STOP EC2

**Làm tương tự như Lambda START:**

```
Function name: StopWeatherEC2
Runtime: Python 3.12
Role: Lambda-EC2-Control-Role
Code: Copy từ lambda_stop_ec2.py
Environment variable: INSTANCE_ID = i-0xxxxx
Timeout: 30 seconds
```

**Test:**
- Click Test → EC2 sẽ stop

---

## Bước 6: Schedule với EventBridge

### 6.1. Schedule START EC2 (8h sáng)

1. Vào Lambda function **StartWeatherEC2**

2. **Add trigger** → **EventBridge (CloudWatch Events)**

3. **Create new rule:**
   ```
   Rule name: StartWeatherEC2Daily
   Rule type: Schedule expression
   Schedule: cron(0 1 * * ? *)
   ```
   (1:00 UTC = 8:00 AM Vietnam)

4. **Add**

### 6.2. Schedule STOP EC2 (6h chiều)

1. Vào Lambda function **StopWeatherEC2**

2. **Add trigger** → **EventBridge**

3. **Create new rule:**
   ```
   Rule name: StopWeatherEC2Daily
   Rule type: Schedule expression
   Schedule: cron(0 11 * * ? *)
   ```
   (11:00 UTC = 6:00 PM Vietnam)

4. **Add**

---

## Bước 7: Testing End-to-End

### 7.1. Test thủ công

1. **Start EC2:**
   - Vào Lambda `StartWeatherEC2` → Click Test
   - Vào EC2 Console → Kiểm tra instance state = running
   - Đợi 2-3 phút

2. **Truy cập web:**
   ```
   http://[EC2_PUBLIC_IP]
   ```

3. **Thu thập dữ liệu:**
   - Click nút "🚀 Bắt đầu thu thập dữ liệu"
   - Xem progress bar
   - Đợi ~30-60 giây

4. **Kiểm tra S3:**
   - Vào S3 bucket
   - Kiểm tra folder `raw/weather/` có file mới không
   - Kiểm tra folder `processed/` có file mới không

5. **Stop EC2:**
   - Vào Lambda `StopWeatherEC2` → Click Test
   - Kiểm tra EC2 state = stopped

### 7.2. Test tự động (với schedule)

- Đợi đến 8h sáng → EC2 tự start
- Truy cập web và thu thập dữ liệu
- Đợi đến 6h chiều → EC2 tự stop

---

## Bước 8: Monitoring & Logs

### 8.1. CloudWatch Logs

**Lambda Logs:**
```
CloudWatch → Logs → Log groups
- /aws/lambda/StartWeatherEC2
- /aws/lambda/StopWeatherEC2
```

**EC2 Logs:**
```bash
ssh -i weather-etl-key.pem ubuntu@[PUBLIC_IP]
sudo docker logs -f weather-app
sudo tail -f /var/log/user-data.log
```

### 8.2. S3 Monitoring

```bash
# List files
aws s3 ls s3://weather-data-bucket-YOUR_NAME/raw/weather/
aws s3 ls s3://weather-data-bucket-YOUR_NAME/processed/

# Download file
aws s3 cp s3://weather-data-bucket-YOUR_NAME/raw/weather/weather_raw_20241217.csv .
```

---

## 🎯 Kiểm tra hoàn thành

- [ ] GitHub repo có code đầy đủ
- [ ] GitHub Actions pass
- [ ] S3 bucket đã tạo với folder structure
- [ ] IAM roles đã tạo
- [ ] EC2 instance chạy được
- [ ] Truy cập web qua HTTP OK
- [ ] Lambda Start/Stop hoạt động
- [ ] EventBridge schedule đã set
- [ ] Dữ liệu upload lên S3 thành công

---

## 💰 Chi phí ước tính

| Service | Usage | Cost/month |
|---------|-------|------------|
| EC2 t2.micro | 10h/day × 30 days | $3.48 |
| S3 Storage | 1 GB | $0.023 |
| Lambda | 60 invocations/month | Free |
| Data Transfer | Minimal | ~$0.10 |
| **TOTAL** | | **~$3.60/month** |

---

## 🔧 Troubleshooting

### EC2 không start được
```bash
# Kiểm tra Lambda logs
# Kiểm tra IAM role có đủ quyền không
# Kiểm tra Instance ID đúng chưa
```

### Không truy cập được web
```bash
# Kiểm tra Security Group port 80
# Kiểm tra Docker container: docker ps
# Kiểm tra logs: docker logs weather-app
```

### Không upload được S3
```bash
# Kiểm tra IAM role của EC2
# Kiểm tra bucket name trong .env
# Kiểm tra logs: docker logs weather-app
```

### API lỗi
```bash
# Kiểm tra API key trong .env
# Kiểm tra rate limit (500 requests/day)
# Đợi 24h nếu đã hết quota
```

---

## 📚 Resources

- Visual Crossing API: https://www.visualcrossing.com/weather-api
- AWS EC2: https://aws.amazon.com/ec2/
- AWS Lambda: https://aws.amazon.com/lambda/
- AWS S3: https://aws.amazon.com/s3/

---

## 🎉 Hoàn thành!

Hệ thống của bạn đã sẵn sàng:
- ✅ Tự động bật EC2 mỗi sáng
- ✅ Thu thập dữ liệu thời tiết
- ✅ Upload lên S3
- ✅ Tự động tắt EC2 mỗi tối
- ✅ Tiết kiệm chi phí tối đa
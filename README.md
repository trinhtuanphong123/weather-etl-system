# 🌤️ Weather Data Collection System

Hệ thống tự động thu thập dữ liệu thời tiết từ Visual Crossing API và lưu trữ vào AWS S3.

## 📋 Tính năng

- ✅ Thu thập dữ liệu thời tiết theo giờ cho 7 ngày gần nhất
- ✅ Xử lý và làm sạch dữ liệu
- ✅ Upload tự động lên S3 (raw + processed)
- ✅ Web UI để giám sát quá trình
- ✅ EC2 tự động bật/tắt
- ✅ CI/CD với GitHub Actions

## 🏗️ Kiến trúc hệ thống

```
Lambda Start → EC2 khởi động → Docker chạy app
                ↓
          Lấy dữ liệu API
                ↓
          Xử lý dữ liệu
                ↓
          Upload lên S3
                ↓
Lambda Stop → EC2 tắt → Tiết kiệm chi phí
```

## 📁 Cấu trúc S3 Bucket

```
weather-data-bucket/
├── raw/
│   └── weather/
│       └── weather_raw_20241217_103000.csv
├── processed/
│   └── weather_processed_20241217_103000.csv
├── models/
│   └── (future ML models)
└── electricity/
    └── (future electricity data)
```

## 🚀 Deployment

### Bước 1: Tạo S3 Bucket

```bash
# Tạo bucket
aws s3 mb s3://weather-data-bucket --region ap-southeast-1

# Tạo folder structure
aws s3api put-object --bucket weather-data-bucket --key raw/weather/
aws s3api put-object --bucket weather-data-bucket --key raw/electricity/
aws s3api put-object --bucket weather-data-bucket --key processed/
aws s3api put-object --bucket weather-data-bucket --key models/
```

### Bước 2: Tạo IAM Role cho EC2

**Policies cần thiết:**
- `AmazonS3FullAccess` - Upload/Download S3
- `CloudWatchAgentServerPolicy` - Logs

### Bước 3: Launch EC2 với User Data

**Instance configuration:**
- AMI: Ubuntu Server 22.04 LTS
- Instance type: t2.micro hoặc t3.small
- Security Group: Port 80 (HTTP)
- IAM Role: EC2-S3-Role

**User Data Script:**

```bash
#!/bin/bash
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=== Starting deployment at $(date) ==="

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker

# Install Git and AWS CLI
apt update
apt install -y git awscli

# Clone repository
cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/YOUR_USERNAME/weather-etl-system.git app
cd app

# Create .env file
cat > .env << EOF
WEATHER_API_KEY=${WEATHER_API_KEY}
S3_BUCKET_NAME=weather-data-bucket
AWS_REGION=ap-southeast-1
EOF

# Build and run Docker
docker build -t weather-app .
docker run -d -p 80:8501 \
  --env-file .env \
  --name weather-app \
  weather-app

echo "=== Deployment completed at $(date) ==="
docker ps
```

### Bước 4: Tạo Lambda Functions

**Lambda Start EC2:**
```python
import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    instance_id = 'i-xxxxx'  # Thay bằng EC2 Instance ID
    ec2.start_instances(InstanceIds=[instance_id])
    return {'statusCode': 200, 'body': 'EC2 Started'}
```

**Lambda Stop EC2:**
```python
import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    instance_id = 'i-xxxxx'
    ec2.stop_instances(InstanceIds=[instance_id])
    return {'statusCode': 200, 'body': 'EC2 Stopped'}
```

### Bước 5: Schedule với EventBridge

**Start EC2 (8h sáng mỗi ngày):**
```
cron(0 1 * * ? *)
```

**Stop EC2 (6h chiều mỗi ngày):**
```
cron(0 11 * * ? *)
```

## 🧪 Testing

```bash
# Local testing
pip install -r requirements.txt
pytest test_app.py -v

# Docker testing
docker build -t weather-app .
docker run -p 8501:8501 --env-file .env weather-app
```

## 📊 Monitoring

**Truy cập Web UI:**
```
http://[EC2_PUBLIC_IP]
```

**Xem logs:**
```bash
# EC2 logs
ssh ubuntu@[EC2_IP]
sudo docker logs -f weather-app

# CloudWatch logs
aws logs tail /aws/lambda/StartEC2 --follow
```

## 🔒 Security

- ✅ API keys trong environment variables (không commit)
- ✅ IAM roles thay vì hardcode credentials
- ✅ S3 bucket private, chỉ EC2 truy cập được
- ✅ Security Group chỉ mở port cần thiết

## 💰 Chi phí ước tính

- EC2 t2.micro: $0.0116/hour × 10 hours/day = $3.5/month
- Lambda: Free tier (1M requests/month)
- S3: $0.023/GB/month (ước tính 1GB) = $0.023/month

**Tổng: ~$3.5/month**

## 📝 Environment Variables

```bash
WEATHER_API_KEY=xxx          # Visual Crossing API key
S3_BUCKET_NAME=xxx           # S3 bucket name
AWS_REGION=ap-southeast-1    # AWS region
```

## 🛠️ Troubleshooting

**Lỗi API:**
- Kiểm tra API key
- Kiểm tra rate limit (500 requests/day free tier)

**Lỗi S3:**
- Kiểm tra IAM role của EC2
- Kiểm tra bucket name và region

**Lỗi Docker:**
- Xem logs: `docker logs weather-app`
- Restart: `docker restart weather-app`

## 📚 API Documentation

Visual Crossing Weather API:
- Docs: https://www.visualcrossing.com/resources/documentation/weather-api/
- Free tier: 500 requests/day
- Data: Hourly weather data with 5+ years history

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License
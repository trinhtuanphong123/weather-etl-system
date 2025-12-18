# 🌤️ Weather Data Collection & ETL System

[![CI Pipeline](https://github.com/YOUR_USERNAME/weather-etl-system/actions/workflows/ci-test.yml/badge.svg)](https://github.com/YOUR_USERNAME/weather-etl-system/actions)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Hệ thống tự động thu thập dữ liệu thời tiết từ Visual Crossing API, xử lý và lưu trữ vào AWS S3 với khả năng tự động bật/tắt EC2 để tiết kiệm chi phí.

## 📋 Tính năng

- ✅ **Thu thập dữ liệu tự động** - Lấy dữ liệu thời tiết theo giờ cho 7 ngày gần nhất
- ✅ **Xử lý dữ liệu** - Làm sạch, xử lý missing values, tạo features
- ✅ **Upload tự động lên S3** - Lưu trữ cả raw data và processed data
- ✅ **Web UI** - Streamlit dashboard để giám sát quá trình
- ✅ **EC2 tự động bật/tắt** - Lambda + EventBridge tiết kiệm chi phí
- ✅ **CI/CD** - GitHub Actions tự động test code

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐
│  GitHub Repo    │
│  (Code + CI/CD) │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│         AWS Infrastructure              │
│                                         │
│  ┌──────────┐      ┌──────────┐       │
│  │ Lambda   │──────│   EC2    │       │
│  │  Start   │      │  Ubuntu  │       │
│  └──────────┘      │  Docker  │       │
│                    └────┬─────┘       │
│  ┌──────────┐          │             │
│  │ Lambda   │          ↓             │
│  │  Stop    │      ┌──────────┐     │
│  └──────────┘      │    S3    │     │
│                    │  Bucket  │     │
│  ┌──────────┐      └──────────┘     │
│  │EventBridge                       │
│  │ Schedule │                       │
│  └──────────┘                       │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Bước 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/weather-etl-system.git
cd weather-etl-system
```

### Bước 2: Cài đặt Dependencies (Local testing)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Bước 3: Tạo file `.env`

```bash
cp .env.example .env
# Sửa .env với API key và config thật
```

### Bước 4: Run Tests

```bash
pytest test_app.py -v
```

### Bước 5: Deploy lên AWS

Xem hướng dẫn chi tiết trong **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

## 📁 Cấu trúc Project

```
weather-etl-system/
├── .github/
│   └── workflows/
│       └── ci-test.yml          # GitHub Actions CI/CD
│
├── aws/
│   ├── ec2_user_data.template.sh   # EC2 User Data template
│   ├── lambda_start_ec2.py         # Lambda start function
│   └── lambda_stop_ec2.py          # Lambda stop function
│
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── test_app.py                  # Unit tests
│
├── .gitignore                   # Git ignore (bảo mật)
├── .env.example                 # Environment variables template
│
├── README.md                    # This file
└── DEPLOYMENT_GUIDE.md          # Hướng dẫn deploy chi tiết
```

## 📊 Cấu trúc S3 Bucket

```
weather-data-bucket/
├── raw/
│   └── weather/
│       └── weather_raw_20241219_103045.csv
├── processed/
│   └── weather_processed_20241219_103045.csv
├── models/
│   └── (ML models - tương lai)
└── raw/electricity/
    └── (electricity data - tương lai)
```

## 🔑 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `WEATHER_API_KEY` | Visual Crossing API key | `pk.abc123xyz456...` |
| `S3_BUCKET_NAME` | AWS S3 bucket name | `weather-data-bucket-john` |
| `AWS_REGION` | AWS region | `ap-southeast-1` |

**Lấy API key miễn phí:** https://www.visualcrossing.com/weather-api

## 🧪 Testing

### Run unit tests

```bash
pytest test_app.py -v
```

### Test Docker build

```bash
docker build -t weather-app .
docker run -p 8501:8501 --env-file .env weather-app
```

### Access local app

```
http://localhost:8501
```

## 📈 Monitoring

### View EC2 logs

```bash
ssh -i weather-etl-key.pem ubuntu@[EC2_IP]
sudo docker logs -f weather-app
```

### View Lambda logs

```bash
# AWS Console → CloudWatch → Logs
/aws/lambda/StartWeatherEC2
/aws/lambda/StopWeatherEC2
```

### Check S3 data

```bash
aws s3 ls s3://weather-data-bucket-YOUR_NAME/raw/weather/
aws s3 ls s3://weather-data-bucket-YOUR_NAME/processed/
```

## 🔒 Security

- ✅ API keys trong environment variables (không commit)
- ✅ IAM roles thay vì hardcode AWS credentials
- ✅ S3 bucket private access only
- ✅ Security Group restricted ports
- ✅ `.gitignore` block sensitive files

**Files KHÔNG được push lên GitHub:**
- `.env` (API keys)
- `aws/ec2_user_data.sh` (với credentials thật)
- `*.pem` (SSH keys)

## 💰 Chi phí

| Service | Usage | Cost/month |
|---------|-------|------------|
| EC2 t2.micro | 10 hours/day | $3.48 |
| S3 Storage | ~1 GB | $0.023 |
| Lambda | 60 invocations | Free tier |
| Data Transfer | Minimal | ~$0.10 |
| **TOTAL** | | **~$3.60/month** |

## 📅 Schedule

- **8:00 AM (Vietnam):** EC2 tự động start
- **6:00 PM (Vietnam):** EC2 tự động stop
- **Runtime:** ~10 hours/day = Tiết kiệm 58% chi phí!

## 🛠️ Tech Stack

- **Backend:** Python 3.9, Streamlit
- **Data Processing:** Pandas, Requests
- **Infrastructure:** AWS EC2, S3, Lambda, EventBridge
- **Containerization:** Docker
- **CI/CD:** GitHub Actions
- **API:** Visual Crossing Weather API

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Hướng dẫn deploy chi tiết
- [API Documentation](https://www.visualcrossing.com/resources/documentation/weather-api/) - Visual Crossing API

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)

## 🙏 Acknowledgments

- Visual Crossing Weather API for free weather data
- AWS for cloud infrastructure
- Streamlit for amazing web framework

---

⭐ **Star this repo nếu bạn thấy hữu ích!**
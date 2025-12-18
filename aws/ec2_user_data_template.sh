#!/bin/bash
# ============================================
# EC2 User Data Script Template
# Weather ETL System - Ubuntu 22.04 LTS
# ============================================
#
# 📝 HƯỚNG DẪN SỬ DỤNG:
# 
# 1. KHI LAUNCH EC2 TRÊN AWS CONSOLE:
#    - Copy nội dung file này
#    - Thay thế CÁC PLACEHOLDER bên dưới:
#      * YOUR_GITHUB_USERNAME
#      * YOUR_VISUAL_CROSSING_API_KEY  
#      * YOUR_S3_BUCKET_NAME
#    - Paste vào phần "User data" khi launch EC2
#
# 2. KHÔNG TẠO FILE ec2_user_data.sh VỚI API KEY THẬT!
#    (Nếu tạo, nó sẽ bị .gitignore block)
#
# 3. Script này AN TOÀN để push lên GitHub
#    vì không chứa API key thật
#
# ============================================

exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "============================================="
echo "🌤️  Weather ETL System Deployment"
echo "Started at: $(date)"
echo "============================================="

# ============================================
# [1/9] Update System
# ============================================
echo "[1/9] 📦 Updating system packages..."
apt update -y
apt upgrade -y

# ============================================
# [2/9] Install Docker
# ============================================
echo "[2/9] 🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu
echo "✅ Docker installed successfully"

# ============================================
# [3/9] Install Dependencies
# ============================================
echo "[3/9] 🔧 Installing Git and AWS CLI..."
apt install -y git awscli curl
echo "✅ Dependencies installed"

# ============================================
# [4/9] Clone Repository
# ============================================
echo "[4/9] 📥 Cloning repository from GitHub..."

# ⚠️ THAY YOUR_GITHUB_USERNAME BẰNG USERNAME THẬT CỦA BẠN
GITHUB_USERNAME="YOUR_GITHUB_USERNAME"
REPO_NAME="weather-etl-system"

cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git app

if [ $? -eq 0 ]; then
    echo "✅ Repository cloned successfully"
else
    echo "❌ ERROR: Failed to clone repository"
    exit 1
fi

cd app

# ============================================
# [5/9] Create Environment File
# ============================================
echo "[5/9] 🔐 Creating .env file with credentials..."

# ⚠️⚠️⚠️ QUAN TRỌNG - THAY THẾ CÁC GIÁ TRỊ SAU: ⚠️⚠️⚠️
#
# 1. YOUR_VISUAL_CROSSING_API_KEY
#    → Lấy tại: https://www.visualcrossing.com/weather-api
#    → Ví dụ: pk.abc123xyz456def789
#
# 2. YOUR_S3_BUCKET_NAME  
#    → Tên bucket S3 bạn đã tạo
#    → Ví dụ: weather-data-bucket-john
#

cat > .env << 'EOF'
WEATHER_API_KEY=YOUR_VISUAL_CROSSING_API_KEY
S3_BUCKET_NAME=YOUR_S3_BUCKET_NAME
AWS_REGION=ap-southeast-1
EOF

# Set secure permissions
chown ubuntu:ubuntu .env
chmod 600 .env

echo "✅ Environment file created"

# ============================================
# [6/9] Verify Configuration
# ============================================
echo "[6/9] ✔️  Verifying configuration..."

# Check if API key was replaced
if grep -q "YOUR_VISUAL_CROSSING_API_KEY" .env; then
    echo "⚠️  WARNING: API key placeholder not replaced!"
    echo "⚠️  Please replace YOUR_VISUAL_CROSSING_API_KEY with real API key"
fi

if grep -q "YOUR_S3_BUCKET_NAME" .env; then
    echo "⚠️  WARNING: S3 bucket placeholder not replaced!"
    echo "⚠️  Please replace YOUR_S3_BUCKET_NAME with real bucket name"
fi

# ============================================
# [7/9] Build Docker Image
# ============================================
echo "[7/9] 🏗️  Building Docker image..."
docker build -t weather-app .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ ERROR: Docker build failed"
    exit 1
fi

# ============================================
# [8/9] Run Docker Container
# ============================================
echo "[8/9] 🚀 Starting Docker container..."
docker run -d \
  -p 80:8501 \
  --name weather-app \
  --restart unless-stopped \
  --env-file .env \
  weather-app

if [ $? -eq 0 ]; then
    echo "✅ Docker container started successfully"
else
    echo "❌ ERROR: Failed to start container"
    exit 1
fi

# ============================================
# [9/9] Wait and Verify
# ============================================
echo "[9/9] ⏳ Waiting for application to be ready..."
sleep 15

# ============================================
# Deployment Status
# ============================================
echo ""
echo "============================================="
echo "📊 DEPLOYMENT STATUS"
echo "============================================="
echo ""

# Check Docker container
echo "🐳 Docker Containers:"
docker ps

echo ""
echo "📝 Recent Container Logs:"
docker logs weather-app --tail 30

echo ""
echo "============================================="
echo "✅ DEPLOYMENT COMPLETED"
echo "============================================="
echo ""
echo "⏰ Completed at: $(date)"
echo ""

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

echo "📍 Instance ID: ${INSTANCE_ID}"
echo "🌐 Public IP: ${PUBLIC_IP}"
echo ""
echo "🔗 Access web interface:"
echo "   http://${PUBLIC_IP}"
echo ""
echo "📊 View logs:"
echo "   ssh ubuntu@${PUBLIC_IP}"
echo "   sudo docker logs -f weather-app"
echo ""
echo "============================================="
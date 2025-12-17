#!/bin/bash
# EC2 User Data Script for Weather ETL System
# Ubuntu 22.04 LTS

exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "========================================="
echo "Weather ETL System Deployment"
echo "Started at: $(date)"
echo "========================================="

# Update system
echo "[1/8] Updating system..."
apt update -y
apt upgrade -y

# Install Docker
echo "[2/8] Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Install Git and AWS CLI
echo "[3/8] Installing Git and AWS CLI..."
apt install -y git awscli curl

# Install boto3 cho Lambda sau này (optional)
apt install -y python3-pip
pip3 install boto3

# Clone repository
echo "[4/8] Cloning repository..."
cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/YOUR_USERNAME/weather-etl-system.git app
cd app

# Create .env file from environment variables
# Lưu ý: Thay YOUR_API_KEY bằng API key thật
echo "[5/8] Creating .env file..."
cat > .env << 'EOF'
WEATHER_API_KEY=YOUR_VISUAL_CROSSING_API_KEY
S3_BUCKET_NAME=weather-data-bucket
AWS_REGION=ap-southeast-1
EOF

chown ubuntu:ubuntu .env

# Build Docker image
echo "[6/8] Building Docker image..."
docker build -t weather-app .

# Run Docker container
echo "[7/8] Running Docker container..."
docker run -d \
  -p 80:8501 \
  --name weather-app \
  --restart unless-stopped \
  --env-file .env \
  weather-app

# Wait for container to be healthy
echo "[8/8] Waiting for container to be ready..."
sleep 10

# Check status
echo "========================================="
echo "Deployment Status:"
echo "========================================="
docker ps
echo ""
echo "Container logs:"
docker logs weather-app --tail 20
echo ""
echo "========================================="
echo "Deployment completed at: $(date)"
echo "========================================="
echo ""
echo "Access the app at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""

# Optional: Auto-stop sau 2 giờ (7200 seconds)
# Uncomment dòng dưới nếu muốn EC2 tự động tắt sau khi hoàn thành
# (sleep 7200 && shutdown -h now) &
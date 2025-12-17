import streamlit as st
import boto3
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import socket
import json
from io import StringIO

# Cấu hình
LOCATION = "Vietnam"
START_DATE = "2021-01-01"
API_HOST = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
ELEMENTS = "datetime,temp,humidity,precip,windspeed,cloudcover"

# AWS S3
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'weather-data-bucket')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-southeast-1')

def get_daily_weather_data(api_key, query_date):
    """
    Gọi API Visual Crossing để lấy dữ liệu hourly cho 1 ngày cụ thể.
    """
    url = f"{API_HOST}/{LOCATION}/{query_date}"
    
    params = {
        "unitGroup": "metric",
        "include": "hours",
        "key": api_key,
        "contentType": "json",
        "elements": ELEMENTS
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def fetch_week_data(api_key):
    """
    Lấy dữ liệu thời tiết cho 7 ngày gần nhất
    """
    all_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        status_text.text(f"Đang tải dữ liệu ngày {date_str}...")
        
        daily_data = get_daily_weather_data(api_key, date_str)
        
        if daily_data and 'days' in daily_data:
            for day in daily_data['days']:
                if 'hours' in day:
                    for hour in day['hours']:
                        hour['date'] = date_str
                        all_data.append(hour)
        
        progress_bar.progress((i + 1) / 7)
    
    status_text.text("✅ Hoàn thành tải dữ liệu!")
    return pd.DataFrame(all_data)

def upload_to_s3(dataframe, bucket_name, file_key):
    """
    Upload DataFrame lên S3
    """
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        # Convert DataFrame to CSV
        csv_buffer = StringIO()
        dataframe.to_csv(csv_buffer, index=False)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        return True
    except Exception as e:
        st.error(f"S3 Upload Error: {str(e)}")
        return False

def process_weather_data(df):
    """
    Xử lý dữ liệu thời tiết
    """
    if df.empty:
        return df
    
    # Convert datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Xử lý missing values
    df['temp'] = df['temp'].fillna(df['temp'].mean())
    df['humidity'] = df['humidity'].fillna(df['humidity'].mean())
    df['precip'] = df['precip'].fillna(0)
    df['windspeed'] = df['windspeed'].fillna(df['windspeed'].mean())
    df['cloudcover'] = df['cloudcover'].fillna(df['cloudcover'].mean())
    
    # Thêm features
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    
    return df

# Streamlit UI
st.set_page_config(page_title="Weather Data Collection", page_icon="🌤️", layout="wide")

st.title("🌤️ Weather Data Collection System")
st.write("Hệ thống tự động thu thập dữ liệu thời tiết và lưu vào S3")

# Hiển thị thông tin host
col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"🖥️ Host: {socket.gethostname()}")
with col2:
    st.info(f"📦 S3 Bucket: {S3_BUCKET}")
with col3:
    st.info(f"🌍 Region: {AWS_REGION}")

# Lấy API key từ môi trường
api_key = os.environ.get('WEATHER_API_KEY', '')

if not api_key:
    st.warning("⚠️ Chưa có WEATHER_API_KEY trong environment variables!")
    api_key_input = st.text_input("Nhập API Key:", type="password")
    if api_key_input:
        api_key = api_key_input

# Main workflow
if api_key:
    st.success("✅ API Key đã được cấu hình")
    
    if st.button("🚀 Bắt đầu thu thập dữ liệu", type="primary"):
        
        with st.spinner("Đang thu thập dữ liệu..."):
            # Step 1: Fetch data
            st.subheader("📥 Bước 1: Thu thập dữ liệu từ API")
            df_raw = fetch_week_data(api_key)
            
            if not df_raw.empty:
                st.success(f"✅ Đã thu thập {len(df_raw)} records")
                st.dataframe(df_raw.head())
                
                # Step 2: Upload raw data
                st.subheader("☁️ Bước 2: Upload dữ liệu thô lên S3")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                raw_key = f"raw/weather/weather_raw_{timestamp}.csv"
                
                if upload_to_s3(df_raw, S3_BUCKET, raw_key):
                    st.success(f"✅ Đã lưu raw data: {raw_key}")
                    
                    # Step 3: Process data
                    st.subheader("⚙️ Bước 3: Xử lý dữ liệu")
                    df_processed = process_weather_data(df_raw.copy())
                    st.success(f"✅ Đã xử lý {len(df_processed)} records")
                    st.dataframe(df_processed.head())
                    
                    # Step 4: Upload processed data
                    st.subheader("☁️ Bước 4: Upload dữ liệu đã xử lý lên S3")
                    processed_key = f"processed/weather_processed_{timestamp}.csv"
                    
                    if upload_to_s3(df_processed, S3_BUCKET, processed_key):
                        st.success(f"✅ Đã lưu processed data: {processed_key}")
                        
                        # Summary
                        st.subheader("📊 Tóm tắt")
                        st.json({
                            "total_records": len(df_processed),
                            "date_range": f"{df_processed['date'].min()} to {df_processed['date'].max()}",
                            "raw_file": raw_key,
                            "processed_file": processed_key,
                            "timestamp": timestamp
                        })
                        
                        st.balloons()
                        st.success("🎉 Hoàn thành quy trình ETL!")
            else:
                st.error("❌ Không có dữ liệu để xử lý")
else:
    st.error("❌ Vui lòng cung cấp API Key!")

# Footer
st.markdown("---")
st.caption("Hệ thống sẽ tự động tắt sau khi hoàn thành. Dữ liệu được lưu tại S3.")
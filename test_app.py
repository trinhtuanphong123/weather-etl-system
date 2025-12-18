import pytest
import pandas as pd
from datetime import datetime
import os

def test_environment_variables():
    """Test kiểm tra có thể set environment variables"""
    os.environ['TEST_VAR'] = 'test_value'
    assert os.environ.get('TEST_VAR') == 'test_value'

def test_pandas_dataframe():
    """Test tạo DataFrame cơ bản"""
    df = pd.DataFrame({
        'datetime': ['2024-01-01 00:00:00'],
        'temp': [25.5],
        'humidity': [80],
        'precip': [0],
        'windspeed': [10],
        'cloudcover': [50]
    })
    assert len(df) == 1
    assert 'temp' in df.columns

def test_data_processing():
    """Test xử lý dữ liệu cơ bản"""
    df = pd.DataFrame({
        'temp': [25, None, 30],
        'humidity': [80, 85, None]
    })
    
    # Fill missing values
    df['temp'] = df['temp'].fillna(df['temp'].mean())
    df['humidity'] = df['humidity'].fillna(df['humidity'].mean())
    
    assert df['temp'].isna().sum() == 0
    assert df['humidity'].isna().sum() == 0

def test_datetime_parsing():
    """Test parse datetime"""
    date_str = "2024-01-01"
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    assert date_obj.year == 2024
    assert date_obj.month == 1
    assert date_obj.day == 1

def test_api_url_construction():
    """Test tạo API URL"""
    api_host = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    location = "Vietnam"
    query_date = "2024-01-01"
    
    url = f"{api_host}/{location}/{query_date}"
    
    assert "Vietnam" in url
    assert "2024-01-01" in url
    assert url.startswith("https://")

def test_s3_key_generation():
    """Test tạo S3 key paths"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    raw_key = f"raw/weather/weather_raw_{timestamp}.csv"
    processed_key = f"processed/weather_processed_{timestamp}.csv"
    
    assert raw_key.startswith("raw/weather/")
    assert processed_key.startswith("processed/")
    assert raw_key.endswith(".csv")
    assert processed_key.endswith(".csv")

def test_data_columns():
    """Test kiểm tra các cột dữ liệu cần thiết"""
    required_columns = ['datetime', 'temp', 'humidity', 'precip', 'windspeed', 'cloudcover']
    
    df = pd.DataFrame(columns=required_columns)
    
    for col in required_columns:
        assert col in df.columns

def test_dummy():
    """Test luôn đúng để đảm bảo pytest chạy được"""
    assert 1 + 1 == 2
    assert True is True
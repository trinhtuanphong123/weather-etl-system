import boto3
import os
from datetime import datetime

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    """
    Lambda function để tự động START EC2 instance
    """
    
    try:
        instance_id = os.environ.get('INSTANCE_ID', '')
        
        if not instance_id:
            return {
                'statusCode': 400,
                'body': 'Error: INSTANCE_ID not configured'
            }
        
        print(f"Starting EC2 instance: {instance_id}")
        
        # Start instance
        response = ec2.start_instances(InstanceIds=[instance_id])
        
        started_instances = [
            inst['InstanceId'] for inst in response['StartingInstances']
        ]
        
        result = {
            'statusCode': 200,
            'body': f'Successfully started EC2: {started_instances}',
            'timestamp': datetime.now().isoformat(),
            'instances': started_instances,
            'message': 'EC2 will fetch weather data and upload to S3'
        }
        
        print(result)
        return result
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error starting EC2: {str(e)}'
        }
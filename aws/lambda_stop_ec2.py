import boto3
import os
from datetime import datetime

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    """
    Lambda function để tự động STOP EC2 instance sau khi hoàn thành ETL
    """
    
    try:
        instance_id = os.environ.get('INSTANCE_ID', '')
        
        if not instance_id:
            return {
                'statusCode': 400,
                'body': 'Error: INSTANCE_ID not configured'
            }
        
        print(f"Stopping EC2 instance: {instance_id}")
        
        # Check instance state trước khi stop
        response = ec2.describe_instances(InstanceIds=[instance_id])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        
        if state != 'running':
            return {
                'statusCode': 200,
                'body': f'EC2 is already {state}, no action needed',
                'timestamp': datetime.now().isoformat()
            }
        
        # Stop instance
        response = ec2.stop_instances(InstanceIds=[instance_id])
        
        stopped_instances = [
            inst['InstanceId'] for inst in response['StoppingInstances']
        ]
        
        result = {
            'statusCode': 200,
            'body': f'Successfully stopped EC2: {stopped_instances}',
            'timestamp': datetime.now().isoformat(),
            'instances': stopped_instances,
            'message': 'Weather data collection completed, EC2 stopped to save cost'
        }
        
        print(result)
        return result
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error stopping EC2: {str(e)}'
        }
import json
import boto3
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    paginator = cloudwatch.get_paginator('describe_alarms')
    page_iterator = paginator.paginate()
    filtered_iterator = page_iterator.search("MetricAlarms[?AlarmActions==['arn:aws:sns:us-east-1:679064942344:auto-recover'] && Namespace==`AWS/EC2`]")
    
    for alarm in filtered_iterator:
        print('Alarm Name:')
        print(alarm['AlarmName'])
        print('Alarm Action:')
        print(alarm['AlarmActions'])
        print('Alarm Namespace:')
        print(alarm['Namespace'])
        
    # filtered_iterator = page_iterator.search("MetricAlarms[?MetricName==`CPUUtilization` && Namespace==`AWS/EC2`]")    
    # paginator = cloudwatch.get_paginator('describe_alarms')
    # for response in paginator.paginate(StateValue='OK'):
    #     print(response['MetricAlarms'])
        
    
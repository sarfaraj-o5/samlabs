
from __future__ import print_function
import boto3
import logging
import os

# SNS Topic Definition for EC2, EBS
ec2_sns = os.environ['SNS_TOPIC_ARN'] #'<SNS_TOPIC_ARN>'


# AWS Account and Region Definition for Reboot Actions
# region = 'us-east-1'
name_tag = 'ec2-stop'

# Create AWS clients
ec2session = boto3.client('ec2')
cw = boto3.client('cloudwatch')

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Retrives instance id from cloudwatch event
# def get_instance_id(event):
#     try:
#         return event['detail']['instance-id']
#     except KeyError as err:
#         LOGGER.error(err)
#         return False

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    regions = ec2.describe_regions()

    for region in regions['Regions']:
        currentregion = region['RegionName']
        print('Region: %s' % currentregion)
        ec2 = boto3.resource('ec2', region_name=currentregion)
        ec2client = boto3.client('ec2', region_name=currentregion)
        cw = boto3.client('cloudwatch')

        ec2resources = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        ec2instances = []
        freezedInstanceType = ['a1', 'c3', 'c4', 'c5', 'c5n', 'm3', 'm4', 'm5', 'm5a', 'p3', 'r3', 'r4', 'r5', 'r5a', 't2', 't3', 'x1', 'x1e']

        for resource in ec2resources:
            ec2instances.append(resource.id)

        for instanceid in ec2instances:
            ec2client = boto3.client('ec2', region_name=currentregion)
            ec2details = ec2client.describe_instances(InstanceIds=[instanceid])
            print(ec2details)

            if 'Reservations' in ec2details:
                for reservations in ec2details['Reservations']:
                    for insttype in reservations['Instances']:
                        instancetype = insttype['InstanceType']
                        instancetype = instancetype.split('.')
                        if instancetype[0] in freezedInstanceType:
                            print('present')
                            matchedInstance = insttype['InstanceId']
                            print(insttype['InstanceType'])
                            response = cw.put_metric_alarm(AlarmName="%s %s Status Check CPU" % (name_tag, matchedInstance), AlarmDescription='CPU Utilization Greater than 85% for 15+ Minutes', ActionsEnabled=True, AlarmActions=[ec2_sns, "arn:aws:automate:%s:ec2:stop" % currentregion], MetricName='CPUUtilization', Namespace='AWS/EC2', Statistic='Average', Dimensions=[{ 'Name': 'InstanceId', 'Value': matchedInstance }, ], Period=300, EvaluationPeriods=3, Threshold=85.0, ComparisonOperator='GreaterThanOrEqualToThreshold')
from __future__ import print_function
import boto3
import logging
import os
import json

cloudwatch = boto3.client('cloudwatch')
ec2_sns = os.environ['SNS_TOPIC_ARN'] #'<SNS_TOPIC_ARN>'

# region = 'us-east-1'

# Create AWS clients
ec2session = boto3.client('ec2')
cw = boto3.client('cloudwatch')
sns = boto3.client('sns')

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# def check_watch():
#     ec2 = boto3.client('ec2')
#     regions = ec2.describe_regions()

#     for region in regions['Regions']:
#         currentregion = region['RegionName']
#         print('Region: %s' % currentregion)
#         ec2 = boto3.resource('ec2', region_name=currentregion)
#         ec2client = boto3.client('ec2', region_name=currentregion)
#         cw = boto3.client('cloudwatch')

#         ec2resources = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
#         ec2instances = []
#         freezedInstanceType = ['a1', 'c3', 'c4', 'c5', 'c5n', 'm3', 'm4', 'm5', 'm5a', 'p3', 'r3', 'r4', 'r5', 'r5a', 't2', 't3', 'x1', 'x1e']

#         for resource in ec2resources:
#             ec2instances.append(resource.id)

#         for instanceid in ec2instances:
#             ec2client = boto3.client('ec2', region_name=currentregion)
#             ec2details = ec2client.describe_instances(InstanceIds=[instanceid])
#             print(ec2details)

#             if 'Reservations' in ec2details:
#                 for reservations in ec2details['Reservations']:
#                     for insttype in reservations['Instances']:
#                         instancetype = insttype['InstanceType']
#                         instancetype = instancetype.split('.')
#                         if instancetype[0] in freezedInstanceType:
#                             print('present')
#                             matchedInstance = insttype['InstanceId']
#                             print(insttype['InstanceType'])


                            # response = cw.put_metric_alarm(AlarmName="%s %s Status Check Failed" % (name_tag, matchedInstance), AlarmDescription='Status Check Failed (Instance) for 5 Minutes', ActionsEnabled=True, AlarmActions=[ec2_sns, "arn:aws:automate:%s:ec2:reboot" % currentregion], MetricName='StatusCheckFailed_Instance', Namespace='AWS/EC2', Statistic='Average', Dimensions=[{ 'Name': 'InstanceId', 'Value': matchedInstance }, ], Period=60, EvaluationPeriods=2, Threshold=2.0, ComparisonOperator='GreaterThanOrEqualToThreshold')
                            
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
                            paginator = cloudwatch.get_paginator('describe_alarms')
                            page_iterator = paginator.paginate()
                            filtered_iterator = page_iterator.search("MetricAlarms[?AlarmActions==['arn:aws:sns:us-east-1:679064942344:auto-recover'] && Namespace==`AWS/EC2`]")
                            for alarm in filtered_iterator:
                                print(alarm['AlarmName'])
                                alarmname = alarm['AlarmName']
                                print('Alarm Action:')
                                print(alarm['AlarmActions'])
                                print('Alarm Namespace:')
                                print(alarm['Namespace'])

                                # Delete alarm
                                cloudwatch.delete_alarms(AlarmNames=[alarmname])
                                #SNS Notification Sending
                                response = sns.publish(TopicArn='arn:aws:sns:us-east-1:679064942344:auto-recover',Message='No Action Assigned to this Alarm:---->' + alarm['AlarmName'] + '**********Hence Deleted**********')
                                # Print out the response
                                print(response)
        
        
        
    # filtered_iterator = page_iterator.search("MetricAlarms[?MetricName==`CPUUtilization` && Namespace==`AWS/EC2`]")    
    # paginator = cloudwatch.get_paginator('describe_alarms')
    # for response in paginator.paginate(StateValue='OK'):
    #     print(response['MetricAlarms'])
        
    
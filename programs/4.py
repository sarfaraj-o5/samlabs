# Create Network Alarms which are platform specific – using lambda python

#Create Network Alarms which are platform specific
    print (instance.platform)
     if   (instance.platform != 'windows'):
        #ImageId, InstanceId, InstanceType
        response = cw.list_metrics(
            Namespace='CWAgent',
            MetricName='netstat_tcp_established',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instanceid
                },
            ]
            #NextToken='string'
         )
        for metric in response['Metrics']:
            ###############################################
            #Create Netstat TCP Established Connection Alarms
            severity = "Warning"
            alarm_title = "Linux_netstat_TCP_Established"
            response = cw.put_metric_alarm(
             AlarmName = "%s_%s_%s_(Lambda)" % (severity, nameinstance, alarm_title),
             AlarmDescription='Netstat TCP Established Connections',
             ActionsEnabled=True,
             AlarmActions=[ec2_sns,],
             MetricName='netstat_tcp_established',
             Namespace='CWAgent',
             Statistic='Average',
             Dimensions=[ {'Name': "InstanceId",   'Value': instanceid},
                          {'Name': 'ImageId',      'Value': instance.image_id},
                          {'Name': 'InstanceType', 'Value': instance.instance_type}
                        ],
             Period=60,
             EvaluationPeriods=3,
             Threshold=200.0,
             ComparisonOperator='GreaterThanOrEqualToThreshold'
            ) 
            if logging_verbosity > 9:
                print (response)
                  
            ###############################################
            #Create Netstat TCP Time Wait Alarms
            severity = "Warning"
            alarm_title = "Linux_netstat_TCP_Time_Wait"
            response = cw.put_metric_alarm(
             AlarmName = "%s_%s_%s_(Lambda)" % (severity, nameinstance, alarm_title),
             AlarmDescription='Netstat TCP Established Connections',
             ActionsEnabled=True,
             AlarmActions=[ec2_sns,],
             MetricName='netstat_tcp_time_wait',
             Namespace='CWAgent',
             Statistic='Average',
             Dimensions=[ {'Name': "InstanceId",   'Value': instanceid},
                          {'Name': 'ImageId',      'Value': instance.image_id},
                          {'Name': 'InstanceType', 'Value': instance.instance_type}
                        ],
             Period=60,
             EvaluationPeriods=3,
             Threshold=400.0,
             ComparisonOperator='GreaterThanOrEqualToThreshold'
            )
            if logging_verbosity > 9:
                print (response)
         
     elif (instance.platform == 'windows'):
        #ImageId, InstanceId, InstanceType
         
        ###############################################
        #Create Windows TCPv4 Established Connection Alarms
        severity = "Warning"
        alarm_title = "Windows_netstat_TCP_Established"
        response = cw.put_metric_alarm(
         AlarmName = "%s_%s_%s_(Lambda)" % (severity, nameinstance, alarm_title),
         AlarmDescription='Netstat TCP Established Connections',
         ActionsEnabled=True,
         AlarmActions=[ec2_sns,],
         MetricName='TCPv4 Connections Established',
         Namespace='CWAgent',
         Statistic='Average',
         Dimensions=[ {'Name': "InstanceId",    'Value': instanceid},
                      {'Name': 'ImageId',       'Value': instance.image_id},
                      {'Name': 'objectname',    'Value': 'TCPv4'},
                      {'Name': 'InstanceType',  'Value': instance.instance_type}
                    ],
         Period=60,
         EvaluationPeriods=3,
         Threshold=400.0,
         ComparisonOperator='GreaterThanOrEqualToThreshold'
        ) 
        if logging_verbosity > 9:
            print (response)
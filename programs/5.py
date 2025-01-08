# EBS Volumes Metric alarm in aws lambda python

###########################################################################
     #########
     ######### EBS Volumes
     #########
     ###########################################################################
     
     vol_id = instance.volumes.all()

     for v in vol_id:
   
          if logging_verbosity > 2:
              print("Found EBS volume %s on instance %s" % (v.id, instanceid))
       
          ###############################################
          #Create Metric "Volume Idle Time <= 30 sec (of 5 minutes) for 30 Minutes
          severity = "Warning"
          alarm_title = "Low_Volume_Idle_Time"
          response = cw.put_metric_alarm(
           AlarmName = "%s_%s_%s_%s_(Lambda)" % (severity, nameinstance, v.id, alarm_title),
           #AlarmName="%s %s High Volume Activity Warning" % (v.id, instanceid),
           AlarmDescription='Volume Idle Time <= 30 sec (of 5 minutes) for 30 Minutes',
           ActionsEnabled=True,
           AlarmActions=[
               ec2_sns
           ],
           MetricName='VolumeIdleTime',
           Namespace='AWS/EBS',
           Statistic='Average',
           Dimensions=[
               {
                   'Name': 'VolumeId',
                   'Value': v.id
               },
           ],
           Period=300,
           EvaluationPeriods=6,
           Threshold=30.0,
           ComparisonOperator='LessThanOrEqualToThreshold'
          )
          if logging_verbosity > 9:
               print (response)
      
          ###############################################
          #Create Metric "Volume Idle Time <= 30 sec (of 5 minutes) for 60 Minutes
          severity = "Critical"
          alarm_title = "Low_Volume_Idle_Time"
          response = cw.put_metric_alarm(
           AlarmName = "%s_%s_%s_%s_(Lambda)" % (severity, nameinstance, v.id, alarm_title),
           #AlarmName="%s %s High Volume Activity Critical" % (v.id, instanceid),
           AlarmDescription='Volume Idle Time <= 30 sec (of 5 minutes) for 60 Minutes',
           ActionsEnabled=True,
           AlarmActions=[
               ec2_sns
           ],
           MetricName='VolumeIdleTime',
           Namespace='AWS/EBS',
           Statistic='Average',
           Dimensions=[
               {
                   'Name': 'VolumeId',
                   'Value': v.id
               },
           ],
           Period=300,
           EvaluationPeriods=12,
           Threshold=30.0,
           ComparisonOperator='LessThanOrEqualToThreshold'
          )
     
     ###########################################################################
     #########
     ######### Instance Level EBS Metrics
     #########
     ###########################################################################
          
     # Nitro does not seem to provide these...
     if (instance.hypervisor == 'xen'):
          ###############################################
          #Create DiskWriteOps Alarms    
          severity = "Warning"
          alarm_title = "DiskWriteOps"
          response = cw.put_metric_alarm(
           AlarmName = "%s_%s_%s_(Lambda)" % (severity, nameinstance, alarm_title),
           #AlarmName = (nameinsta) +"_DiskWriteOps_(Lambda)",
           AlarmDescription='DiskWriteOps ',
           ActionsEnabled=True,
           AlarmActions=[ec2_sns,],
           MetricName='DiskWriteOps',
           Namespace='AWS/EC2',
           Statistic='Average',
           Dimensions=[ {'Name': "InstanceId",'Value': instanceid},],
           Period=900,
           EvaluationPeriods=1,
           Threshold=2500,
           ComparisonOperator='GreaterThanOrEqualToThreshold'
          )
          if logging_verbosity > 9:
               print (response)
                  
          ###############################################
          #Create DiskReadOps Alarms    
          severity = "Warning"
          alarm_title = "DiskReadOps"
          response = cw.put_metric_alarm(
           AlarmName = "%s_%s_%s_(Lambda)" % (severity, nameinstance, alarm_title),
           #AlarmName= (nameinsta) +"_DiskReadOps_(Lambda)",
           AlarmDescription='DiskReadOps ',
           ActionsEnabled=True,
           AlarmActions=[ec2_sns,],
           MetricName='DiskReadOps',
           Namespace='AWS/EC2',
           Statistic='Average',
           Dimensions=[ {'Name': "InstanceId",'Value': instanceid},],
           Period=900,
           EvaluationPeriods=1,
           Threshold=2500,
           ComparisonOperator='GreaterThanOrEqualToThreshold'
          )
          if logging_verbosity > 9:
               print (response)
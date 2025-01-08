Create Metric – CPU Utilization Greater than 85% for 15+ Minutes – using lambda python

severity = "Information"
     alarm_title = "High_CPUUtilization"
     response = cw.put_metric_alarm(
      AlarmName = "%s_%s_%s_(Lambda)" % (severity, nameinstance, alarm_title),
      #AlarmName = (nameinsta) + "_CPU_Load_(Lambda)",
      AlarmDescription='CPU Utilization Greater than 85% for 15+ Minutes',
      ActionsEnabled=True,
      AlarmActions=[ec2_sns,],
      MetricName='CPUUtilization',
      Namespace='AWS/EC2',
      Statistic='Average',
      Dimensions=[ {'Name': "InstanceId",'Value': instanceid},],
      Period=300,
      EvaluationPeriods=3,
      Threshold=85.0,
      ComparisonOperator='GreaterThanOrEqualToThreshold'
     )
     if logging_verbosity > 9:
          print (response)
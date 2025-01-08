Centralized Linux Instances of Multiple Accounts and Cross-Platform EC2 Instances Using AWS Systems Manager

Step 1 – Activation Id and Activation Code Creation
Open Console AWS Sign In Screen
Login to Parent Account i.e. Shared Account as per above diagram
In Services select System Manager
Click on Hybrid Activations
click on create activation button.
Specify Instance Limit
Specify activation expiry date of next month as from todays date. It is valid for 30 days.
click on create activation

Step 2 – Create Parameter Store
Sign out from parent account
Login to child account i.e. sandbox as per diagram
in services box type system manager
click on paraemter store – click on create parameter
Specify Name i.e. ActivationId – click on standard and string radio buttons then copy and paste the value generated from Hybrid Activations in the value box.
click on create paramete

step-3 Linux Instances Registering Instances Lambda Python Program

import json
import boto3
import re
import time

def tagging(tagInstance):
    tagvalue = ''
    outputactivation = ''
    s3 = boto3.resource('s3')
    ec2client = boto3.client('ec2', region_name='us-east-1')
    tagInstancePrefix = tagInstance+'-nonprod'
    
    
    bucket = s3.Bucket('cloudz-mi-instances')
    for obj in bucket.objects.filter(Prefix=tagInstancePrefix):
        if "stdout" in obj.key:
        	print obj
        	outputactivation = s3.Object('cloudz-mi-instances', obj.key)
        	outputactivation = outputactivation.get()['Body'].read().decode('utf-8')
        	myoutput = outputactivation.splitlines()
        	print myoutput
        	for content in myoutput:
				words = content.split()
				for word in words:
					if "mi-" in word:
						tagvalue = word
						print 'tagvalue: %s' % tagvalue
						create_tags = ec2client.create_tags(Resources=[str(tagInstance)],Tags=[{'Key':'NonProdManagedInstanceid', 'Value':tagvalue }])
						print 'create_tags:'
						tagresponse = create_tags['ResponseMetadata']['HTTPStatusCode']
						# print tagresponse
						if tagresponse == 200:
							print 'Successfully tagged instanceid: %s' % tagInstance
						else:
							print 'Activation failed for instanceid: %s\n' % tagInstance
    

def Activation(InstanceID):
	REGION="us-east-1"
	# Getting the AWS credentials from the IAM role
	mysession = session.Session()
	credentials = mysession.get_credentials()

	#Getting Activation ID and Code from parameter store
	ssm = boto3.client('ssm',region_name=REGION)
	s3 = boto3.resource('s3')
	ec2client = boto3.client('ec2', region_name='us-east-1')

	activation_id = ssm.get_parameter(Name='ActivationID')
	ActivationID = activation_id['Parameter']['Value']
	activation_code = ssm.get_parameter(Name='ActivationCode')
	ActivationCode = activation_code['Parameter']['Value']
	
	myprefix = InstanceID+'-nonprod'
	
	print 'Platform type: Linux'
	client = boto3.client('ssm', region_name='us-east-1')
	response = client.send_command(
		InstanceIds=[InstanceID],
		DocumentName='AWS-RunShellScript',
		DocumentVersion='1',
		Parameters={
			'commands': [
				'sudo amazon-ssm-agent -register -y -code %s -id %s -region us-east-1' % (ActivationCode, ActivationID)
				]
		}, 
		OutputS3Region='us-east-1',
		OutputS3BucketName='bose-mi-instances',
		OutputS3KeyPrefix=myprefix
	)
	# print "response:"
	# print response
	time.sleep(3)
	return InstanceID
	
	
def lambda_handler(event, context):
    toBetaggedInstanceid = []
    currentregion = 'us-east-1'
    # ec2client = boto3.client('ec2', region_name=currentregion)
    ec2 = boto3.resource('ec2', region_name=currentregion)
    
    running_instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    
    # running_instances = ec2.instances.filter(Filters=[{
				# 							'Name': 'tag-value',
				# 							'Values': ['amazon']
				# 				        	    }
				# 		        	        ]
				# 		)
	

    myid = []
    for instance in running_instances:
        myid.append(instance.id)
    
    ssmclient = boto3.client('ssm')
    ec2client = boto3.client('ec2', region_name='us-east-1')
    
    for instanceid in myid:
    	platform = ssmclient.describe_instance_information(InstanceInformationFilterList=[{'key':'InstanceIds','valueSet':[instanceid] }])

    	for plt in platform['InstanceInformationList']:
    		platformtype = plt['PlatformType']
    		ec2_attached_tags = ec2client.describe_instances(Filters=[{'Name': 'tag-key','Values': ['NonProdManagedInstanceid']}],InstanceIds=[instanceid])
        
	        if platformtype == 'Linux':
	        	if not ec2_attached_tags['Reservations']:
	        		instid = Activation(instanceid)
	        		toBetaggedInstanceid.append(instid)
	        	else:
	        		print 'InstanceId: %s is already Activated' % instanceid
	
	
	taggingInstanceid = ''
	print 'all instances'
	print toBetaggedInstanceid
	for taggingInstanceid in toBetaggedInstanceid:
		tagging(taggingInstanceid)

Step 4 – Create one role SSMManager Full Access and attach this role to all ec2 instances [Note Before executing above progam pls do th
Step 5- permissions to access Systems Manager Parameter Store and create EC2 tags. Policy Created i.e. IAM – POLICY – policy name (ssm-paraemter)




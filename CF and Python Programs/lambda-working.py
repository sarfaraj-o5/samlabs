from boto3 import session
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
    bucket = s3.Bucket('sysman-py1')
    for obj in bucket.objects.filter(Prefix=tagInstancePrefix):
        if "stdout" in obj.key:
			# print obj
			outputactivation = s3.Object('sysman-py1', obj.key)
			outputactivation = outputactivation.get()['Body'].read().decode('utf-8')

			myoutput = outputactivation.splitlines()
			# print myoutput
			for content in myoutput:
				words = content.split()
				for word in words:
					if "mi-" in word:
						tagvalue = word
						print 'tagvalue: %s' % tagvalue
						mivalue = json.loads(tagvalue)
						mitag = mivalue['ManagedInstanceID']
						print 'test: %s' % mivalue['ManagedInstanceID']
						create_tags = ec2client.create_tags(Resources=[str(tagInstance)],Tags=[{'Key':'NonProdManagedInstanceid', 'Value':mitag }])
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

	print 'Platform type: Windows'

	client = boto3.client('ssm', region_name='us-east-1')
	response = client.send_command( InstanceIds=[InstanceID],
				DocumentName='AWS-RunPowerShellScript',
				Comment='Restarting Server',
				Parameters={
					"commands":
						[
							"curl https://sysman-py1.s3.amazonaws.com/win-registration.ps1 -O c:\\win-registration.ps1",
							".\\win-registration.ps1"

						],
						"workingDirectory": ["C:\\"]
				},
				OutputS3Region='us-east-1',
				OutputS3BucketName='sysman-py1',
				OutputS3KeyPrefix=myprefix
				)

	time.sleep(3)
	return InstanceID

def starTagging(toBetaggedInstanceid):
	time.sleep(15)
	taggingInstanceid = ''
	print 'all instances'
	print toBetaggedInstanceid
	for taggingInstanceid in toBetaggedInstanceid:
		tagging(taggingInstanceid)


def lambda_handler(event, context):
    toBetaggedInstanceid = []
    currentregion = 'us-east-1'
    # ec2client = boto3.client('ec2', region_name=currentregion)
    ec2 = boto3.resource('ec2', region_name=currentregion)

    running_instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    myid = []
    for instance in running_instances:
        myid.append(instance.id)

    ssmclient = boto3.client('ssm')
    ec2client = boto3.client('ec2', region_name='us-east-1')
    starTagging(toBetaggedInstanceid)

    for instanceid in myid:
    	platform = ssmclient.describe_instance_information(InstanceInformationFilterList=[{'key':'InstanceIds','valueSet':[instanceid] }])

    	for plt in platform['InstanceInformationList']:
    		platformtype = plt['PlatformType']
    		ec2_attached_tags = ec2client.describe_instances(Filters=[{'Name': 'tag-key','Values': ['NonProdManagedInstanceid']}],InstanceIds=[instanceid])

	        if platformtype == 'Windows':
	        	if not ec2_attached_tags['Reservations']:
	        		instid = Activation(instanceid)
	        		toBetaggedInstanceid.append(instid)
	        	else:
	        		print 'InstanceId: %s is already Activated' % instanceid


    starTagging(toBetaggedInstanceid)



        

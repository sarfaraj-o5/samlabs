import boto3
import datetime

client = boto3.client('iam')

def lambda_handler(event, context):
    output =[]
    data = []
    paginator = client.get_paginator('list_instance_profiles')
    # iamclient = boto3.client('iam')

    for response in paginator.paginate():
        for instanceProfile in response['InstanceProfiles']:
            print
            print(instanceProfile['InstanceProfileName'])
            # print(instanceProfile['Roles'])
            try:
                profile = instanceProfile['InstanceProfileName']
                response = client.delete_instance_profile(InstanceProfileName=profile)
                print(response)
                print('Deleted instance profile - %s ' % profile )
            except Exception, e:
                continue
            for rolename in instanceProfile['Roles']:
                print(rolename['RoleName'])


            

            



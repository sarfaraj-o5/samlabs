import sys
import boto3
import datetime

client = boto3.client('iam')

def lambda_handler(event, context):

    paginator = client.get_paginator('list_instance_profiles')
    policyPaginator = client.get_paginator('get_account_authorization_details')

    ec2client = boto3.client('ec2')
    iamclient = boto3.client('iam')

    allInstanceIds = []
    usedInstanceProfileArn = []
    usedInstanceProfileName = []
    roleName = []
    managedPolicies = []
    managedPoliciesData = {}
    instanceProfileList = []
    inlinePolicies = []

    ec2 = boto3.resource('ec2')
    for instance in ec2.instances.all():
        # print (instance.id , instance.state)
        allInstanceIds.append(instance.id)

    # print allInstanceIds

    for instId in allInstanceIds:
        res = ec2client.describe_instances(InstanceIds=[instId])
        # res = ec2client.describe_instances(InstanceIds=['i-0b209466f870fbd1f'])
        # print "res"
        if 'IamInstanceProfile' in res['Reservations'][0]['Instances'][0]:
            # print res['Reservations'][0]['Instances'][0]['IamInstanceProfile']['Arn']
            usedInstanceProfileArn.append(res['Reservations'][0]['Instances'][0]['IamInstanceProfile']['Arn'])


    # print "in use role:"
    for i in usedInstanceProfileArn:
        usedInstanceProfileName.append(i.split("/")[1])


    for roleDetails in policyPaginator.paginate(Filter=['Role']):
        # print roleDetails

        for i in roleDetails['RoleDetailList']:
            if i['RolePolicyList']:
                for l in i['RolePolicyList']:
                    inlinePolicies.append(l['PolicyName'])

            if i['AttachedManagedPolicies']:
                for j in i['AttachedManagedPolicies']:
                    managedPolicies.append(j['PolicyArn'])

            if i['InstanceProfileList']:
                for k in i['InstanceProfileList']:
                    instanceProfileList.append(k['Arn'])

            rolePol = i['RoleName']
            managedPoliciesData[rolePol] = { 'inlinePolicies': inlinePolicies, 'managedPolicies': managedPolicies, 'instanceProfileName': instanceProfileList }
            instanceProfileList = []
            managedPolicies = []
            inlinePolicies = []

    # Pick only the Roles which have instance profile on it.
    # print managedPoliciesData[rolePol]
    for role, roleDetails in managedPoliciesData.items():
        if len(roleDetails['instanceProfileName']) == 0:
            managedPoliciesData.pop(role)

    # Delete used roles from the Dictionary
    for rRole, rRoleDetails in managedPoliciesData.items():
        if rRoleDetails['instanceProfileName']:
            for matches in rRoleDetails['instanceProfileName']:
                if matches in usedInstanceProfileArn:
                    managedPoliciesData.pop(rRole)

    # Before deleting:::
    for key, data in managedPoliciesData.items():
        print "Role:::"
        print key
        print data


    if bool(managedPoliciesData):
        for deleteRole, deletePolicy in managedPoliciesData.items():
            if deletePolicy['inlinePolicies']:
                for delpol in deletePolicy['inlinePolicies']:
                    print delpol
                    print deleteRole
                    removePolicyResponse = iamclient.delete_role_policy(RoleName=deleteRole, PolicyName=delpol)
                    print "Removed Policy Response:"
                    print removePolicyResponse
            if deletePolicy['managedPolicies']:
                for profArn in deletePolicy['managedPolicies']:
                    detachRolePol_Response = iamclient.detach_role_policy(RoleName=deleteRole, PolicyArn=profArn)
                    print "detachRolePol_Response"
                    print detachRolePol_Response
            if deletePolicy['instanceProfileName']:
                for p in deletePolicy['instanceProfileName']:
                    print p.split("/")[-1]
                    instProfName = p.split("/")[-1]
                    removeRoleInstanceProfResponse = iamclient.remove_role_from_instance_profile(InstanceProfileName=instProfName, RoleName=deleteRole)
                    print "removeRoleInstanceProfResponse"
                    print removeRoleInstanceProfResponse
            print "Deleting role: %s" % deleteRole
            delRoleResponse = iamclient.delete_role(RoleName=deleteRole)
            print delRoleResponse


    # ec2conn = boto3.client('ec2')
    # reservations = conn.get_all_instances()
    # print reservations

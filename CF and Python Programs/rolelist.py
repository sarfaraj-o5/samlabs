import boto3

client = boto3.client('iam',aws_access_key_id="",aws_secret_access_key="")

def lambda_handler(event, context):
    roles = client.list_roles()
    Role_list = roles['Roles']
    for key in Role_list:
        if (key['RoleName'])=='admin-access':
            print('rolename:----------')
            print(key['RoleName'])
            print(key['Arn'])
        # print(a)
        # if a=='admin-access':
            users = client.list_users()
            user_list = []
            for key in users['Users']:
                result = {}
                Policies = []
                Groups=[]
                result['userName']=key['UserName']
                List_of_Policies =  client.list_user_policies(UserName=key['UserName'])
                result['Policies'] = List_of_Policies['PolicyNames']
                List_of_Groups =  client.list_groups_for_user(UserName=key['UserName'])
                for Group in List_of_Groups['Groups']:
                    Groups.append(Group['GroupName'])
                    result['Groups'] = Groups
                    print(key)
                    
    
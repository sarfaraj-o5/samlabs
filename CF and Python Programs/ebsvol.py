# scripts delete all the ebs volumes that are in available state
import boto3
ec2 = boto3.client("ec2")
response = ec2.describe_volumes(
    Filters=[
        {
            'Name': 'status',
            'Values': [
                'available',
            ]
        },
    ]
)

for volume in response['Volumes']:
    print("Deleting Volume: " + volume['VolumeId'])
    response = ec2.delete_volume(
        VolumeId=volume['VolumeId']
    )
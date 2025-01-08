import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define the connection
ec2 = boto3.resource('ec2')

def lambda_handler(event, context):
    # Use the filter() method of the instances collection to retrieve
    # all running EC2 instances.
    filters = [{
            'Name': 'tag:AutoOnOff',
            'Values': ['True']
        },
        {
            'Name': 'instance-state-name', 
            'Values': ['stopped']
        }
    ]
    
    #filter the instances
    instances = ec2.instances.filter(Filters=filters)

    #locate all stopped instances
    StoppedInstances = [instance.id for instance in instances]
    
    #print the instances for logging purposes
    #print StoppedInstances 
    
    #make sure there are actually instances to start. 
    if len(StoppedInstances) > 0:
        #perform the startup
        startingUp = ec2.instances.filter(InstanceIds=StoppedInstances).start()
        print startingUp
    else:
        print "Nothing to see here"
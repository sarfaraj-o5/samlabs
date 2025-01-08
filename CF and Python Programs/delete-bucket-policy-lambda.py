import boto3
import json

# controls console output verbosity
DEBUG=1

s3_resource_connection = boto3.resource('s3')
s3_client_connection = boto3.client('s3')

# given a bucket policy, this returns a json document with public exposures and details
def check_policy(bucket_policy):
    if bucket_policy:
        policy = json.loads(bucket_policy)
        print('policy--------------------')
        print(policy)
        public_actions = []
        if 'Statement' in policy:
            print('hello world do u')
            for p in policy['Statement']:
                print('i m in for')
                print(p)
                if p['Effect'] == 'Allow':
                        print('hello world')
                        public_actions.append(p['Action'])
                        

        if len(public_actions) > 0:
            return {
                'public': True,
                'publicReason': 'policy',
                'public_actions': public_actions
            }
    return {
        'public': 'False'
    }

# main handler
def lambda_handler(event, context):

    # cather output in this object
    public_buckets=[]

    # iterate over buckets
    for bucket in s3_resource_connection.buckets.all():
        

        try:
            # Get the Bucket Policy
            bucketPolicy = s3_resource_connection.BucketPolicy(bucket.name)
            # did not find a better way to check if a bucket has a policy using the resource object
            bucket_policy = bucketPolicy.policy
        except Exception as e:
            # the S3 bucket does not have a bucket policy
            bucket_policy = ''

        # check bucket policy
        policyResult = check_policy(bucket_policy)

        # analyze results
        public_reasons = []
        public_acls = []
        public_actions = []

        if str(policyResult['public']) == 'True':
            public_reasons.append(policyResult['publicReason'])
            public_actions = policyResult['public_actions']
            try:
                delete_bucket_policy_response = s3_client_connection.delete_bucket_policy( Bucket=bucket.name )
                print ("%s: Bucket Policy removed" % (bucket.name))
            except:
                delete_bucket_policy_response = 'exception caught: could not delete bucket policy'
                print ("%s: *** Could not delete bucket policy ***" % (bucket.name))
        else:
            delete_bucket_policy_response={}

        if len(public_reasons) > 0:
            public_buckets.append({
                'bucket': bucket.name,
                'publicReasons': public_reasons,
                'public_acls': public_acls,
                'public_actions': public_actions,
                'bucket_policy': bucket_policy,
                'delete_bucket_policy_response': delete_bucket_policy_response
            })

            if DEBUG > 0:
                print ("------------------------ %s" % (bucket.name) )
                print (public_reasons)

                for action in public_actions:
                    print ("    %s" % (action))

    return public_buckets

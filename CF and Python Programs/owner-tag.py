import boto3
 
def list_instances_by_tag_value(tagkey, tagvalue):
    # When passed a tag key, tag value this will return a list of InstanceIds that were found.
 
    ec2client = boto3.client('ec2')
 
    response = ec2client.describe_instances(
        Filters=[
            {
                'Name': 'tag:'+tagkey,
                'Values': [tagvalue]
            }
        ]
    )
    instancelist = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist.append(instance["InstanceId"])
    return instancelist

===================================================
    # Method 1
tag_value = [tag['Value'] for tag in instance.tags if tag['Key'] == 'tag_key'][0]

# Method 2
for tag in instance.tags:
    if tag['Key'] == 'tag_key':
        tag_value = tag['Value']
        break
else:
    raise KeyError(...)


===================================================

    import boto3

def list_instances_by_tag_value(tagkey, tagvalue):
    # When passed a tag key, tag value this will return a list of InstanceIds that were found.

    ec2client = boto3.client('ec2')

    response = ec2client.describe_instances(
        Filters=[
            {
                'Name': 'tag:'+tagkey,
                'Values': [tagvalue]
            }
        ]
    )
    instancelist = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist.append(instance["InstanceId"])
    return instancelist

    =================================================================

    #!/bin/python
import boto.ec2

# production instances
production = [
    'srv1', 'srv2', 'srv3', 'srv4', 'srv5', 'srv6', 'srv7', 'srv9', 'srv9',
    ]

# currently not used
def send_alert_gmail():
   import smtplib

   # Specifying the from and to addresses

   fromaddr = 'khong@gmail.com'
   toaddrs  = 'khong@gmail.com'

   # Writing the message (this message will appear in the email)

   msg = 'Testing 2'

   # Gmail Login

   username = 'khong@gmail.com'
   password = '********'

   # Sending the mail

   server = smtplib.SMTP('smtp.gmail.com:587')
   server.starttls()
   server.login(username,password)
   server.sendmail(fromaddr, toaddrs, msg)
   server.quit()

# currently using this mandrill smtp
def send_alert_mandrill(message):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart('alternative')

    msg['Subject'] = "AWS Alert: stopped production instance"
    msg['From']    = "from@yourcompany.com"
    msg['To']      = "to@yourcompany.com"

    text = message
    part1 = MIMEText(text, 'plain')

    html = message
    part2 = MIMEText(html, 'html')

    username = "smtp@yourcompany.com"
    password = "******"

    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP('smtp.mandrillapp.com', 587)

    s.login(username, password)
    s.sendmail(msg['From'], msg['To'], msg.as_string())

    s.quit()

# polling all instances
# if the stopped instance is for production, sends an alert email with instance info
def polling():
    conn = boto.ec2.connect_to_region('us-west-1')
    reservations = conn.get_all_reservations()

    for r in reservations:
        for i in r.instances:
            if 'Name' in i.tags:
               # check a stopped instance is for production
               if i.state == 'stopped' and i.tags['Name'] in production:
                  # if it is, sends an alert email
                  print "production:  %s (%s) [%s]" % (i.tags['Name'], i.id, i.state)
                  message = str(i.tags['Name']) + ' (' + str(i.id) + ') ' + '[' + str(i.state) + ']'
                  send_alert_mandrill(message)
               else:
                  print "Non-production:  %s (%s) [%s]" % (i.tags['Name'], i.id, i.state)

            else:
               print "%s [%s]" % (i.id, i.state)

if __name__ == '__main__':
    '''
    How it works : should work with cron. For example,
    */30 * * * *  /usr/bin/python /home/ubuntu/EC2/detecting_stopped_production_instances.py
    '''
    polling()
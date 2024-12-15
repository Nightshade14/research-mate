import boto3
import json
import urllib.parse

# Initialize clients
sqs = boto3.client('sqs', region_name='us-west-2')
ses = boto3.client('ses')

# Replace with your queue URL
QUEUE_URL = 'https://sqs.us-west-2.amazonaws.com/992382724291/UserEmailQueue'

# Replace with your SES verified sender email
SES_SENDER = 'siddharthcv77@gmail.com'

# API Gateway URL where the user will be redirected for activation
API_GATEWAY_URL = 'https://qjxccgwt9f.execute-api.us-east-1.amazonaws.com/prod/link-action'

# Dummy message details
SUBJECT = 'Welcome to Our Service!'
BODY_TEXT = 'Hello,\n\nThank you for joining our service!\n\nClick the link to activate your email: {}'
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Welcome to Our Service!</h1>
  <p>Thank you for joining our service!</p>
  <p><a href="{}">Click here to activate your email</a></p>
</body>
</html>
"""

def send_email(recipient_email, activation_link):
    """
    Sends an email to the recipient using Amazon SES with the activation link.
    """
    try:
        # Update the email body to include the activation link
        body_text = BODY_TEXT.format(activation_link)
        body_html = BODY_HTML.format(activation_link)
        
        response = ses.send_email(
            Source=SES_SENDER,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': SUBJECT,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': body_html,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print(f"Email sent to {recipient_email}, Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {str(e)}")

def lambda_handler(event, context):
    try:
        # Receive message from SQS queue
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,  # Adjust based on batch size
            WaitTimeSeconds=10       # Long polling
        )

        print('queue response: ', response)

        # Check if messages exist
        if 'Messages' in response:
            for message in response['Messages']:
                # Extract and log the email
                print(f"Processing message: {message['Body']}")
                email_data = json.loads(message['Body'])
                recipient_email = email_data.get('email')

                if recipient_email:
                    # Create the activation link with the email query parameter
                    encoded_email = urllib.parse.quote(recipient_email)  # URL-encode the email address
                    activation_link = f"{API_GATEWAY_URL}?email={encoded_email}"

                    # Send email with the activation link
                    send_email(recipient_email, activation_link)

                    # Delete the message from the queue after processing
                    sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    print("Message deleted")
                else:
                    print("No email found in message body")
        else:
            print("No messages to process")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e

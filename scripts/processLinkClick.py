import boto3
import json
import re
from boto3.dynamodb.conditions import Key

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

# Replace with your DynamoDB table name
DYNAMODB_TABLE_NAME = 'research_user_table'

def lambda_handler(event, context):
    print("Received event: ", json.dumps(event, indent=2))  # Log the event to inspect the structure
    
    try:
        email_id = None  # Initialize email variable
        
        # Check if queryStringParameters exists and is a string
        if 'queryStringParameters' in event and isinstance(event['queryStringParameters'], str):
            query_string = event['queryStringParameters']
            
            # Extract the email using regex
            match = re.search(r'email=([^,}]+)', query_string)
            if match:
                email_id = match.group(1)  # Extract the email value
            
        # Log the extracted email ID
        print(f"Extracted email ID: {email_id}")

        if email_id:
            # Access the DynamoDB table
            table = dynamodb.Table(DYNAMODB_TABLE_NAME)

            print('email: ', email_id)

            # Update the 'active' field to 1 for the given email_id
            # response = table.update_item(
            #     Key={'email': email_id},
            #     UpdateExpression="SET #active = :activeValue",
            #     ExpressionAttributeNames={
            #         '#active': 'active'  # Attribute name to update
            #     },
            #     ExpressionAttributeValues={
            #         ':activeValue': 1  # New value for 'active'
            #     },
            #     ReturnValues="UPDATED_NEW"  # Return the updated attributes
            # )

            # Step 1: Query the item based on the 'email' partition key
            response = table.query(
                KeyConditionExpression=Key('email').eq(email_id)  # Query using 'email'
            )

            # Step 2: Check if an item is returned and perform the update
            if 'Items' in response and response['Items']:
                # Since we know it will only return one row, get the first item
                item = response['Items'][0]  # Only one item is expected

                # Extract the user_id from the item
                user_id = item['user_id']  # Assuming 'user_id' is part of the item

                # Step 3: Perform the update using the email and user_id
                update_response = table.update_item(
                    Key={
                        'email': email_id,        # Partition key
                        'user_id': user_id        # Sort key (from the query result)
                    },
                    UpdateExpression="SET #active = :activeValue",  # Set the 'active' attribute
                    ExpressionAttributeNames={
                        '#active': 'active'  # Attribute name to update
                    },
                    ExpressionAttributeValues={
                        ':activeValue': 1  # New value for 'active'
                    },
                    ReturnValues="UPDATED_NEW"  # Return the updated attributes
                )

                # Print the updated attributes
                print("Updated item:", update_response['Attributes'])

            else:
                print("Item not found.")  # In case no item matches

                
            # Step 2: Check if any items are returned and then update the first match

            # response = table.query(
            #     KeyConditionExpression=Key('email').eq(email_id)  # Only use 'email' as the partition key
            # )

            # # Check if any items are returned
            # if 'Items' in response and response['Items']:
            #     for item in response['Items']:
            #         print(item)  # Print all items matching the 'email'
            # else:
            #     print("Item not found.")  # In case no item matches


            print('email again: ', email_id)

            # Log the update response
            print(f"Update response: {response}")

            # Return a successful response
            return {
                'statusCode': 200,
                'body': json.dumps({'message': f'Email {email_id} activated successfully!'})
            }
        else:
            print("No email parameter found in the request")

            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Email parameter is missing'})
            }

    except Exception as e:
        # Log any error for debugging purposes
        print(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error activating email'})
        }

import json
import boto3

dynamodb = boto3.client('dynamodb', region_name='ap-northeast-2')

def lambda_handler(event, context):

    if 'body' in event:
        body = json.loads(event['body'])
        if 'ticketId' in body:
            ticket_id = body['ticketId']
    
    if not ticket_id:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'incoming request did not have a ticket id'
            })
        }
        return response
    
    dynamo_db_request_params = {
        'TableName': 'MatchmakingTickets',
        'Key': {
            'Id': {'S': ticket_id}
        }
    }
    
    try:
        data = dynamodb.get_item(**dynamo_db_request_params)
        ticket = data.get('Item', None)
        
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'ticket': ticket
            })
        }
    except Exception as e:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(e)
            })
        }
    
    return response

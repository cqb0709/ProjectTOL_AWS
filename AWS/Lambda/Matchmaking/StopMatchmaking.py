import json
import boto3

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
    
    game_lift = boto3.client('gamelift', region_name='ap-northeast-2')
    
    game_lift_request_params = {
        'TicketId': ticket_id
    }
    
    try:
        game_lift.stop_matchmaking(**game_lift_request_params)
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'success': 'matchmaking request has been cancelled'
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

import json
import boto3
import os
from datetime import datetime, timedelta

dynamodb = boto3.client('dynamodb', region_name='ap-northeast-2')

def lambda_handler(event, context):
    
    if 'Records' in event and len(event['Records']) > 0:
        record = event['Records'][0]
        if 'Sns' in record and 'Message' in record['Sns']:
            print('Message from GameLift: ' + record['Sns']['Message'])
            message = json.loads(record['Sns']['Message'])
    
    if not message or message.get('detail-type') != 'GameLift Matchmaking Event':
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'No message available or message is not about GameLift matchmaking'
            })
        }
        return response
    
    message_detail = message['detail']
    
    if 'tickets' not in message_detail or len(message_detail['tickets']) == 0:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'No tickets found'
            })
        }
        return response
    
    dynamo_db_request_params = {
        'RequestItems': {
            'MatchmakingTickets': []
        }
    }
    
    if message_detail['type'] in ['MatchmakingSucceeded', 'MatchmakingTimedOut', 'MatchmakingCancelled', 'MatchmakingFailed']:
        for ticket in message_detail['tickets']:
            ticket_item = {
                'Id': {'S': ticket['ticketId']},
                'Type': {'S': message_detail['type']},
                'ttl': {'N': str(int(datetime.now().timestamp()) + 3600)}
            }
            
            if message_detail['type'] == 'MatchmakingSucceeded':
                players = ticket['players']
                player_items = []
                
                for player in players:
                    player_item = {
                        'M': {
                            'PlayerId': {'S': player['playerId']}
                        }
                    }
                    if 'playerSessionId' in player:
                        player_item['M']['PlayerSessionId'] = {'S': player['playerSessionId']}
                    
                    player_items.append(player_item)
                
                ticket_item['Players'] = {'L': player_items}
                ticket_item['GameSessionInfo'] = {
                    'M': {
                        'IpAddress': {'S': message_detail['gameSessionInfo']['ipAddress']},
                        'Port': {'N': str(message_detail['gameSessionInfo']['port'])}
                    }
                }
            
            dynamo_db_request_params['RequestItems']['MatchmakingTickets'].append({
                'PutRequest': {
                    'Item': ticket_item
                }
            })
    
    try:
        dynamodb.batch_write_item(**dynamo_db_request_params)
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'success': 'Ticket data has been saved to DynamoDB'
            })
        }
    except Exception as err:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(err)
            })
        }
    
    return response

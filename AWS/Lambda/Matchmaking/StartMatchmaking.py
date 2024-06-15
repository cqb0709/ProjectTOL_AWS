import json
import boto3
from botocore.exceptions import ClientError

# AWS Lambda와 GameLift 클라이언트를 초기화
lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
gamelift_client = boto3.client('gamelift', region_name='ap-northeast-2')

def lambda_handler(event, context):
    raised_error = None
    latency_map = None

    # 이벤트의 body에서 latencyMap을 추출
    if 'body' in event:
        body = json.loads(event['body'])
        if 'latencyMap' in body:
            latency_map = body['latencyMap']

    # latencyMap이 없으면 400 상태 코드를 반환
    if not latency_map:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'incoming request did not have a latency map'
            })
        }
        return response

    # GetPlayerData Lambda 함수를 호출하기 위한 매개변수 설정
    lambda_request_params = {
        'FunctionName': 'api-get-userinfo',
        'Payload': json.dumps(event)
    }

    # Lambda 함수를 호출하여 플레이어 데이터를 가져옴
    try:
        lambda_response = lambda_client.invoke(**lambda_request_params)
        if 'Payload' in lambda_response:
            payload = json.loads(lambda_response['Payload'].read())
            if 'body' in payload:
                payload_body = json.loads(payload['body'])
                player_data = payload_body.get('playerData')
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

    if not player_data:
        response = {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'unable to retrieve player data'
            })
        }
        return response

    # 플레이어 ID와 경기 결과를 바탕으로 총 경기 수와 기술 점수를 계산
    player_id = player_data['SUB']['S']
    player_wins = int(player_data['WIN']['N'])
    player_losses = int(player_data['LOSE']['N'])
    total_games_played = player_wins + player_losses

    player_skill = 50 if total_games_played < 1 else (player_wins / total_games_played) * 100

    # GameLift 매치메이킹 요청을 위한 매개변수 설정
    gamelift_request_params = {
        'ConfigurationName': 'testmatchmaking',
        'Players': [{
            'LatencyInMs': latency_map,
            'PlayerId': player_id,
            'PlayerAttributes': {
                'skill': {
                    'N': player_skill
                }
            }
        }]
    }

    # 매치메이킹 요청을 콘솔에 출력
    print('matchmaking request: ' + json.dumps(gamelift_request_params))

    # GameLift 매치메이킹 요청을 시작하고 티켓 ID를 반환
    try:
        gamelift_response = gamelift_client.start_matchmaking(**gamelift_request_params)
        ticket_id = gamelift_response.get('MatchmakingTicket', {}).get('TicketId')
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'ticketId': ticket_id
            })
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

    return response

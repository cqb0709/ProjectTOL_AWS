import json
import boto3


def delete_account(event, context):
    try:
        # API Gateway로부터 전달된 요청 데이터 가져오기
        request_body = json.loads(event['body'])

        # 필요한 정보 추출
        Access_Token = request_body.get('accessToken')
        response = client.delete_user(
            AccessToken=Access_Token
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User Deleted Successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

import json
import boto3
from botocore.exceptions import ClientError

def login(event, context):
    try:
        # API Gateway로부터 전달된 요청 데이터 가져오기
        request_body = json.loads(event['body'])

        # 필요한 정보 추출
        username = request_body.get('username')
        password = request_body.get('password')
    
        
        cognito_client = boto3.client('cognito-idp')
        # Cognito에 로그인 요청
        response = cognito_client.initiate_auth(
            ClientId='42hq5nf0hvrfjni1ufltb1bamd',
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        # 로그인 성공 시 JWT 토큰 반환
        jwt_token = response['AuthenticationResult']['IdToken']
        return {
            'statusCode': 200,
            'body': json.dumps({'token': jwt_token})
        }
    except ClientError as e:
        # 로그인 실패 시 에러 메시지 반환
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

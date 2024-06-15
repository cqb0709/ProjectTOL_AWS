import json
import boto3

def register(event, context):
    try:
        # API Gateway로부터 전달된 요청 데이터 가져오기
        request_body = json.loads(event['body'])

        # 필요한 정보 추출
        username = request_body.get('username')
        password = request_body.get('password')
        email = request_body.get('email')
        
        # 사용자를 Cognito 사용자 풀에 등록
        cognito_client = boto3.client('cognito-idp')
        response = cognito_client.sign_up(
            ClientId='<YourCognitoClientID>',
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email}
            ]
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Registration successful'})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

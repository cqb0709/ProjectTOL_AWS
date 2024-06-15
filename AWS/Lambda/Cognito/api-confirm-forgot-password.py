import json
import boto3

def confirm_forgot_password(event, context):
    try:
        # API Gateway로부터 전달된 요청 데이터 가져오기
        request_body = json.loads(event['body'])

        # 필요한 정보 추출
        username = request_body.get('username')
        confirmation_code = request_body.get('confirmationCode')
        password=request_body.get('NewPassword')

        # AWS Cognito 클라이언트 생성
        cognito_client = boto3.client('cognito-idp')

        # 확인 코드 확인
        response = cognito_client.confirm_forgot_password(
            ClientId='<YourCognitoClientID>',
            Username=username,
            ConfirmationCode=confirmation_code,
            Password=password
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Password Successfully Reset'})
        }
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid reset code'})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

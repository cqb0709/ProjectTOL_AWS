import json
import boto3


def confirm_registration(event, context):
    try:
        # API Gateway로부터 전달된 요청 데이터 가져오기
        request_body = json.loads(event['body'])

        # 필요한 정보 추출
        username = request_body.get('username')
        confirmation_code = request_body.get('confirmationCode')
        
        
        cognito_client = boto3.client('cognito-idp')
        response = cognito_client.confirm_sign_up(
            ClientId='<YourCognitoClientID>',
            Username=username,
            ConfirmationCode=confirmation_code
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Registration confirmation successful'})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

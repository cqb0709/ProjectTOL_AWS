import json
import boto3


def forgot_password(event, context):
    try:
        # API Gateway로부터 전달된 요청 데이터 가져오기
        request_body = json.loads(event['body'])

        # 필요한 정보 추출
        username = request_body.get('username')
        
        
        cognito_client = boto3.client('cognito-idp')
        response = cognito_client.forgot_password(
            ClientId='<YourCognitoClientID>',
            Username=username
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Password reset initiated successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

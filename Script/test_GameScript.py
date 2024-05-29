import json
import boto3
from botocore.exceptions import ClientError

def login(event, context):
    try:
        # API Gateway�κ��� ���޵� ��û ������ ��������
        request_body = json.loads(event['body'])

        # �ʿ��� ���� ����
        username = request_body.get('username')
        password = request_body.get('password')
    
        
        cognito_client = boto3.client('cognito-idp')
        # Cognito�� �α��� ��û
        response = cognito_client.initiate_auth(
            ClientId='42hq5nf0hvrfjni1ufltb1bamd',
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        # �α��� ���� �� JWT ��ū ��ȯ
        jwt_token = response['AuthenticationResult']['IdToken']
        return {
            'statusCode': 200,
            'body': json.dumps({'token': jwt_token})
        }
    except ClientError as e:
        # �α��� ���� �� ���� �޽��� ��ȯ
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

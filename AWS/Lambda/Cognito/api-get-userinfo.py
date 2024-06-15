import json
import boto3
import jwt
#JWT 라이브러리를 람다에 같이 업로드하여 사용

def query_userinfo(dynamodb, sub, username):
    response = dynamodb.get_item(
        TableName='<YourDynamoDBName>',
        Key={
            'SUB': {'S': sub},  # 파티션 키(Cognito UserPool의 개인 SUB 필드 활용)
            'username': {'S': username}  # 정렬 키
        }
    )
    return response.get('Item')


def add_new_item(dynamodb, sub, username):
    new_item = {
        'SUB': {'S': sub},
        'username': {'S': username},
        'WIN': {'N': '0'},
        'LOSE': {'N': '0'}
    }
    dynamodb.put_item(
        TableName='<YourDynamoDBName>',
        Item=new_item
    )
    return new_item



        
#Handler
def get_userinfo(event, context):
    try:
        # 헤더에서 ID토큰 추출
        IDtoken = event['headers'].get('Authorization')


        # JWT Decoding
        decoded_token = jwt.decode(IDtoken, options={"verify_signature": False})
        sub = decoded_token['sub']
        username = decoded_token['cognito:username']

        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb')
    

        # Extract user info from DynamoDB response
        user_info = query_userinfo(dynamodb, sub, username)

        if user_info:
            return {
                'statusCode': 200,
                'body': json.dumps({"playerData": user_info})
            }
        else:
            new_user_info = add_new_item(dynamodb, sub, username)
            return {
                'statusCode': 200,
                'body': json.dumps({"playerData": new_user_info})
            }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

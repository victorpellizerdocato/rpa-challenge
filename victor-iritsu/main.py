import json
from src.challenge.ChallengeServiceHandler import ChallengeServiceHandler

def lambda_handler(event, context):
    challenge = ChallengeServiceHandler()

    print("Starting bot execution")
    for package in event['Packages']:
        print(f"Execution params: {package}")
        challenge.handler(package)

    print("Bot execution finished.")

    return {
        'statusCode': 200,
        'body': json.dumps('Mensagens processadas e excluídas com sucesso!')
    }
lambda_handler({
    'Packages': [
        {
            "query": "Javier Milei",
            "topic": "Politics",
            "months_delta": 10
        },
        {
            "query": "Bad Bunny",
            "topic": "Music",
            "months_delta": 2
        },
        {
            "query": "Dwayne Johnson",
            "topic": "Entertainment & Arts",
            "months_delta": 1
        },
        {
            "query": "COVID",
            "topic": "Politics",
            "months_delta": 12
        },
    ]
},0)

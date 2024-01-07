import json
from src.challenge.ChallengeServiceHandler import ChallengeServiceHandler
from robocorp.tasks import task

@task
def solve_challenge():
    challenge = ChallengeServiceHandler()
    input_json = json.load(open("./input_data.json"))

    print("Starting bot execution")
    for package in input_json['Packages']:
        print(f"Execution params: {package}")
        challenge.handler(package)

    print("Bot execution finished.")
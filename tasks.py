import json
from src.challenge.ChallengeServiceHandler import ChallengeServiceHandler
from robocorp.tasks import task
from robocorp import workitems

@task
def solve_challenge():
    challenge = ChallengeServiceHandler()

    print("Starting bot execution")
    for work_item in workitems.inputs:
        print(f"Execution params: {work_item.payload}")
        challenge.handler(work_item.payload)

    print("Bot execution finished.")
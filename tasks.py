import logging
from robocorp import workitems
from robocorp.tasks import task
from src.challenge.ChallengeServiceHandler import ChallengeServiceHandler


@task
def solve_challenge():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    challenge = ChallengeServiceHandler()

    logging.info("Starting bot execution")
    for work_item in workitems.inputs:
        logging.info(f"Execution params: {work_item.payload}")
        challenge.handler(work_item.payload)

    logging.info("Bot execution finished.")

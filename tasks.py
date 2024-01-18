import logging

from robocorp import workitems
from robocorp.tasks import task

from src.LATimesService import LATimesService


@task
def solve_challenge():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    challenge = LATimesService()

    logging.info("Starting bot execution")
    for work_item in workitems.inputs:
        logging.info(f"Execution params: {work_item.payload}")
        exec_response = challenge.exec(payload=work_item.payload)
        if exec_response.get('success'):
            logging.info("The bot executed successfully.")

    logging.info("Bot execution finished.")

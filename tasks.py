"""

> Packages used to start the robot execution

logging - logs every relevant step
workitems - supplies the bot with external payload
task - defines the task to be accessed by the framework
LATimesService - class to scrape LATimes website

"""
import logging

from robocorp import workitems
from robocorp.tasks import task

from src.LATimesService import LATimesService


@task
def solve_challenge():
    """
    Defines the logging config, instantiates the main class,
    and executes the robot for N payloads.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    challenge = LATimesService()

    logging.info("Starting bot execution")
    for work_item in workitems.inputs:
        logging.info("Execution params: %s", work_item.payload)
        exec_response = challenge.exec(payload=work_item.payload)
        if exec_response.get('success'):
            logging.info("The bot executed successfully.")

    logging.info("Bot execution finished.")

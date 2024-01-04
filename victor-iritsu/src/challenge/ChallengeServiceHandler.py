from src.challenge.utils.data_handling import DataHandling
from src.challenge.ChallengeService import ChallengeService


class ChallengeServiceHandler:
    def __init__(
        self
    ):
        self.data_handling = DataHandling

    def handler(
        self,
        pacote
    ):
        challenge = ChallengeService(
            data_handling=self.data_handling
        )
        challenge.exec_robots(pacote)
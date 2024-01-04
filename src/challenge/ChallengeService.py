from src.challenge.utils.data_handling import DataHandling
from src.challenge.systems.latimes.LATimesService import LATimes


class ChallengeService():
    def __init__(
        self,
        data_handling: DataHandling
    ):
        self.data_handling = data_handling
        self.la_times = LATimes(
            data_handling=self.data_handling
        )

    def exec_robots(
        self,
        package: dict
    ):
        systems = {
            'LATimes': self.la_times
        }
        for system in systems:
            print(f"Extracting info from {system}.")
            exec_response = systems[system].exec(package)
            if not exec_response.get('success'):
                print(f"The robot failed to extract info from {system}.")
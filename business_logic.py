import re
from logger import logger


class BusinessLogic:

    @logger.catch
    def extract_first_digit(self, message):
        try:
            match = re.search(r'\d+', message)  # Ищет первую цифру в строке
            # Возвращает найденную цифру как целое число
            return int(match.group(0))
        except (AttributeError, ValueError):
            return 0

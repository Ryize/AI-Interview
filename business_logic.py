import re


class BusinessLogic:
    @staticmethod
    def extract_first_digit(message):
        try:
            match = re.search(r'\d+', message)  # Ищет первую цифру в строке
            # Возвращает найденную цифру как целое число
            return int(match.group(0))
        except (AttributeError, ValueError):
            return 0

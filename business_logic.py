import re


class BusinessLogic:
    
	@staticmethod
	def extract_first_digit(message):
		match = re.search(r'\d', message)  # Ищет первую цифру в строке
		if match:
			return int(match.group(0))  # Возвращает найденную цифру как целое число
		return None
	



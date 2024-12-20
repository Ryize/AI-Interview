import os
import requests
import json
from dotenv import load_dotenv
from logger import logger


class Interview:
    """
    Класс для проведения интервью на знание Python.

    Класс использует OpenAI API для сравнения эталонного ответа с ответом
    пользователя и выставления оценки по 10-бальной шкале.

    Attributes:
        client: Объект клиента OpenAI, инициализируется с помощью API токена.
        description (str): Инструкция для оценки ответов.
        question (str): Вопрос, на который нужно ответить.
        reference_answer (str): Эталонный ответ.
        user_answer (str): Ответ пользователя.
    """

    client = None
    description = """
                   Ты проводишь собеседование на знание языка программирования
                   Python.
                   На вход получаешь два ответа на вопрос, эталонный и ответ,
                   который нужно проверить.
                   Сравни их по смыслу. Выстави оценку за правильность ответа
                   по 10-бальной шкале.
                   Будь снисходителен: ответ не должен точно повторять
                   эталонный, должны быть похожи основные мысли.
                   Не снижай оценку за структуру ответа, его краткость или
                   многословность.
                   Главное, чтобы в представленном ответе хоть как-то
                   упоминалисьтезисы из эталонного ответа!
                   Если все мысли похожи — это максимальный балл.
                   Не снижай оценку за грамотность и форматирование ответа.
                   Полное несовпадение — 0 баллов.
                   Верна основная мысль — от 2 до 6 баллов.
                   Верна основная мысль и дополнительные мысли — от 6 до 10
                   баллов.
                   Не пиши о сравнении с эталонным ответом.
                   Не снижай оценку за отсутствие второстепенных данных.
                   Начни без вступления — сразу с оценки и того, что можно
                   добавить к ответу.
                   Оценку пиши так: "Ваша оценка: число(оценка)"
                  """

    def __init__(self, question, reference_answer, user_answer) -> None:
        """
        Инициализация объекта класса Interview.

        Args:
            question (str): Вопрос для собеседования.
            reference_question (str): Эталонный ответ на вопрос.
            user_question (str): Ответ пользователя.
        """
        load_dotenv()
        self.token = os.getenv('GPT_TOKEN')
        self.question = question
        self.reference_answer = reference_answer
        self.user_answer = user_answer
        self.user_request = self.user_request()

    @logger.catch
    def user_request(self):
        if self.reference_answer:
            return f'Вопрос: {self.question}.' \
                   f'Эталонный ответ: {self.reference_answer}' \
                   f'Ответ: {self.user_answer}'
        else:
            return f'Вопрос: {self.question}.' \
                   f'Ответ: {self.user_answer}'

    @logger.catch
    def get_response(self) -> str:
        """
        Выполняет запрос к OpenAI API для оценки ответа пользователя.

        Формирует запрос к модели с инструкцией по оценке ответа пользователя.

        Returns:
            str: Оценка ответа пользователя, сгенерированная OpenAI.
        """

        # Заголовки запроса
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

        # Данные запроса
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": self.description},
                {"role": "user", "content": self.user_request}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }

        proxies = {
            "https": "http://1zhPU6Rq:aafJcerK@194.87.117.211:63692"
        }

        # Отправка POST-запроса к API
        response = requests.post('https://api.openai.com/v1/chat/completions',
                                 headers=headers, data=json.dumps(data),
                                 proxies=proxies)

        # Обработка ответа
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code}\n{response.text}"


class InterviewThisOutReferensAnswer(Interview):
    """
    По смылу полностью повторяет класс Interview,
    но не использует эталонный ответ.
    """
    description = """
                   Ты проводишь собеседование на знание языка программирования
                   Python. На вход получаешь вопрос и ответ пользователя.
                   Сформируй эталонный ответ на вопрос и сравните его с ответом
                   пользователя.
                   Сравни их по смыслу. Выстави оценку за правильность ответа
                   по 10-бальной шкале.
                   Будь снисходителен: ответ не должен точно повторять
                   эталонный, должны быть похожи основные мысли.
                   Не снижай оценку за структуру ответа, его краткость или
                   многословность.
                   Главное, чтобы в представленном ответе хоть как-то
                   упоминались тезисы из эталонного ответа!
                   Если все мысли похожи — это максимальный балл.
                   Не снижай оценку за грамотность и форматирование ответа.
                   Полное несовпадение — 0 баллов.
                   Верна основная мысль — от 2 до 6 баллов.
                   Верна основная мысль и дополнительные мысли — от 6 до 10
                   баллов.
                   Не пиши о сравнении с эталонным ответом.
                   Не снижай оценку за отсутствие второстепенных данных.
                   Начни без вступления — сразу с оценки и того, что можно
                   добавить к ответу.
                   Оценку пиши так: "Ваша оценка: число(оценка)"
                  """

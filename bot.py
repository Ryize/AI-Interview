import telebot
from keyboard_mixin import KeyboardMixin
from models import DataAccess
from ai_logic import Interview, InterviewThisOutReferensAnswer
from business_logic import BusinessLogic
import os
from dotenv import load_dotenv
from telebot import types
from logger import logger

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)
kb = KeyboardMixin()
data_access = DataAccess()
bussiness_logic = BusinessLogic()

temp_data = {}
interview_data = {}
interview_question = {}


@logger.catch
@bot.message_handler(commands=['start', 'help'])
def start(message):
    try:
        login = str(message.from_user.id)
        data_access.add_user(login)
        bot.send_message(message.chat.id,
                         f'Привет, {message.from_user.first_name}, начнем!',
                         reply_markup=kb.main_menu())

    except AttributeError:
        bot.send_message(
            message.chat.id,
            'Ошибка при получении данных пользователя, перезапустите бот')
    except telebot.apihelper.ApiException:
        bot.send_message(
            message.chat.id,
            'Ошибка при отправке сообщения, перезапустите бот')
    except Exception:
        bot.send_message(
            message.chat.id,
            'Произошла непредвиденная ошибка, перезапустите бот')


# Обработчик нажатия на кнопку "Информация"
@logger.catch
@bot.message_handler(func=lambda message: message.text == 'Информация 📚')
def info(message):
    bot.send_message(
        message.chat.id,
        'Этот бот предоставляет комплексную подготовку к собеседованию по '
        'языку Python, Django и принципам объектно-ориентированного '
        'программирования (ООП). Он генерирует вопросы различной сложности, '
        'оценивает ответы пользователя и предоставляет обратную связь для '
        'улучшения навыков. На день у вас есть 10 попыток ответить на вопросы.'
        'Каждый день количество попыток обновляется до 10. В профилке вы '
        'можете наблюдать колличество попыток и прогресс обучения. Вопрос вам '
        'засчитывается, если вы ответили на 7 баллов и выше. В начале все '
        'вопросы будут уникальными, после будут повторяться вопросы, ниже '
        'проходного балла, до тех пор пока все вопросы не будут зачтены.')


# Обработчик нажатия на кнопку "Профиль"
@logger.catch
@bot.message_handler(func=lambda message: message.text == 'Ваш профиль 🧑')
def profile(message):
    user = data_access.get_user(message.from_user.id)
    limit = user.question_limit
    progress_python_trainee = data_access.get_progress_Python(user.id)[0]
    progress_python_junior = data_access.get_progress_Python(user.id)[1]
    progress_python_middle = data_access.get_progress_Python(user.id)[2]
    progress_django = data_access.get_progress_topic(user.id, 'Django')
    progress_oop = data_access.get_progress_topic(user.id, 'ООП')
    bot.send_message(
        message.chat.id,
        f'Сегодня у вас осталось {limit} попыток.\n'
        f'Прогресс изучения Python(trainee): {progress_python_trainee}%\n'
        f'Прогресс изучения Python(junior): {progress_python_junior}%\n'
        f'Прогресс изучения Python(middle): {progress_python_middle}%\n'
        f'Прогресс изучения Django: {progress_django}%\n'
        f'Прогресс изучения ООП: {progress_oop}%')


@logger.catch
@bot.message_handler(
        func=lambda message: message.text == 'Выбрать тему для вопросов 🧑‍💻')
def ai_interview_topics(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Выберите тему для собеседования:',
                     reply_markup=kb.topics_kb(True))
    bot.register_next_step_handler(message, ai_interview_question)


# Обработчик выбора темы для AI Собес
@logger.catch
def ai_interview_question(message):
    chat_id = message.chat.id
    login = message.from_user.id
    if message.text == 'Назад':
        bot.send_message(chat_id, 'Возвращаемся в главное меню',
                         reply_markup=kb.main_menu())
        return

    interview_data[chat_id] = {}
    if message.text == 'Python(trainee)':
        interview_data[chat_id]['topic'] = 'Python'
        interview_data[chat_id]['difficulty'] = 'trainee'
        get_question(message, login, chat_id, 'Python', 'trainee')
    elif message.text == 'Python(junior)':
        interview_data[chat_id]['topic'] = 'Python'
        interview_data[chat_id]['difficulty'] = 'junior'
        get_question(message, login, chat_id, 'Python', 'junior')
    elif message.text == 'Python(middle)':
        interview_data[chat_id]['topic'] = 'Python'
        interview_data[chat_id]['difficulty'] = 'middle'
        get_question(message, login, chat_id, 'Python', 'middle')
    elif message.text == 'Django':
        interview_data[chat_id]['topic'] = 'Django'
        interview_data[chat_id]['difficulty'] = None
        get_question(message, login, chat_id, 'Django')
    elif message.text == 'ООП':
        interview_data[chat_id]['topic'] = 'ООП'
        interview_data[chat_id]['difficulty'] = None
        get_question(message, login, chat_id, 'ООП')


@logger.catch
def get_question(message, login, chat_id, topic, difficulty=None):
    user = data_access.get_user(login)
    data_access.check_date(user)  # Обновляем колличество вопросов на день
    question = data_access.get_random_unanswered_question(
        user.login, topic, difficulty)
    if question:
        if question == -1:
            bot.send_message(
                chat_id,
                'Колличество попыток иссякло, завтра можно продолжить',
                reply_markup=kb.main_menu())
        elif question == -2:
            if difficulty:
                bot.send_message(
                    chat_id, 'Вы ответили на все вопросы правильно!'
                    f'\nПоздравляю! Вы прошли интервью по {topic}({difficulty})! 🎉',
                    reply_markup=kb.main_menu())
            else:
                bot.send_message(
                    chat_id, 'Вы ответили на все вопросы правильно!'
                    f'\nПоздравляю! Вы прошли интервью по {topic}! 🎉',
                    reply_markup=kb.main_menu())
        else:
            interview_question[chat_id] = {'question': question}
            bot.send_message(chat_id, 'Ответьте на вопрос:')
            bot.send_message(
                chat_id, question.question,
                reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(
                message, ai_interview_receive_answer)
    else:
        bot.send_message(chat_id, 'Произошла ошибка, попробуйте заново!')


@logger.catch
def ai_interview_receive_answer(message):
    chat_id = message.chat.id
    user_answer = message.text  # Ответ пользователя
    login = message.from_user.id

    msg = bot.send_message(chat_id, '⚙️ Ожидание...')

    question = interview_question[chat_id]['question'].question
    question_id = int(interview_question[chat_id]['question'].id)
    reference_answer = interview_question[chat_id]['question'].answer

    if reference_answer:
        answer_gpt = Interview(question, reference_answer, user_answer). \
            get_response()
    else:
        answer_gpt = InterviewThisOutReferensAnswer(
            question, reference_answer, user_answer).get_response()

    score = bussiness_logic.extract_first_digit(answer_gpt)
    data_access.save_progress(login, question_id, user_answer, score)

    bot.edit_message_text(chat_id=chat_id,
                          message_id=msg.message_id,
                          text=answer_gpt,
                          reply_markup=kb.interview_menu())


# Добавляем обработчик для инлайн-кнопки
@logger.catch
@bot.callback_query_handler(func=lambda call: call.data == "next_question")
def callback_next_question(call):
    chat_id = call.message.chat.id
    login = call.from_user.id
    topic = interview_data[chat_id]['topic']
    difficulty = interview_data[chat_id]['difficulty']
    get_question(call.message, login, chat_id, topic, difficulty)

    # Удаляем инлайн-кнопку после нажатия
    bot.edit_message_reply_markup(chat_id=chat_id,
                                  message_id=call.message.message_id,
                                  reply_markup=None)


@logger.catch
@bot.callback_query_handler(func=lambda call: call.data == "topic")
def call_back_main_menu(call):
    bot.send_message(call.message.chat.id,
                     'Выберите тему для собеседования:',
                     reply_markup=kb.topics_kb(True))
    bot.register_next_step_handler(call.message, ai_interview_question)


@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def callback_main_menu(call):
    bot.send_message(call.message.chat.id, 'Возвращаемся в главное меню',
                     reply_markup=kb.main_menu())


# Обработчик неизвестных команд
@logger.catch
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.send_message(
        message.chat.id,
        '🧐 Неизвестная команда. Выберите одну из предложенных опций.',
        reply_markup=kb.main_menu())


# Запуск бота
if __name__ == '__main__':
    print('Бот запущен')
    while True:
        try:
            bot.polling()
        except Exception:
            continue

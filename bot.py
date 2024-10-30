import telebot
from keyboard_mixin import KeyboardMixin
from models import DataAccess
from ai_logic import Interview, InterviewThisOutReferensAnswer
from business_logic import BusinessLogic
import os
from dotenv import load_dotenv
from telebot import types

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)
kb = KeyboardMixin()
data_access = DataAccess()
bussiness_logic = BusinessLogic()

temp_data = {}
interview_data = {}
interview_question = {}


@bot.message_handler(commands=['start'])
def start(message):
    try:
        login = str(message.from_user.id)
        data_access.add_user(login)
        bot.send_message(message.chat.id,
                         f"Привет, {message.from_user.first_name}, начнем!",
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
@bot.message_handler(func=lambda message: message.text == 'Информация 📚')
def info(message):
    bot.send_message(
        message.chat.id,
        "Этот бот помогает")


# Обработчик нажатия на кнопку 'Выбрать тему для вопросов 🧑‍💻'
@bot.message_handler(
        func=lambda message: message.text == 'Выбрать тему для вопросов 🧑‍💻')
def ai_interview_topics(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Выберите тему для собеседования:',
                     reply_markup=kb.topics_kb(True))
    bot.register_next_step_handler(message, ai_interview_question)


# Обработчик выбора темы для AI Собес
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


def ai_interview_receive_answer(message):
    chat_id = message.chat.id
    user_answer = message.text  # Ответ пользователя
    login = message.from_user.id
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

    bot.send_message(chat_id, answer_gpt, reply_markup=kb.interview_menu())


# Добавляем обработчик для инлайн-кнопки
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
    bot.register_next_step_handler(call.message, ai_interview_question)


# Обработчик неизвестных команд
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.send_message(
        message.chat.id,
        '🧐 Неизвестная команда. Выберите одну из предложенных опций.',
        reply_markup=kb.main_menu())


# Запуск бота
if __name__ == '__main__':
    print('Bot is running')
    bot.polling(none_stop=True)

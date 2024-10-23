import telebot
from keyboard_mixin import KeyboardMixin
from models import DataAccess
from ai_logic import InterviewThisOutOfOpenAI
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
    
    login = str(message.from_user.id)
    if data_access.add_user(login):
        bot.send_message(message.chat.id,
                         f"Привет, {message.from_user.first_name}, начнем!",
                         reply_markup=kb.main_menu())
    

# Обработчик нажатия на кнопку "Информация"
@bot.message_handler(func=lambda message: message.text == 'Информация 📚')
def info(message):
    bot.send_message(message.chat.id, "Этот бот помогает готовиться к собеседованию по языку программирования Python")


# Обработчик нажатия на кнопку 'Выбрать тему для вопросов 🧑‍💻'
@bot.message_handler(func=lambda message: message.text == 'Выбрать тему для вопросов 🧑‍💻')
def ai_interview_topics(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Выберите тему для собеседования:', reply_markup=kb.topics_kb(True))
    bot.register_next_step_handler(message, ai_interview_question)


# Обработчик выбора темы для AI Собес
def ai_interview_question(message):
    chat_id = message.chat.id
    if message.text == 'Назад':
        bot.send_message(chat_id, 'Возвращаемся в главное меню',
                         reply_markup=kb.main_menu())
        return
    interview_data[chat_id] = {'topic': message.text}
    if interview_data[chat_id]['topic'] == 'Python':
        bot.send_message(chat_id, 'Выберите сложность вопросов:', reply_markup=kb.difficulty_kb(True))
        bot.register_next_step_handler(message, ai_interview_start)
    if interview_data[chat_id]['topic'] == 'Django':
        login = message.from_user.id
        existing_user = data_access.get_existing_user(login)
        question = data_access.get_random_unanswered_question(existing_user.login, 'Django')
        if question:
            interview_question[chat_id] = {'question': question}
            bot.send_message(chat_id, question.question, reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, ai_interview_receive_answer)
        else:
            bot.send_message(chat_id, "Вы ответили на все вопросы правильно!\nПоздравляю! Вы прошли интервью по Django! 🎉", reply_markup=kb.main_menu())

def ai_interview_receive_answer(message):
    chat_id = message.chat.id
    user_answer = message.text  # Ответ пользователя
    user_id = data_access.get_user_id_by_login(message.from_user.id)
    question = interview_question[chat_id]['question'].question
    question_id = int(interview_question[chat_id]['question'].id)
    reference_question = interview_question[chat_id]['question'].answer
    answer_gpt = InterviewThisOutOfOpenAI(question, reference_question, user_answer).get_response()
    score = bussiness_logic.extract_first_digit(answer_gpt)
    data_access.save_progress(user_id, question_id, user_answer, score)
    bot.send_message(chat_id, answer_gpt, reply_markup=kb.interview_reply_kb())

@bot.message_handler(func=lambda message: message.text in ['Следующий вопрос ➡️', 'К выбору темы 📝', 'В главное меню 🏠'])
def handle_reply_buttons(message):
    chat_id = message.chat.id
    if message.text == 'Следующий вопрос ➡️':
        existing_user = data_access.get_existing_user(message.from_user.id)
        question = data_access.get_random_unanswered_question(existing_user.login, 'Django')
        if question:
            interview_question[chat_id] = {'question': question}
            bot.send_message(chat_id, question.question, reply_markup=kb.main_menu())
            bot.register_next_step_handler(message, ai_interview_receive_answer)
        else:
            bot.send_message(chat_id, "Вы ответили на все вопросы правильно!\nПоздравляю! Вы прошли интервью по Django! 🎉", reply_markup=kb.main_menu())
    elif message.text == 'К выбору темы 📝':
        bot.send_message(chat_id, 'Выберите тему для собеседования:', reply_markup=kb.topics_kb(True))
        bot.register_next_step_handler(message, ai_interview_question)
    elif message.text == 'В главное меню 🏠':
        bot.send_message(chat_id, 'Возвращаемся в главное меню', reply_markup=kb.main_menu())

# Обработчик выбора сложности для AI Собес Python
def ai_interview_start(message):
    chat_id = message.chat.id
    if message.text == 'Назад':
        bot.send_message(chat_id, 'Возвращаемся к выбору темы:', reply_markup=kb.topics_kb(True))
        bot.register_next_step_handler(message, ai_interview_question)
        return
    bot.send_message(chat_id, 'Начинаем собеседование!', reply_markup=kb.user_kb())


# Обработчик неизвестных команд
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.send_message(message.chat.id, '🧐 Неизвестная команда. Пожалуйста, выберите одну из предложенных опций.',
                     reply_markup=kb.main_menu())


# Запуск бота
if __name__ == '__main__':
    print('Bot is running')
    bot.polling(none_stop=True)


import telebot
from keyboard_mixin import KeyboardMixin

API_TOKEN = ''  # Нужен токен

bot = telebot.TeleBot(API_TOKEN)
kb = KeyboardMixin()

temp_data = {}
interview_data = {}
interview_question = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    welcome_message = f"Привет, {message.from_user.first_name}! Это телеграм-бот."
    bot.send_message(message.chat.id, welcome_message, reply_markup=kb.main_menu())


# Обработчик нажатия на кнопку "Информация"
@bot.message_handler(func=lambda message: message.text == 'Информация')
def info(message):
    bot.send_message(message.chat.id, "Этот бот помогает готовиться к собеседованию по языку программирования Python")


# Обработчик нажатия на кнопку "Твой собес"
@bot.message_handler(func=lambda message: message.text == 'Твой собес 👨‍💻')
def check_category_interview_button(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Выберите тип собеседования:', reply_markup=kb.interview_menu())


# Обработчик нажатия на кнопку "AI Собес"
@bot.message_handler(func=lambda message: message.text == 'AI Собес')
def ai_interview_button(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Укажите количество вопросов:', reply_markup=kb.amount_question_kb(True))
    bot.register_next_step_handler(message, ai_interview_topics)


# Появление тем после выбора количества вопросов для AI Собес
def ai_interview_topics(message):
    chat_id = message.chat.id
    if message.text == 'Назад':
        bot.send_message(chat_id, 'Возвращаемся в меню выбора собеседования:', reply_markup=kb.interview_menu())
        return
    amount = message.text
    interview_data[chat_id] = {'type': 'AI Собес', 'amount': amount}
    bot.send_message(chat_id, 'Выберите тему для собеседования:', reply_markup=kb.topics_kb(True))
    bot.register_next_step_handler(message, ai_interview_difficulty)


# Обработчик выбора темы для AI Собес
def ai_interview_difficulty(message):
    chat_id = message.chat.id
    if message.text == 'Назад':
        bot.send_message(chat_id, 'Возвращаемся к выбору количества вопросов:',
                         reply_markup=kb.amount_question_kb(True))
        bot.register_next_step_handler(message, ai_interview_topics)
        return
    interview_data[chat_id]['topic'] = message.text
    if interview_data[chat_id]['topic'] == 'Python':
        bot.send_message(chat_id, 'Выберите сложность вопросов:', reply_markup=kb.difficulty_kb(True))
        bot.register_next_step_handler(message, ai_interview_start)
    else:
        bot.send_message(chat_id, 'Начинаем собеседование!', reply_markup=kb.user_kb())


# Обработчик выбора сложности для AI Собес
def ai_interview_start(message):
    chat_id = message.chat.id
    if message.text == 'Назад':
        bot.send_message(chat_id, 'Возвращаемся к выбору темы:', reply_markup=kb.topics_kb(True))
        bot.register_next_step_handler(message, ai_interview_difficulty)
        return
    bot.send_message(chat_id, 'Начинаем собеседование!', reply_markup=kb.user_kb())


# Обработчик нажатия на кнопку "Вопросы"
@bot.message_handler(func=lambda message: message.text == 'Вопросы')
def questions_button(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Выберите тему вопросов:', reply_markup=kb.topics_kb(True))
    bot.register_next_step_handler(message, question_difficulty)


# Обработчик выбора темы
def question_difficulty(message):
    chat_id = message.chat.id
    if message.text == 'Назад':
        bot.send_message(chat_id, 'Возвращаемся в меню выбора собеседования:', reply_markup=kb.interview_menu())
        return
    interview_data[chat_id] = {'type': 'Вопросы', 'topic': message.text}
    if interview_data[chat_id]['topic'] == 'Python':
        bot.send_message(chat_id, 'Выберите сложность вопросов:', reply_markup=kb.difficulty_kb(True))
        bot.register_next_step_handler(message, question_amount)
    else:
        bot.send_message(chat_id, 'Укажите количество вопросов:', reply_markup=kb.amount_question_kb(True))
        bot.register_next_step_handler(message, question_amount)


# Обработчик выбора количества вопросов
def question_amount(message):
    chat_id = message.chat.id
    if message.text == 'Назад':
        bot.send_message(chat_id, 'Возвращаемся к выбору темы вопросов:', reply_markup=kb.topics_kb(True))
        bot.register_next_step_handler(message, question_difficulty)
        return
    interview_data[chat_id]['amount'] = message.text
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

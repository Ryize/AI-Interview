from telebot import types


class KeyboardMixin:
    def main_menu(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        interview_button = types.KeyboardButton('Выбрать тему для вопросов 🧑‍💻')
        profile_button = types.KeyboardButton('Ваш профиль 🧑')
        info_button = types.KeyboardButton('Информация 📚')
        markup.add(interview_button, profile_button, info_button)
        return markup

    def interview_menu(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        ai_interview_button = types.KeyboardButton('AI Собес')
        question_button = types.KeyboardButton('Вопросы')
        back_button = types.KeyboardButton('Назад')
        markup.add(ai_interview_button, question_button, back_button)
        return markup

    def topics_kb(self, back=False):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        python_trainee = types.KeyboardButton('Python(trainee)')
        python_junior = types.KeyboardButton('Python(junior)')
        python_middle = types.KeyboardButton('Python(middle)')
        django_button = types.KeyboardButton('Django')
        oop_button = types.KeyboardButton('ООП')
        markup.row(python_trainee, python_junior, python_middle)
        markup.row(django_button, oop_button)
        if back:
            back_button = types.KeyboardButton('Назад')
            markup.add(back_button)
        return markup

    def difficulty_kb(self, back=False):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        easy_button = types.KeyboardButton('1-3')
        medium_button = types.KeyboardButton('3-5')
        hard_button = types.KeyboardButton('5-7')
        markup.add(easy_button, medium_button, hard_button)
        if back:
            back_button = types.KeyboardButton('Назад')
            markup.add(back_button)
        return markup

    def amount_question_kb(self, back=False):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        five_button = types.KeyboardButton('5')
        ten_button = types.KeyboardButton('10')
        fifteen_button = types.KeyboardButton('15')
        markup.add(five_button, ten_button, fifteen_button)
        if back:
            back_button = types.KeyboardButton('Назад')
            markup.add(back_button)
        return markup

    def user_kb(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        interview_button = types.KeyboardButton('Твой собес 👨‍💻')
        markup.add(interview_button)
        return markup

    def interview_reply_kb(self):
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        next_question_button = types.KeyboardButton('Следующий вопрос ➡️')
        choose_topic_button = types.KeyboardButton('К выбору темы 📝')
        main_menu_button = types.KeyboardButton('В главное меню 🏠')

        reply_markup.add(next_question_button, choose_topic_button, main_menu_button)
        return reply_markup
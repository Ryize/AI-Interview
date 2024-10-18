from telebot import types


class KeyboardMixin:
    def main_menu(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        interview_button = types.KeyboardButton('Твой собес 👨‍💻')
        info_button = types.KeyboardButton('Информация')
        markup.add(interview_button, info_button)
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
        python_button = types.KeyboardButton('Python')
        hr_button = types.KeyboardButton('HR’ские')
        django_button = types.KeyboardButton('Django')
        oop_button = types.KeyboardButton('ООП')
        markup.add(python_button, hr_button, django_button, oop_button)
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

from telebot import types


class KeyboardMixin:
    def main_menu(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        interview_button = types.KeyboardButton(
            'Выбрать тему для вопросов 🧑‍💻')
        profile_button = types.KeyboardButton('Ваш профиль 🧑')
        info_button = types.KeyboardButton('Информация 📚')
        markup.add(interview_button, profile_button, info_button)
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

    def user_kb(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        interview_button = types.KeyboardButton('Твой собес 👨‍💻')
        markup.add(interview_button)
        return markup

    def interview_reply_kb(self):
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                 row_width=2)
        next_question_button = types.KeyboardButton('Следующий вопрос ➡️')
        choose_topic_button = types.KeyboardButton('К выбору темы 📝')
        main_menu_button = types.KeyboardButton('В главное меню 🏠')

        reply_markup.add(next_question_button, choose_topic_button,
                         main_menu_button)
        return reply_markup

    def interview_menu(self):
        markup = types.InlineKeyboardMarkup()
        next_question_button = types.InlineKeyboardButton(
            "Следующий вопрос ➡️", callback_data="next_question")
        topic = types.InlineKeyboardButton(
            "К выбору темы 📝", callback_data="topic")
        main_menu = types.InlineKeyboardButton(
            "В главное меню 🏠", callback_data="main_menu")
        markup.row(next_question_button)
        markup.row(topic, main_menu)
        return markup

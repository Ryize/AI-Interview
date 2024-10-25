from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
import random
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(255), nullable=False)
    question_limit = Column(Integer, nullable=False, default=0)  # Количество вопросов

    # Устанавливаем связь с таблицей ProgressStudy
    progresses = relationship("ProgressStudy", back_populates="user")


class ProgressStudy(Base):
    __tablename__ = 'progress_study'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer = Column(Text)
    score = Column(Integer)

    # Связи
    user = relationship("User", back_populates="progresses")
    question = relationship("Question", back_populates="progresses")

# Определяем модель Question
class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(255), nullable=False)
    difficulty = Column(Integer, nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # Устанавливаем связь с таблицей ProgressStudy
    progresses = relationship("ProgressStudy", back_populates="question")


# Создание движка базы данных MySQL с PyMySQL
login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')
engine = create_engine(f'mysql+pymysql://{login}:{password}@{host}/{database}')

# Создаем таблицы в базе данных
# Base.metadata.create_all(engine)

# Создаем сессию для взаимодействия с базой данных
Session = sessionmaker(bind=engine)
session = Session()

class DataAccess:
    def __init__(self):
        self.session = Session()

    def get_existing_user(self, login):
        user = session.query(User).filter_by(login=login).first()
        if not user:
            return None
        return user

    def add_user(self, login):
        # Проверяем, существует ли пользователь с таким логином в базе
        user = self.get_existing_user(login)
        
        if not user:
            # Если пользователя нет, добавляем его в базу
            try:
                new_user = User(login=login,
                                question_limit=10)
                session.add(new_user)
                session.commit()
            except IntegrityError:
                session.rollback()  # Откатить изменения, если возникла ошибка    
            else:
                return True
        else:
            return True

    def get_random_unanswered_question(self, login, topic):
        # Получаем пользователя по его логину
        user = self.get_existing_user(login)
        if user.question_limit < 1:
            return -1

        # Получаем список всех вопросов по указанной теме
        all_questions = session.query(Question).filter_by(topic=topic).all()

        # Получаем список ID вопросов, на которые пользователь уже ответил
        answered_question_ids = (
            session.query(ProgressStudy.question_id)
            .filter_by(user_id=user.id)
            .all()
        )
        answered_question_ids = [qid[0] for qid in answered_question_ids]  # Преобразуем в список ID

        # Фильтруем вопросы, на которые пользователь не ответил
        unanswered_questions = [
            question for question in all_questions
            if question.id not in answered_question_ids
        ]

        # Проверяем, есть ли вопросы, на которые пользователь не ответил
        if not unanswered_questions:
            question_low_score = self.get_questions_for_user_with_low_score(user.id)
            if question_low_score:
                # user.question_limit = user.question_limit - 1
                session.commit()
                return random.choice(question_low_score)
            else:
                return False

        # Возвращаем случайный вопрос
        # user.question_limit = user.question_limit - 1
        session.commit()
        return random.choice(unanswered_questions)
    
    def save_progress(self, login, question_id, answer, score):

        user = self.get_existing_user(login=login)

        # Проверяем, есть ли уже прогресс для данного пользователя и вопроса
        existing_progress = session.query(ProgressStudy).filter_by(user_id=user.id,
                                                                   question_id=question_id).first()
        
        if existing_progress:
            # Если прогресс существует, обновляем answer и score
            existing_progress.answer = answer
            existing_progress.score = score
        else:
            # Если прогресс не найден, создаем новый экземпляр
            new_progress = ProgressStudy(user_id=user.id,
                                        question_id=question_id,
                                        answer=answer,
                                        score=score)
            session.add(new_progress)
    
        # Сохраняем изменения в базе данных
        session.commit()

    def get_questions_for_user_with_low_score(self, user_id):
        return session.query(Question).\
            join(ProgressStudy, ProgressStudy.question_id == Question.id).\
            filter(ProgressStudy.user_id == user_id).\
            filter(ProgressStudy.score < 7).\
            all()

    def check_date(self, user):
        now_day = datetime.now().date()
        last_visit = user.last_visit
        if now_day > last_visit:
            user.question_limit = 10
            user.last_visit = now_day
            session.commit()
            return True
        else:
            return False
# Пример добавления данных
# def add_test_data():
#     # Создаем пользователя
#     user = User(login="denis", question_limit=5)
#     user1 = User(login="uma", question_limit=2)
#     session.add_all([user, user1])
    
#     Создаем вопросы
# question1 = Question(topic="Django",
#                      question="Что такое Django и почему его используют?",
#                      answer="Django это Python фреймворк, который упрощает разработку веб-приложений. Его используют потому, что он предоставляет множество встроенных инструментов (например, для работы с базами данных, аутентификации и администрирования). Также Django защищает от основных уязвимостей, таких как SQL инъекции, XSS, CSRF")
# question2 = Question(topic="Django",
#                      question="В чем преимущества Django?",
#                      answer="""
#                             Безопасность: Встроенные защиты от SQL-инъекций, CSRF, XSS и других угроз.
#                             Масштабируемость: Благодаря огромному количеству готовых модулей и батареечной модели получается быстро добавлять новый функционал.
#                             Админ-панель: Автоматическое создание, можно полностью кастомизировать.
#                             Сообщество и документация: Большое сообщество и качественная документация.
#                             """)
# question3 = Question(topic="Django",
#                      question="Каковы недостатки Django?",
#                      answer="""
#                             Недостатки Django:
#                             Монолитность: Django обычно избыточен для небольших проектов.
#                             Скорость: По сравнению с более легковесными фреймворками, Django менее производительный.
#                             Сложность обучения: Django является одним из самых сложных в изучении фреймворков в Python.
#                             Django ORM: невозможность использовать другую ORM, вместо Django ORM.
#                             Синхронный принцип работы: это значительно ограничивает использование Django в высоконагруженных проектах.""",)
# question4 = Question(topic="Django",
#                      question="На каком принципе построена архитектура Django?",
#                      answer="""
# Архитектура Django основана на принципе MTV (Model-Template-View):
# Model: Определяет взаимодействие с базой данных.
# Template: Отвечает за отображение данных у пользователя.
# View: Логика обработки запросов.
# Этот подход разделяет логику, данные и представление, что упрощает поддержку и масштабирование приложения.
# """)
# question5 = Question(topic="Django",
#                      question="Что ты знаешь о Djangopackages.org?",
#                      answer="Djangopackages.org — это сайт, который хранит и сравнивает сторонние пакеты для Django. Он помогает быстро находить готовые решения например для: аутентификации, REST API,  интеграции с платёжными системами и так далее. Использование таких расширений сокращает время разработки и повышает надёжность.")
# session.add_all([question1, question2, question3, question4, question5])

# #     # Сохраняем изменения в базе данных
# session.commit()

#     # Добавляем прогресс для пользователя
#     progress1 = ProgressStudy(user_id=user.id, question_id=question1.id, answer="4", score=10)
#     progress2 = ProgressStudy(user_id=user.id, question_id=question2.id, answer="H2O", score=10)
#     progress3 = ProgressStudy(user_id=user1.id, question_id=question1.id, answer="5", score=2)
#     progress4 = ProgressStudy(user_id=user1.id, question_id=question2.id, answer="H3O", score=7)
#     session.add_all([progress1, progress2, progress3, progress4])

#     # Сохраняем изменения
#     session.commit()

#     print("Test data added successfully.")

# # Функция для проверки данных
# def check_data():
#     users = session.query(User).all()
#     for user in users:
#         print(f"User {user.login} can ask {user.question_limit} questions.")
#         for progress in user.progresses:
#             question = session.query(Question).filter(Question.id == progress.question_id).first()
#             print(f"Answered question: {question.question}, User answer: {progress.answer}, Score: {progress.score}")

# # Добавляем тестовые данные и проверяем
# add_test_data()
# check_data()
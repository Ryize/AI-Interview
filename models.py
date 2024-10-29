from sqlalchemy import create_engine, Column, Integer, String, Text, \
      ForeignKey, DateTime
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
    question_limit = Column(Integer, nullable=False, default=0)
    last_visit = Column(DateTime, nullable=True)  # Дата последнего посещения

    # Устанавливаем связь с таблицей ProgressStudy
    progresses = relationship("ProgressStudy", back_populates="user")


class ProgressStudy(Base):
    __tablename__ = 'progress_study'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer = Column(Text)
    score = Column(Integer)
    date = Column(DateTime, nullable=True)
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
    answer = Column(Text, nullable=True)

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
                                question_limit=10,
                                last_visit=datetime.now())
                session.add(new_user)
                session.commit()
            except IntegrityError:
                session.rollback()  # Откатить изменения, если возникла ошибка
            else:
                return True
        else:
            return True

    def get_random_unanswered_question(self, login, topic, difficulty=None):
        # Получаем пользователя по его логину
        user = self.get_existing_user(login)
        if user.question_limit < 1:
            return -1
        # Создаем базовый запрос
        query = session.query(Question).filter_by(topic=topic)
        # Получаем список всех вопросов по указанной теме
        if difficulty:
            if difficulty == 'trainee':
                all_questions = query.filter(Question.difficulty.between(1, 3))
            elif difficulty == 'junior':
                all_questions = query.filter(Question.difficulty.between(3, 5))
            elif difficulty == 'middle':
                all_questions = query.filter(Question.difficulty >= 5)
        else:
            all_questions = query.all()

        # Получаем список ID вопросов, на которые пользователь уже ответил
        answered_question_ids = (
            session.query(ProgressStudy.question_id)
            .filter_by(user_id=user.id)
            .all()
        )
        # Преобразуем в список ID
        answered_question_ids = [qid[0] for qid in answered_question_ids]

        # Фильтруем вопросы, на которые пользователь не ответил
        unanswered_questions = [
            question for question in all_questions
            if question.id not in answered_question_ids
        ]

        # Проверяем, есть ли вопросы, на которые пользователь не ответил
        if not unanswered_questions:
            question_low_score = self.get_questions_for_user_with_low_score(
                user.id)
            if question_low_score:
                user.question_limit = user.question_limit - 1
                session.commit()
                return random.choice(question_low_score)
            else:
                return False

        # Возвращаем случайный вопрос
        user.question_limit = user.question_limit - 1
        session.commit()
        return random.choice(unanswered_questions) 

    def save_progress(self, login, question_id, answer, score):

        user = self.get_existing_user(login=login)

        # Проверяем, есть ли уже прогресс для данного пользователя и вопроса
        existing_progress = session.query(ProgressStudy).filter_by(
            user_id=user.id,
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
                                         score=score,
                                         date=datetime.now())
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
        now_day = datetime.now()
        last_visit = user.last_visit
        if now_day.day > last_visit.day:
            user.question_limit = 10
            user.last_visit = now_day
            session.commit()
            return True
        else:
            return False

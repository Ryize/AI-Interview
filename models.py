from sqlalchemy import create_engine, Column, Integer, String, Text, \
      ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
import random
from dotenv import load_dotenv
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
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

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session = Session()
        return cls._instance

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

    def get_random_unanswered_question(self, login, topic, difficulty=None):
        user = self.get_user(login)
        if not user:
            return False
        # Проверяем, есть ли у пользователя вопросы
        if user.question_limit < 1:
            return -1

        # Получаем все вопросы по теме и сложности
        all_questions = self.get_all_questions(topic, difficulty)
        if not all_questions:
            return False

        # Получаем список ID вопросов, на которые пользователь уже ответил
        answered_question_ids = self.get_answered_question_ids(user.id)

        # Фильтруем вопросы, на которые пользователь не ответил
        if not answered_question_ids:
            unanswered_questions = all_questions
        else:
            unanswered_questions = self.filter_unanswered_questions(
                all_questions, answered_question_ids)

        # Если нет неотвеченных вопросов, получаем вопрос с низкой оценкой
        if not unanswered_questions:
            return self.get_low_score_question(user)

        return self.select_random_question(user, unanswered_questions)

    def get_user(self, login):
        try:
            # Получаем пользователя по его логину
            user = self.get_existing_user(login)
            return user
        except SQLAlchemyError:
            return False

    def get_all_questions(self, topic, difficulty):
        try:
            # Создаем базовый запрос
            query = session.query(Question).filter_by(topic=topic)
            # Получаем список всех вопросов по указанной теме
            if difficulty:
                if difficulty == 'trainee':
                    return query.filter(
                        Question.difficulty.between(1, 3)).all()
                elif difficulty == 'junior':
                    return query.filter(
                        Question.difficulty.between(3, 5)).all()
                elif difficulty == 'middle':
                    return query.filter(
                        Question.difficulty >= 5).all()
                else:
                    return False
            else:
                return query.all()
        except SQLAlchemyError:
            return False

    def get_answered_question_ids(self, user_id):
        try:
            # Получаем список ID вопросов,
            # на которые пользователь уже ответил
            answered = session.query(
                ProgressStudy.question_id).filter_by(user_id=user_id).all()
            return [qid[0] for qid in answered]
        except (SQLAlchemyError, IndexError):
            return False

    def filter_unanswered_questions(self,
                                    all_questions,
                                    answered_question_ids):
        try:
            # Фильтруем вопросы, на которые пользователь не ответил
            return [
                question for question in all_questions
                if question.id not in answered_question_ids
            ]
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def get_low_score_question(self, user):
        try:
            # Получаем вопросы с низкой оценкой
            question_low_score = self. \
                get_questions_for_user_with_low_score(user.id)
            if question_low_score:
                user.question_limit -= 1
                session.commit()
                return random.choice(question_low_score)
            else:
                return -2
        except (SQLAlchemyError, IndexError):
            return False

    @staticmethod
    def select_random_question(user, questions):
        try:
            # Уменьшаем количество вопросов у пользователя
            user.question_limit -= 1
            session.commit()
            # Возвращаем случайный вопрос
            return random.choice(questions)
        except (SQLAlchemyError, IndexError):
            return False

    def save_progress(self, login, question_id, answer, score):

        user = self.get_user(login=login)

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

        session.commit()

    def get_questions_for_user_with_low_score(self, user_id):
        try:
            query = session.query(Question).\
                join(ProgressStudy, ProgressStudy.question_id == Question.id).\
                filter(ProgressStudy.user_id == user_id).\
                filter(ProgressStudy.score < 7).\
                all()
            return query
        except SQLAlchemyError:
            return False

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

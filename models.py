from sqlalchemy import create_engine, Column, Integer, String, Text, \
      ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
import random
from dotenv import load_dotenv
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from logger import logger
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


class DataAccess:

    _instance = None

    @logger.catch
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance.session = Session()
        return cls._instance

    @logger.catch
    def get_existing_user(self, login):
        user = self._instance.session.query(User).filter_by(login=login). \
            first()
        if not user:
            return None
        return user

    @logger.catch
    def get_user(self, login):
        try:
            # Получаем пользователя по его логину
            user = self.get_existing_user(login)
            return user
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении пользователя: {e}")
            return False

    @logger.catch
    def add_user(self, login):
        # Проверяем, существует ли пользователь с таким логином в базе
        user = self.get_existing_user(login)

        if not user:
            # Если пользователя нет, добавляем его в базу
            try:
                new_user = User(login=login,
                                question_limit=10,
                                last_visit=datetime.now())
                self._instance.session.add(new_user)
                self._instance.session.commit()
            except IntegrityError:
                self._instance.session.rollback()

    @logger.catch
    def check_date(self, user):
        now_day = datetime.now()
        last_visit = user.last_visit
        if now_day.date() > last_visit.date():
            user.question_limit = 10
            user.last_visit = now_day
            self._instance.session.commit()
            return True
        else:
            return False

    @logger.catch
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

    @logger.catch
    def get_all_questions(self, topic, difficulty):
        try:
            # Создаем базовый запрос
            query = self._instance.session.query(Question).filter_by(
                topic=topic)
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

    @logger.catch
    def get_answered_question_ids(self, user_id):
        try:
            # Получаем список ID вопросов,
            # на которые пользователь уже ответил
            answered = self._instance.session.query(
                ProgressStudy.question_id).filter_by(user_id=user_id).all()
            return [qid[0] for qid in answered]
        except (SQLAlchemyError, IndexError):
            return False

    @logger.catch
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

    @logger.catch
    def get_low_score_question(self, user):
        try:
            # Получаем вопросы с низкой оценкой
            question_low_score = self. \
                get_questions_for_user_with_low_score(user.id)
            if question_low_score:
                user.question_limit -= 1
                self._instance.session.commit()
                return random.choice(question_low_score)
            else:
                return -2
        except (SQLAlchemyError, IndexError):
            return False

    @logger.catch
    def select_random_question(self, user, questions):
        try:
            # Уменьшаем количество вопросов у пользователя
            user.question_limit -= 1
            self._instance.session.commit()
            # Возвращаем случайный вопрос
            return random.choice(questions)
        except (SQLAlchemyError, IndexError):
            return False

    @logger.catch
    def save_progress(self, login, question_id, answer, score):

        user = self.get_user(login=login)

        # Проверяем, есть ли уже прогресс для данного пользователя и вопроса
        existing_progress = self._instance.session.query(ProgressStudy). \
            filter_by(
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
            self._instance.session.add(new_progress)

        self._instance.session.commit()

    @logger.catch
    def get_questions_for_user_with_low_score(self, user_id):
        try:
            query = self._instance.session.query(Question).\
                join(ProgressStudy, ProgressStudy.question_id == Question.id).\
                filter(ProgressStudy.user_id == user_id).\
                filter(ProgressStudy.score < 7).\
                all()
            return query
        except SQLAlchemyError:
            return False

    @logger.catch
    def get_questions_for_user_with_high_score(self, user_id):
        try:
            query = self._instance.session.query(Question).\
                join(ProgressStudy, ProgressStudy.question_id == Question.id).\
                filter(ProgressStudy.user_id == user_id).\
                filter(ProgressStudy.score >= 7).\
                all()
            return query
        except SQLAlchemyError:
            return False

    @logger.catch
    def get_questions_for_user_with_high_score_by_topic(self, user_id, topic):
        try:
            query = self.get_questions_for_user_with_high_score(user_id)
            return [question for question in query if question.topic == topic]
        except SQLAlchemyError:
            return False

    @logger.catch
    def get_count_questions_for_user_with_high_score_by_Python(self, user_id):
        try:
            query = self.get_questions_for_user_with_high_score_by_topic(
                user_id, 'Python')
            python_trainee = [
                question for question in query if question.difficulty in range(
                    1, 4)]
            python_junior = [
                question for question in query if question.difficulty in range(
                    3, 6)]
            python_middle = [
                question for question in query if question.difficulty >= 5]
            return len(python_trainee), len(python_junior), len(python_middle)
        except SQLAlchemyError:
            return False

    @logger.catch
    def get_count_all_questions_for_Python(self):
        try:
            query = self.get_all_questions('Python', None)
            python_trainee = [
                question for question in query if question.difficulty in range(
                    1, 4)]
            python_junior = [
                question for question in query if question.difficulty in range(
                    3, 6)]
            python_middle = [
                question for question in query if question.difficulty >= 5]
            return len(python_trainee), len(python_junior), len(python_middle)
        except SQLAlchemyError:
            return False

    @logger.catch
    def get_progress_Python(self, user_id):
        try:
            trainee_all, junior_all, middle_all = self. \
                get_count_all_questions_for_Python()
            trainee_user, junior_user, middle_user = self. \
                get_count_questions_for_user_with_high_score_by_Python(user_id)
            return round(trainee_user / trainee_all * 100, 2), \
                round(junior_user / junior_all * 100, 2), \
                round(middle_user / middle_all * 100, 2)
        except SQLAlchemyError:
            return False

    @logger.catch
    def get_progress_topic(self, user_id, topic):
        try:
            all_questions = self.get_all_questions(topic, None)
            user_questions = self. \
                get_questions_for_user_with_high_score_by_topic(user_id, topic)
            return round(len(user_questions) / len(all_questions) * 100, 2)
        except SQLAlchemyError:
            return False

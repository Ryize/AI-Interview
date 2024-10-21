from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

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
login = 'LOGIN'
password = 'PASSWORD'
host = 'HOST'
database = 'DATABASE'
engine = create_engine(f'mysql+pymysql://{login}:{password}@{host}/{database}')

# Создаем таблицы в базе данных
Base.metadata.create_all(engine)

# Создаем сессию для взаимодействия с базой данных
Session = sessionmaker(bind=engine)
session = Session()

#Пример добавления данных
# def add_test_data():
#     # Создаем пользователя
#     user = User(login="denis", question_limit=5)
#     user1 = User(login="uma", question_limit=2)
#     session.add_all([user, user1])
    
#     # Создаем вопросы
#     question1 = Question(topic="Math", question="What is 2+2?", answer="4")
#     question2 = Question(topic="Science", question="What is the chemical formula of water?", answer="H2O")
#     session.add_all([question1, question2])

#     # Сохраняем изменения в базе данных
#     session.commit()

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
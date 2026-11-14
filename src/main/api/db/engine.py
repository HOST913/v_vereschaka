# Настройка движка SQLAlchemy и фабрики сессий PostgreSQL.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main.api.configs.config import Config

# Создаём движок SQLAlchemy для адреса БД из настроек.
engine = create_engine(Config.fetch('dataBaseUrl'), echo=False)
# Создаём фабрику сессий для SQL-запросов тестов.
SessionLocal = sessionmaker(bind=engine)
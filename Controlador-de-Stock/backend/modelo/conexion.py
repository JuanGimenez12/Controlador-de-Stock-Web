import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Valores por defecto apuntando a PostgreSQL
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "") 
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432") # Puerto de PostgreSQL
DB_NAME = os.getenv("DB_NAME", "Sistema_Stock.db") # El nombre que le pusiste en pgAdmin

# Forma segura y a prueba de errores para armar la conexión a Postgres
url_segura = URL.create(
    drivername="postgresql", # El driver cambia a postgresql
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

# Crear el motor de la base de datos
engine = create_engine(url_segura)

# Crear el generador de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para crear los modelos
Base = declarative_base()

# Función para obtener la sesión en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from fastapi import FastAPI
from modelo.conexion import engine, Base
from routers import productos

# 1. Instrucción a SQLAlchemy para que cree las tablas en MySQL 
# (Solo crea las que no existan leyendo el archivo models/modelos.py)
Base.metadata.create_all(bind=engine)

# 2. Configuración principal de la API
app = FastAPI(
    title="API Kiosco",
    description="Backend transaccional para el sistema de gestión del kiosco",
    version="1.0.0"
)

# 3. "Enchufar" (incluir) las rutas de los módulos que fuimos programando
app.include_router(productos.router)

# 4. Ruta base de comprobación
@app.get("/")
def inicio():
    return {"mensaje": "¡El servidor Backend del Kiosco y la Base de Datos están operativos!"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modelo.conexion import engine, Base
from modelo import modelo
# Importamos las rutas (asegúrate de que la ruta exista en tu archivo productos.py)
from routers import productos 

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Le damos permiso exacto a React
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PUT, DELETE
    allow_headers=["*"],
)

# Conectamos el router de productos a la app principal
app.include_router(productos.router)

@app.get("/")
def read_root():
    return {"mensaje": "¡Backend conectado a PostgreSQL exitosamente!"}
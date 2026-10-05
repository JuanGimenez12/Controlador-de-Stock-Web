from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from modelo import modelo
from schemas import esquemas
from modelo.conexion import get_db

router = APIRouter(prefix="/productos", tags=["Productos"])

# Ruta GET: Para leer los productos (La que ya tenías)
@router.get("/")
def obtener_productos(db: Session = Depends(get_db)):
    lista_productos = db.query(modelo.Producto).all()
    return lista_productos

# Ruta POST: Para guardar un producto nuevo
@router.post("/")
def crear_producto(producto: esquemas.ProductoCrear, db: Session = Depends(get_db)):
    # 1. Transformamos los datos que llegan de React a un modelo de Base de Datos
    nuevo_producto = modelo.Producto(
        codigo=producto.codigo,
        nombre=producto.nombre,
        precio=producto.precio,
        stock=producto.stock
    )
    
    # 2. Lo guardamos en PostgreSQL
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto) # Refrescamos para obtener el ID que le asignó la base
    
    # 3. Devolvemos el producto creado como respuesta
    return nuevo_producto
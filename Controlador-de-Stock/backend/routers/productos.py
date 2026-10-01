from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modelo.conexion import get_db
from modelo import modelos
from schemas import esquemas

# Creamos el enrutador para este módulo
router = APIRouter(
    prefix="/inventario",
    tags=["Inventario (Productos y Categorías)"]
)

# ==========================================
# RUTAS PARA CATEGORÍAS
# ==========================================

@router.post("/categorias/", response_model=esquemas.CategoriaResponse)
def crear_categoria(categoria: esquemas.CategoriaCreate, db: Session = Depends(get_db)):
    nueva_categoria = modelos.Categoria(**categoria.model_dump())
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

@router.get("/categorias/", response_model=list[esquemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(modelos.Categoria).all()


# ==========================================
# RUTAS PARA PRODUCTOS ( Alta, Edición, Baja)
# ==========================================

# 1. ALTA DE PRODUCTO
@router.post("/productos/", response_model=esquemas.ProductoResponse)
def crear_producto(producto: esquemas.ProductoCreate, db: Session = Depends(get_db)):
    # Verificamos si la categoría existe antes de crear el producto
    categoria = db.query(modelos.Categoria).filter(modelos.Categoria.id_categoria == producto.id_categoria).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="La categoría indicada no existe")
    
    nuevo_producto = modelos.Producto(**producto.model_dump())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto

# 2. LECTURA (Listar todos los productos activos)
@router.get("/productos/", response_model=list[esquemas.ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    # Filtramos para que solo muestre los que tienen "activo == True"
    return db.query(modelos.Producto).filter(modelos.Producto.activo == True).all()

# 3. EDICIÓN DE PRODUCTO
@router.put("/productos/{id_producto}", response_model=esquemas.ProductoResponse)
def editar_producto(id_producto: int, producto_actualizado: esquemas.ProductoCreate, db: Session = Depends(get_db)):
    producto_bd = db.query(modelos.Producto).filter(modelos.Producto.id_producto == id_producto).first()
    if not producto_bd:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Actualizamos los campos
    for key, value in producto_actualizado.model_dump().items():
        setattr(producto_bd, key, value)
    
    db.commit()
    db.refresh(producto_bd)
    return producto_bd

# 4. BAJA DE PRODUCTO (Baja Lógica)
@router.delete("/productos/{id_producto}")
def eliminar_producto(id_producto: int, db: Session = Depends(get_db)):
    producto_bd = db.query(modelos.Producto).filter(modelos.Producto.id_producto == id_producto).first()
    if not producto_bd:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # En lugar de borrarlo de la base de datos (DELETE), lo desactivamos (Baja lógica).
    # Esto protege la integridad del historial de ventas.
    producto_bd.activo = False
    db.commit()
    return {"mensaje": f"El producto {producto_bd.nombre} fue dado de baja exitosamente"}

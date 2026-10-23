from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modelo import modelo
from schemas import esquemas
from modelo.conexion import get_db

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/")
def obtener_productos(db: Session = Depends(get_db)):
    lista_productos = db.query(modelo.Producto).all()
    return lista_productos

from fastapi import HTTPException # Asegúrate de tener esto importado arriba

@router.post("/")
def crear_producto(producto: esquemas.ProductoCrear, db: Session = Depends(get_db)):
    # 1. VERIFICACIÓN DE DUPLICADOS
    if producto.codigo_barras:
        producto_existente = db.query(modelo.Producto).filter(modelo.Producto.codigo_barras == producto.codigo_barras).first()
        if producto_existente:
            # Si existe, frenamos todo y lanzamos un error 400 (Bad Request)
            raise HTTPException(status_code=400, detail=f"El código {producto.codigo_barras} ya está registrado en otro producto.")

    # 2. CREACIÓN DEL PRODUCTO
    nuevo_producto = modelo.Producto(
        codigo_barras=producto.codigo_barras,
        nombre=producto.nombre,
        marca=producto.marca,              
        descripcion=producto.descripcion,
        precio_costo=producto.precio_costo,
        precio_venta=producto.precio_venta,
        stock_actual=producto.stock_actual,
        stock_minimo=producto.stock_minimo,
        unidad_medida=producto.unidad_medida,
        unidades_por_caja=producto.unidades_por_caja,
        fecha_vencimiento=producto.fecha_vencimiento,
        id_categoria=producto.id_categoria,
        id_proveedor=producto.id_proveedor
    )
    
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto

@router.delete("/{id_producto}")
def eliminar_producto(id_producto: int, db: Session = Depends(get_db)):
    producto = db.query(modelo.Producto).filter(modelo.Producto.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(producto)
    db.commit()
    return {"mensaje": "Producto eliminado exitosamente"}
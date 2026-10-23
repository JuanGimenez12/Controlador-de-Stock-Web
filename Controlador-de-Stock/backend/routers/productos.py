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
@router.put("/{id_producto}")
def actualizar_producto(id_producto: int, producto: esquemas.ProductoCrear, db: Session = Depends(get_db)):
    # 1. Buscar si el producto existe
    db_producto = db.query(modelo.Producto).filter(modelo.Producto.id_producto == id_producto).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    # 2. Validar si el código de barras ya pertenece a OTRO producto (evitar duplicados al editar)
    if producto.codigo_barras:
        producto_existente = db.query(modelo.Producto).filter(
            modelo.Producto.codigo_barras == producto.codigo_barras,
            modelo.Producto.id_producto != id_producto
        ).first()
        if producto_existente:
            raise HTTPException(status_code=400, detail=f"El código {producto.codigo_barras} ya está registrado en otro producto.")

    # 3. Actualizar los campos
    db_producto.codigo_barras = producto.codigo_barras
    db_producto.nombre = producto.nombre
    db_producto.marca = producto.marca
    db_producto.descripcion = producto.descripcion
    db_producto.precio_costo = producto.precio_costo
    db_producto.precio_venta = producto.precio_venta
    db_producto.stock_actual = producto.stock_actual
    db_producto.stock_minimo = producto.stock_minimo
    db_producto.unidad_medida = producto.unidad_medida
    db_producto.unidades_por_caja = producto.unidades_por_caja
    db_producto.fecha_vencimiento = producto.fecha_vencimiento
    db_producto.id_categoria = producto.id_categoria
    db_producto.id_proveedor = producto.id_proveedor

    db.commit()
    db.refresh(db_producto)
    return db_producto
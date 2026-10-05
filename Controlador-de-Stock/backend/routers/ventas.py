from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modelo.conexion import get_db
from modelo import modelo
from schemas import esquemas

router = APIRouter(
    prefix="/ventas",
    tags=["Ventas y Caja"]
)

@router.post("/", response_model=esquemas.VentaResponse)
def registrar_venta(venta_in: esquemas.VentaCreate, db: Session = Depends(get_db)):
    # 1. Variables para calcular el ticket
    total_venta = 0.0
    detalles_a_guardar = []

    # 2. Recorremos cada producto que mandó el cajero
    for item in venta_in.detalles:
        # Buscamos el producto en la base de datos (y nos aseguramos que esté activo)
        producto = db.query(modelo.Producto).filter(
            modelo.Producto.id_producto == item.id_producto,
            modelo.Producto.activo == True
        ).first()

        if not producto:
            raise HTTPException(status_code=404, detail=f"El producto ID {item.id_producto} no existe o está dado de baja.")
        
        # Verificamos que alcance el stock
        if producto.stock_actual < item.cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente para {producto.nombre}. Hay {producto.stock_actual} unidades."
            )

        # 3. Matemática interna (Seguridad)
        subtotal = producto.precio_venta * item.cantidad
        total_venta += subtotal

        # 4. Descuento automático de stock
        producto.stock_actual -= item.cantidad

        # 5. Armamos el renglón del ticket (Detalle)
        nuevo_detalle = modelo.DetalleVenta(
            id_producto=producto.id_producto,
            cantidad=item.cantidad,
            precio_unitario=producto.precio_venta, # Congelamos el precio histórico
            subtotal=subtotal
        )
        detalles_a_guardar.append(nuevo_detalle)

    # 6. Creamos la cabecera de la venta
    nueva_venta = modelo.Venta(
        total=total_venta,
        medio_pago=venta_in.medio_pago,
        detalles=detalles_a_guardar
    )

    # 7. Guardamos TODO junto en la base de datos (Transacción)
    db.add(nueva_venta)
    db.commit()
    db.refresh(nueva_venta)

    return nueva_venta
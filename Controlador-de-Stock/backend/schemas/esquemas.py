from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from datetime import date

# --- ESQUEMAS PARA CATEGORÍA ---
class CategoriaBase(BaseModel):
    nombre: str
    tipo_reposicion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id_categoria: int

    model_config = {"from_attributes": True}

# --- ESQUEMAS PARA PRODUCTO ---
class ProductoBase(BaseModel):
    id_categoria: int
    codigo_barras: Optional[str] = None
    nombre: str
    precio_costo: float
    precio_venta: float
    stock_actual: int = 0
    stock_minimo: Optional[int] = None
    fecha_vencimiento: Optional[date] = None
    activo: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id_producto: int

    model_config = {"from_attributes": True}
# ==========================================
# ESQUEMAS PARA VENTAS (TAREA #7)
# ==========================================

# 1. Lo que recibimos desde la pantalla para CADA producto
class DetalleVentaCreate(BaseModel):
    id_producto: int
    cantidad: int

# 2. Lo que recibimos para crear la VENTA en general
class VentaCreate(BaseModel):
    medio_pago: str
    detalles: List[DetalleVentaCreate]

# 3. Lo que le respondemos a la pantalla una vez guardado (Ticket)
class DetalleVentaResponse(BaseModel):
    id_detalle: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float

    model_config = {"from_attributes": True}

class VentaResponse(BaseModel):
    id_venta: int
    fecha_hora: datetime
    total: float
    medio_pago: str
    detalles: List[DetalleVentaResponse]

    model_config = {"from_attributes": True}
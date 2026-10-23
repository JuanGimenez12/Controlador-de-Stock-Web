from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from modelo.conexion import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    tipo_reposicion = Column(String(50))

    # Relación bidireccional
    productos = relationship("Producto", back_populates="categoria")

# ==========================================
# MÓDULO DE INVENTARIO Y PRODUCTOS (UNIFICADO)
# ==========================================
class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=True)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    codigo_barras = Column(String(50), nullable=True)
    nombre = Column(String(150), nullable=False)
    marca = Column(String(100), nullable=True)         # <-- NUEVO
    descripcion = Column(String(255), nullable=True)
    precio_costo = Column(Numeric(10, 2), nullable=False)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)
    unidad_medida = Column(String(20), default="Unidad")
    unidades_por_caja = Column(Integer, default=1)
    fecha_vencimiento = Column(Date, nullable=True)
    activo = Column(Boolean, default=True)

    # Relación bidireccional
    categoria = relationship("Categoria", back_populates="productos")
    proveedor = relationship("Proveedor", back_populates="productos")
    movimientos_stock = relationship("MovimientoStock", back_populates="producto")

# ==========================================
# MÓDULO DE PROVEEDORES
# ==========================================
class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    cuit = Column(String(20), nullable=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True)

    # Relación bidireccional
    productos = relationship("Producto", back_populates="proveedor")
    compras = relationship("Compra", back_populates="proveedor")


# ==========================================
# MÓDULO DE MOVIMIENTOS DE STOCK (auditoría de inventario)
# ==========================================
class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'Entrada', 'Salida', 'Ajuste', 'Merma'
    cantidad = Column(Integer, nullable=False)
    stock_resultante = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    fecha_hora = Column(DateTime, default=func.now())

    # Relaciones
    producto = relationship("Producto", back_populates="movimientos_stock")
    usuario = relationship("Usuario")


# ==========================================
# MÓDULO DE COMPRAS A PROVEEDORES (reposición de stock)
# ==========================================
class Compra(Base):
    __tablename__ = "compras"

    id_compra = Column(Integer, primary_key=True, autoincrement=True)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    fecha_hora = Column(DateTime, default=func.now())
    total = Column(Numeric(10, 2), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)

    # Relaciones
    proveedor = relationship("Proveedor", back_populates="compras")
    usuario = relationship("Usuario")
    detalles = relationship("DetalleCompra", back_populates="compra")


class DetalleCompra(Base):
    __tablename__ = "detalle_compra"

    id_detalle_compra = Column(Integer, primary_key=True, autoincrement=True)
    id_compra = Column(Integer, ForeignKey("compras.id_compra"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    # Relaciones
    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto")


# ==========================================
# MODELOS PARA VENTAS (TAREA #7)
# ==========================================
class Venta(Base):
    __tablename__ = "ventas"

    id_venta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_hora = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)
    medio_pago = Column(String(50), nullable=False) 
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=True) # Solo en ventas a cuenta corriente

    # Relación bidireccional con el detalle
    detalles = relationship("DetalleVenta", back_populates="venta")


class DetalleVenta(Base):
    __tablename__ = "detalles_venta"

    id_detalle = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_venta = Column(Integer, ForeignKey("ventas.id_venta"))
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relaciones
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")
    
# ==========================================
# MÓDULO DE USUARIOS Y SEGURIDAD
# ==========================================
class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Permisos tildables según documentación MVP
    permiso_ventas = Column(Boolean, default=True)
    permiso_inventario = Column(Boolean, default=False)
    permiso_caja = Column(Boolean, default=False)
    
    activo = Column(Boolean, default=True)

# ==========================================
# MÓDULO DE CAJA
# ==========================================
class Caja(Base):
    __tablename__ = "cajas"

    id_caja = Column(Integer, primary_key=True, autoincrement=True)
    fecha_apertura = Column(DateTime, default=func.now())
    fecha_cierre = Column(DateTime, nullable=True)
    saldo_inicial = Column(Numeric(10, 2), nullable=False)
    saldo_final = Column(Numeric(10, 2), nullable=True)
    estado = Column(String(20), default='Abierta') # Puede ser 'Abierta' o 'Cerrada'


class MovimientoCaja(Base):
    __tablename__ = "movimientos_caja"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_caja = Column(Integer, ForeignKey("cajas.id_caja"))
    tipo = Column(String(50), nullable=False) # Ej: 'INGRESO' (pago de deuda en efectivo)
    monto = Column(Numeric(10, 2), nullable=False)
    descripcion = Column(String(255), nullable=True)
    fecha_hora = Column(DateTime, default=func.now())
    
# ==========================================
# MÓDULO DE CLIENTES Y CUENTA CORRIENTE (TAREA #9)
# ==========================================
class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(String(20), nullable=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(50), nullable=True)
    direccion = Column(String(200), nullable=True)
    saldo_deuda = Column(Numeric(10, 2), default=0.00) # Acá guardaremos cuánta plata nos debe
    activo = Column(Boolean, default=True) # Para la baja lógica


class MovimientoCuenta(Base):
    __tablename__ = "movimientos_cuenta"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"))
    tipo = Column(String(50), nullable=False) # 'VENTA' suma deuda, 'PAGO' la descuenta
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_hora = Column(DateTime, default=func.now())
    descripcion = Column(String(255), nullable=True)

        
# ==========================================
# MÓDULO DE PROMOCIONES (TAREA #13)
# ==========================================
class Promocion(Base):
    __tablename__ = "promociones"

    id_promocion = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    tipo_descuento = Column(String(50), nullable=True) # Ej: "Porcentaje" o "Monto"
    valor_descuento = Column(Numeric(10, 2), nullable=True)
    activa = Column(Boolean, default=True)
    
    
class PromocionProducto(Base):
    __tablename__ = "promocion_productos"

    id_promocion_detalle = Column(Integer, primary_key=True, autoincrement=True)
    id_promocion = Column(Integer, ForeignKey('promociones.id_promocion'), nullable=False)
    codigo_producto = Column(String(50), nullable=False)
    cantidad_requerida = Column(Integer, nullable=False)           

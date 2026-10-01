"""Reglas de la cuenta corriente (fiado): límites de mora y cálculo del estado de un cliente."""

from datetime import datetime
from decimal import Decimal
from modelo.modelos import MovimientoCuenta

# Límites definidos con el cliente (Alcance v2.0). Por ahora solo generan aviso, no bloquean.
PLAZO_MAXIMO_DIAS = 30
IMPORTE_MAXIMO = Decimal("50000")

TIPOS_QUE_SUMAN = ("VENTA", "SALDO_INICIAL")
TIPOS_QUE_RESTAN = ("PAGO",)


def estado_mora(db, cliente, monto_extra=0):
    """Devuelve la deuda (sumando monto_extra, ej. la venta que se está por fiar), los días desde la
    deuda impaga más vieja y si supera cada límite.

    Los pagos cancelan primero las deudas más viejas. La deuda cargada antes de que existiera el
    historial no tiene fecha: cuenta para el importe pero no para el plazo."""
    deuda = (cliente.saldo_deuda or Decimal("0")) + Decimal(str(monto_extra))
    movimientos = (
        db.query(MovimientoCuenta)
        .filter(MovimientoCuenta.id_cliente == cliente.id_cliente)
        .order_by(MovimientoCuenta.fecha_hora, MovimientoCuenta.id_movimiento)
        .all()
    )
    cargos = [(m.fecha_hora, m.monto) for m in movimientos if m.tipo in TIPOS_QUE_SUMAN]
    pagado = sum((m.monto for m in movimientos if m.tipo in TIPOS_QUE_RESTAN), Decimal("0"))

    saldo_sin_fecha = (cliente.saldo_deuda or Decimal("0")) - (sum((c[1] for c in cargos), Decimal("0")) - pagado)
    if saldo_sin_fecha > 0:
        cargos.insert(0, (None, saldo_sin_fecha))

    dias = None
    for fecha, monto in cargos:
        if pagado >= monto:
            pagado -= monto
            continue
        if fecha is not None:
            dias = (datetime.now().date() - fecha.date()).days
            break
        pagado = Decimal("0")

    return {
        "deuda": deuda,
        "dias": dias,
        "excede_importe": deuda > IMPORTE_MAXIMO,
        "excede_plazo": dias is not None and dias > PLAZO_MAXIMO_DIAS,
    }


def texto_mora(estado):
    """Texto de aviso para mostrar al operador, o "" si el cliente está dentro de los límites."""
    avisos = []
    if estado["excede_importe"]:
        avisos.append(f"debe $ {estado['deuda']:.2f} (límite $ {IMPORTE_MAXIMO:.0f})")
    if estado["excede_plazo"]:
        avisos.append(f"tiene deuda de hace {estado['dias']} días (plazo {PLAZO_MAXIMO_DIAS} días)")
    return " y ".join(avisos)


import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="DRAME 360° | Simulador financiero",
    page_icon="📊",
    layout="wide"
)

# Identidad visual
st.markdown("""
<style>
    .stApp { background-color: #FAF8F5; }
    h1, h2, h3 { color: #573F32 !important; }
    div[data-testid="stMetric"] {
        background: #F0E6DC;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #E4D6C9;
    }
    div[data-testid="stMetricLabel"] {
        color: #654D40;
    }
    .stButton button {
        background-color: #654D40;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def pesos(valor):
    return f"${valor:,.0f}".replace(",", ".")


def calcular(precio, costo, descuento, despacho,
             umbral, comision, embalaje):
    """Simulación de contribución por pedido, en CLP."""

    venta_bruta = max(0, precio - descuento)
    ingreso_neto = venta_bruta / 1.19

    # Comisión aplicada al cobro efectivo, IVA incluido
    comision_total = venta_bruta * (comision / 100) * 1.19

    # Se compara el umbral con el valor final del pedido
    despacho_empresa = despacho if venta_bruta >= umbral else 0

    costos_variables = (
        costo + comision_total + embalaje + despacho_empresa
    )

    contribucion = ingreso_neto - costos_variables

    margen = (
        contribucion / ingreso_neto * 100
        if ingreso_neto > 0 else 0
    )

    return {
        "venta_bruta": venta_bruta,
        "ingreso_neto": ingreso_neto,
        "costo": costo,
        "comision": comision_total,
        "embalaje": embalaje,
        "despacho": despacho_empresa,
        "costos": costos_variables,
        "contribucion": contribucion,
        "margen": margen
    }


st.title("DRAME 360°")
st.subheader("Simulador de rentabilidad por pedido")

st.info(
    "Prototipo académico demostrativo. Los valores iniciales "
    "son ficticios y no representan resultados reales de Drame SPA."
)

st.markdown("### 1. Datos de la simulación")

izquierda, derecha = st.columns(2)

with izquierda:
    precio = st.number_input(
        "Precio de venta (IVA incluido) · CLP",
        min_value=0,
        value=39990,
        step=1000
    )

    costo = st.number_input(
        "Costo unitario neto del producto · CLP",
        min_value=0,
        value=18000,
        step=500
    )

    descuento = st.number_input(
        "Descuento aplicado · CLP",
        min_value=0,
        value=0,
        step=500
    )

with derecha:
    despacho = st.number_input(
        "Costo de despacho para Drame · CLP",
        min_value=0,
        value=3500,
        step=500
    )

    umbral = st.selectbox(
        "Umbral para despacho gratuito · CLP",
        options=[34990, 39990, 80000],
        format_func=pesos
    )

    comision = st.number_input(
        "Comisión de pago (%) antes de IVA",
        min_value=0.0,
        max_value=100.0,
        value=3.19,
        step=0.1
    )

    embalaje = st.number_input(
        "Costo de embalaje neto · CLP",
        min_value=0,
        value=300,
        step=100
    )

# Validaciones
if precio == 0:
    st.error("El precio de venta debe ser mayor que cero.")
    st.stop()

if descuento > precio:
    st.error(
        "El descuento no puede superar el precio de venta. "
        "Corrige el valor para continuar."
    )
    st.stop()

if descuento == precio:
    st.warning(
        "El descuento equivale al 100% del precio. "
        "No se genera ingreso por esta venta."
    )

resultado = calcular(
    precio, costo, descuento, despacho,
    umbral, comision, embalaje
)

st.divider()
st.markdown("### 2. Resultados de la simulación")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Ingreso neto sin IVA",
    pesos(resultado["ingreso_neto"])
)

col2.metric(
    "Margen de contribución",
    pesos(resultado["contribucion"])
)

col3.metric(
    "Margen sobre venta neta",
    f'{resultado["margen"]:.1f}%'
)

if resultado["contribucion"] < 0:
    st.error(
        "Este escenario presenta una contribución negativa: "
        "los costos variables estimados superan el ingreso neto."
    )
else:
    st.success(
        "La contribución estimada de este escenario es "
        "igual o superior a cero."
    )

st.markdown("#### Desglose por pedido")

detalle = pd.DataFrame([
    ["Cobro al cliente (IVA incluido)",
     resultado["venta_bruta"]],
    ["Ingreso neto sin IVA",
     resultado["ingreso_neto"]],
    ["Costo unitario neto",
     resultado["costo"]],
    ["Comisión de pago estimada",
     resultado["comision"]],
    ["Costo de embalaje",
     resultado["embalaje"]],
    ["Despacho asumido por Drame",
     resultado["despacho"]],
    ["Costos variables estimados",
     resultado["costos"]],
    ["Contribución estimada",
     resultado["contribucion"]]
], columns=["Concepto", "Monto (CLP)"])

detalle["Monto (CLP)"] = detalle["Monto (CLP)"].apply(pesos)

st.dataframe(
    detalle,
    hide_index=True,
    use_container_width=True
)

if resultado["despacho"] > 0:
    st.info(
        "El pedido alcanza el umbral seleccionado. "
        "El modelo supone que Drame asume el costo de despacho."
    )
else:
    st.info(
        "El pedido no alcanza el umbral seleccionado. "
        "El modelo supone que Drame no asume el costo de despacho."
    )

st.divider()
st.markdown("### 3. Comparación de escenarios de despacho")

escenarios = []

for limite in [34990, 39990, 80000]:
    calculo = calcular(
        precio, costo, descuento, despacho,
        limite, comision, embalaje
    )

    escenarios.append({
        "Umbral": pesos(limite),
        "Despacho asumido": pesos(calculo["despacho"]),
        "Contribución": pesos(calculo["contribucion"]),
        "Margen": f'{calculo["margen"]:.1f}%'
    })

st.dataframe(
    pd.DataFrame(escenarios),
    hide_index=True,
    use_container_width=True
)

st.caption(
    "La comparación mantiene constantes los datos de un mismo "
    "pedido y modifica únicamente el umbral de despacho gratuito."
)

st.divider()
st.markdown("### 4. Alcance del prototipo")

st.write(
    "DRAME 360° permite explorar cómo determinadas decisiones "
    "comerciales pueden modificar la contribución estimada "
    "de una venta. Esta versión utiliza datos ingresados "
    "manualmente y no está conectada a Shopify, SII ni Claude."
)

st.caption(
    "Supuestos: IVA de venta del 19%; comisión de pago calculada "
    "sobre el cobro final, más IVA; costos de producto y embalaje "
    "ingresados como valores netos. El costo de despacho se "
    "considera un costo económico completo. No se incluyen "
    "costos fijos, devoluciones, publicidad ni otros gastos. "
    "El resultado es una contribución estimada, no utilidad neta."
)

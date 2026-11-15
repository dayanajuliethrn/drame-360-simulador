import streamlit as st

st.set_page_config(page_title='DRAME 360° | Simulador financiero', page_icon='📊', layout='wide')
st.markdown('''<style>
.stApp {background-color:#FCFAF7;color:#30231D}
h1,h2,h3 {color:#593B2C!important}
[data-testid="stMetric"] {background:#F0E5DA;padding:16px;border-radius:12px}
</style>''', unsafe_allow_html=True)
st.title('DRAME 360°')
st.subheader('Simulador de rentabilidad por pedido')
st.info('Prototipo académico. Los valores iniciales son ficticios y no corresponden a resultados reales de Drame SPA.')

left,right=st.columns(2)
with left:
    precio=st.number_input('Precio de venta (IVA incluido) · CLP',min_value=0, value=39990,step=1000)
    costo=st.number_input('Costo unitario neto · CLP',min_value=0,value=18000,step=500)
    descuento=st.number_input('Descuento aplicado · CLP',min_value=0,value=0,step=500)
with right:
    despacho=st.number_input('Costo del despacho · CLP',min_value=0,value=3500,step=500)
    umbral=st.selectbox('Umbral para despacho gratuito · CLP',[80000,39990,34990],index=2,format_func=lambda x:f'${x:,.0f}'.replace(',','.'))
    comision_pct=st.number_input('Comisión de pago (%) antes de IVA',min_value=0.0,max_value=100.0,value=3.19,step=0.1)
    embalaje=st.number_input('Costo de embalaje neto · CLP',min_value=0,value=300,step=100)

cobro=max(precio-descuento,0)
neto=cobro/1.19
comision=cobro*(comision_pct/100)*1.19
costo_envio=despacho if cobro>=umbral else 0
contribucion=neto-costo-comision-embalaje-costo_envio
margen=(contribucion/neto*100) if neto>0 else 0
fmt=lambda v:'${:,.0f}'.format(v).replace(',','.')
st.divider()
st.markdown('### Resultados de la simulación')
a,b,c=st.columns(3)
a.metric('Ingreso neto sin IVA',fmt(neto))
b.metric('Margen de contribución',fmt(contribucion))
c.metric('Margen sobre venta neta',f'{margen:.1f}%')
st.write('**Desglose por pedido**')
st.table({'Concepto':['Cobro al cliente (IVA incluido)','Ingreso neto sin IVA','Costo unitario neto','Comisión de pago estimada','Embalaje neto','Despacho asumido por Drame','Contribución estimada'], 'Monto (CLP)':[fmt(cobro),fmt(neto),fmt(-costo),fmt(-comision),fmt(-embalaje),fmt(-costo_envio),fmt(contribucion)]})
if cobro>=umbral:
    st.warning('El pedido cumple el umbral elegido: se descuenta el costo de despacho de la contribución.')
else:
    st.success('El pedido no alcanza el umbral: el modelo supone que Drame no asume el costo de despacho.')
st.caption('Supuestos: IVA de ventas 19%; comisión de pago calculada sobre el cobro final e incrementada en 19% de IVA; costos unitarios y embalaje ingresados netos. No incluye gastos fijos, devoluciones, impuestos a la renta ni otros costos variables. El margen de contribución no equivale a utilidad neta. El tratamiento tributario de las comisiones se simplifica para fines académicos.')
st.caption('DRAME 360° · Demostración académica · Elaboración propia')

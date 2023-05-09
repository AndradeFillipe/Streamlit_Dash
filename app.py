import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
from datetime import datetime
import plotly.express as px
from PIL import Image

root = 'data/application_record.csv'
rec = 'data/credit_record.csv'

cr = pd.read_csv(root)
rc = pd.read_csv(rec)

df = rc.merge(cr, how='inner', on='ID')

df_safra = df.groupby(['ID']).agg(
   MOB_START=  ('MONTHS_BALANCE', min)).reset_index()

df_safra['SAFRA'] = datetime.today() + df_safra['MOB_START'].astype("timedelta64[M]")
df = df.merge(df_safra,how='inner',on='ID')
df['FLAG_OWN_CAR'] = np.where(df['FLAG_OWN_CAR'] == 'Y',1,0)
df['FLAG_OWN_REALTY'] = np.where(df['FLAG_OWN_REALTY'] == 'Y',1,0)
df['FLAG_MOBIL'] = df['FLAG_MOBIL'].astype(int)
df['FLAG_WORK_PHONE'] = df['FLAG_WORK_PHONE'].astype(int)
df['FLAG_PHONE'] = df['FLAG_PHONE'].astype(int)
df['FLAG_EMAIL'] = df['FLAG_EMAIL'].astype(int)
df['FLAG_PROP'] = np.where(df['FLAG_OWN_CAR']+df['FLAG_OWN_REALTY']>0,'Sim','Não')
df['FLAG_COM'] = np.where(df['FLAG_PHONE'] + df['FLAG_EMAIL'] > 0,'Sim','Não')

df['MOB'] = abs(df['MOB_START']) - abs(df['MONTHS_BALANCE']) 
df['MES'] = df['SAFRA'] + df['MOB'].astype("timedelta64[M]")
df['SAFRA'] = df['SAFRA'].dt.strftime('%m-%Y')
df['MES'] = df['MES'].dt.strftime('%m-%Y')

#df_mob = df.pivot_table(index=['SAFRA','MOB','FLAG_PROP','FLAG_COM','STATUS'],
#                        values=['DAYS_BIRTH','DAYS_EMPLOYED','AMT_INCOME_TOTAL','ID'],
#                        aggfunc={'DAYS_BIRTH':np.mean,'DAYS_EMPLOYED':np.mean,
#                                 'AMT_INCOME_TOTAL':np.mean,'ID':'count'})
#df_mob = df_mob.reset_index()
#
#df_carteira = df.pivot_table(index=['MES','FLAG_PROP','FLAG_COM','STATUS'],
#                        values=['DAYS_BIRTH','DAYS_EMPLOYED','AMT_INCOME_TOTAL','ID'],
#                        aggfunc={'DAYS_BIRTH':np.mean,'DAYS_EMPLOYED':np.mean,
#                                 'AMT_INCOME_TOTAL':np.mean,'ID':'count'})
#df_carteira = df_carteira.reset_index()


st.set_page_config(page_title='DASHBORAD CLIENTES')
st.header('Relatório Perfil dos Clientes')
st.sidebar.write("Filtros")
status = st.sidebar.selectbox(
    "Status Cliente",
    ('Sem Debitos','Normal','Atraso 30 dias','Atraso 60 dias',
     'Atraso 90 dias','Atraso 120 dias','Atraso 150','Atraso 150+')
)

com =  st.sidebar.selectbox(
    "Flag Comunicação",
    ('Tudo','Sim', 'Não')
)

prop =  st.sidebar.selectbox(
    "Flag Propriedades",
    ('Tudo','Sim', 'Não')
)
selected = option_menu(
    menu_title='Navegação',
    options=['Carteira','Safra','Contato'],
    icons= ['bar-chart-fill','graph-up-arrow','envelope'],
    menu_icon='cast',
    default_index=0,
    orientation='horizontal'
)


if status == 'Normal':
    s = 'C'
elif status == 'Atraso 30 dias':
    s = '0'
elif status == 'Atraso 60 dias':
    s = '1'
elif status == 'Atraso 90 dias':
    s = '2'
elif status == 'Atraso 120 dias':
    s = '3'
elif status == 'Atraso 150 dias':
    s = '4'
elif status == 'Atraso 150+':
    s = '5'
else:
    s = 'X'

if prop == 'Tudo' and com != 'Tudo':
    base = df.loc[df.FLAG_COM ==com].reset_index()
elif prop != 'Tudo' and com == 'Tudo':
    base = df.loc[df.FLAG_PROP ==prop].reset_index()
elif prop == 'Tudo' and com == 'Tudo':
    base = df
else:
    base = df.loc[(df.FLAG_PROP ==prop) & (df.FLAG_COM ==com)].reset_index()

if selected ==  'Carteira':   
    st.subheader(f'Visão {selected}')
    safra = st.sidebar.slider(
        "Safra",
        datetime(2019, 1, 1), datetime(2023,12,12),
        (datetime(2019, 1, 1),datetime(2023,12,12)),
        format="MM/YY")

    base.MES = pd.to_datetime(base.MES,format='%m-%Y')
    base = base.loc[(base['MES'] > safra[0]) & (base['MES'] <= safra[1])]    
    carteira = base.pivot_table(index='MES', columns='STATUS',
                                values='ID', aggfunc='count')
    carteira = carteira.reset_index()
    carteira.MES = pd.to_datetime(carteira.MES,format='%m-%Y')
    carteira = carteira[['MES',s]]
    carteira.rename(columns={s:'QUANTIDADE'},inplace=True)
    barras = px.bar(carteira, 
                    x='MES',
                    y='QUANTIDADE',
                    text='QUANTIDADE',
                    title= f'Gráfico da Quantidade de Pessoas com Status: {status}',
                    color_discrete_sequence=['#F63366']*len(carteira),
                    template='plotly_white')
    st.plotly_chart(barras)

    renda = base.pivot_table(index='MES', columns='STATUS',
                                values='AMT_INCOME_TOTAL', aggfunc=np.mean)
    renda = renda.reset_index()
    renda.MES = pd.to_datetime(renda.MES,format='%m-%Y')

    renda = renda[['MES',s]]
    renda.rename(columns={s:'MEDIA'},inplace=True)

    linha = px.line(
                    renda,
                    x='MES',
                    y='MEDIA',
                    title= f'Gráfico da Renda Média Anual das Pessoas com Status: {status}',
                    color_discrete_sequence=['#F63366']*len(carteira),
                    template='plotly_white'
    )

    st.plotly_chart(linha)

    carteira2 = base.pivot_table(index=['MES','STATUS'],
                                values='ID', aggfunc='count')
    carteira2 = carteira2.reset_index()
    carteira2.MES = pd.to_datetime(carteira2.MES,format='%m-%Y')
    carteira2.rename(columns={'ID':'QUANTIDADE'},inplace=True)

    barras_status = px.bar(carteira2, 
                    x='MES',
                    y='QUANTIDADE',
                    text='QUANTIDADE',
                    color='STATUS',
                    template='plotly_white')

    st.plotly_chart(barras_status)
elif selected == 'Safra':
    st.subheader(f'Visão {selected}')
    safras = base['SAFRA'].unique().tolist()
    safra_select = st.sidebar.multiselect('SAFRAS',
                                  safras,
                                  default=safras[0])
    base2 = base.loc[base.STATUS == s].reset_index(drop=True)
    safra = base2.pivot_table(index=['MOB','SAFRA'],
                                values='ID', aggfunc='count')
    safra = safra.reset_index()
    safra = safra.loc[safra.SAFRA.isin(safra_select)]
    linhas_safra = px.line(safra, 
                    x='MOB',
                    y='ID',
                    title= f'Gráfico por Safra da Quantidade de Pessoas com Status: {status}',
                    color='SAFRA',
                    template='plotly_white')
    st.plotly_chart(linhas_safra)
    safra_status = base.pivot_table(index=['SAFRA','STATUS'],
                                values='ID', aggfunc='count')
    safra_status = safra_status.reset_index()
    safra_status.rename(columns={'ID':'QUANTIDADE'},inplace=True)
    safra_status = safra_status.loc[safra_status.SAFRA.isin(safra_select)]
    barras_status = px.bar(safra_status, 
                    x='SAFRA',
                    y='QUANTIDADE',
                    text='QUANTIDADE',
                    color='STATUS',
                    barmode='group',
                    template='plotly_white')
    st.plotly_chart(barras_status)
else:
    NAME = "Fillipe Almeida"
    st.subheader(f'Contato')
    DESCRIPTION = """
    Bacharel em Engenharia Elétrica na Universidade Federal do Recôncavo da Bahia, 
    e atualmente Analista de Dados Jr na FortBrasil.
    """
    EMAIL = "andradefillipe0@gmail.com"
    SOCIAL_MEDIA = {
        "LinkedIn": "https://www.linkedin.com/in/fillipe-almeida-89464b53/",
        "GitHub": "https://github.com/AndradeFillipe",
        "Medium": "https://medium.com/@lipe97.fa",
    }
    
    profile_pic = Image.open('data\perfil.jpg')

    # --- HERO SECTION ---
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.image(profile_pic, width=230)

    with col2:
        st.title(NAME)
        st.write(DESCRIPTION)
        st.write("📫", EMAIL)
        cols = st.columns(len(SOCIAL_MEDIA))
        for index, (platform, link) in enumerate(SOCIAL_MEDIA.items()):
            cols[index].write(f"[{platform}]({link})")

    









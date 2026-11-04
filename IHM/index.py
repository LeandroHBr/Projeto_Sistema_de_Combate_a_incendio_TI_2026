import streamlit as st
import cv2 as cv
import matplotlib.pyplot as plt
from ultralytics import YOLO
import torch
from streamlit_webrtc import webrtc_streamer
import av
from My_serial.Comando_Serial import Serial_CMD,ler_resposta_serial
from Save_data.rw_data import Read_data,Write_data
from streamlit_autorefresh import st_autorefresh
import numpy as np

# realizando configuração de página
st.set_page_config(
    page_title="IHM Monitoramento",
    layout="wide",
)
##sst_autorefresh(interval=1000, key="refresh_tela")


# inicializado o modelo yolo 
@st.cache_resource
def carregar_modelo():
    cuda = torch.cuda.is_available()
    if cuda:
        print("GPU reconhecida")
        print("Carregando modelo YOLO")
        #model = YOLO('./runs/detect/train-13/weights/best.pt')
        model = YOLO('../Modelo_treinado/best2.pt')
        
        return model
    else:
        print("O programas está usando a CPU")


#carregando modelo/câmera
model = carregar_modelo()
cap = cv.VideoCapture(0)
#carregando dados.json
if "Data" not in st.session_state:
    st.session_state.Data = Read_data()
st.session_state.Data = Read_data()

# Css do footer
st.markdown("""
    <style>
        div[data-testid="stVerticalBlockr"] {
            background-color: #1e2129; /* Cor do fundo do card (cinza escuro) */
            border: 1px solid #2d313e; /* Cor da borda */
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# footer style

footer="""<style>
::-webkit-scrollbar {
            display: none !important;
        }
        * {
            -ms-overflow-style: none !important;  /* IE/Edge */
            scrollbar-width: none !important;  /* Firefox */
        }

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #0e1117;
color: #f1f1f1;
text-align: right;
}

p{
    padding-right:10px;
}
</style>
<div class="footer">
<p>Projeto IFMG Itabirito</p>
</div>
"""



# Criando a sidebar

conf = st.sidebar.slider(label="Limiar de confiança",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.Data["Conf"],
    step=0.01)


if (st.session_state.Data["Alert"] == 1):
    if st.sidebar.button(label="Reconhecimento de Alarme",width="stretch",type="primary"):
        Serial_CMD(0x0B)
        Write_data(None,0,None)
if st.sidebar.toggle(label="Silenciar Alarme",value=0):
    Serial_CMD(0x05)
    alarm_status = "Silenc."
    controle_val= 1;
else:
    Serial_CMD(0x06)
    alarm_status = "Operante"
    controle_val = 0;

submit_button = st.sidebar.button(label="Salvar Configuração", type="secondary",width="stretch")

    

# processando os frames

def processar_frame(frame: av.VideoFrame) -> av.VideoFrame:
    # aproveitando para atualizar o json 
    
    ser_result = ler_resposta_serial();
    if(ser_result == "liga"):
        Write_data(None, 1,"ligado")
    elif(ser_result == "desliga"):
        st.session_state.bomb_state = "Deslig";
        Write_data(None, None,"Desligado")
    
    # Converte o frame da câmera direto para array BGR (NumPy)
    img = frame.to_ndarray(format="bgr24")
    
    # Pega o limiar atualizado do slider
    limiar = st.session_state.get("conf", 0.37)
            
    results = model.predict(
        source=img,
        classes=[1],
        conf=conf,
        imgsz=1920,
        verbose=False,
    )
    
    
    if(len(results[0].boxes) > 0 ):
        Serial_CMD(0x0A);
    
    annotated_img = results[0].plot()   
    return av.VideoFrame.from_ndarray(annotated_img, format="bgr24")




# criando a tela principal
@st.fragment(run_every="1s")
def painel_status(conf, alarm_status):
    # Recarrega os dados atualizados do JSON
    data = Read_data()

    c1, c2, c3, c4 = st.columns([30, 23, 23, 23])

    c1.metric(
        label="STATUS DO ALARME",
        value=alarm_status
    )

    c2.metric(
        label="CONFIANÇA %",
        value=f"{conf * 100:.1f}%"
    )

    c3.metric(
        label="BOMBA",
        value=data["Bomb"]
    )

    c4.metric(
        label="Setor",
        value="A"
    )

_, col_principal, _ = st.columns([5, 90, 5])
with col_principal:
    #subdividindo a coluna principal em 2 partes
    col1,col2 = st.columns([50,50],border=True)
    with col1:
        with st.container(border=True):
            st.text("📷 Câmera em Tempo Real",width="stretch")
            
            webrtc_streamer(
            key="camera_ihm",
            video_frame_callback=processar_frame,
            media_stream_constraints={"video": True, "audio": False}
            )
            
            if (st.session_state.Data["Alert"] == 1):
                st.warning("Alerta de incêndio detectado! Pressione 'Reconhecer Alarme' para cancelar o estado de alerta.",icon="⚠️");
            
    with col2:
        
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([30,23,23,23])
            painel_status(conf,alarm_status)
        st.text("Localização do Evento",width="stretch")
        st.iframe(src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2253.249423528859!2d-43.794326817447725!3d-20.25528571246853!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0xa6a9ffaeab8bb9%3A0xb0e79dac425bd831!2sIFMG%20Campus%20Avan%C3%A7ado%20Itabirito!5e0!3m2!1spt-BR!2sbr!4v1790909136337!5m2!1spt-BR!2sbr")
    


#Inciando State do vídeo
if "cap" not in st.session_state:
    st.session_state.cap = cap

#salvando dados
if(submit_button):
    Write_data(conf, None,st.session_state.Data["Bomb"])

#adicionando o footer
st.markdown(footer,unsafe_allow_html=True)

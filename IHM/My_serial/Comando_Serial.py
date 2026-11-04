import serial
import time
import serial.tools.list_ports

ser = None

def Find_arduino():
    portas = serial.tools.list_ports.comports()

    for porta in portas:
        describe = porta.description.lower().find("arduino")
        if(describe != -1):
            return porta.device
    return None

def conectar_arduino():
    global ser
    if(ser and ser.is_open):
        return ser
    else:
        porta = Find_arduino()
        if(porta):
            try:
                ser = serial.Serial(porta, 9600, timeout=2)
                time.sleep(2)
                return ser
            except serial.SerialException as e:
                print(f"Erro ao acessar a porta: {e}")
                ser = None
                return ser
        else:
            print("PORTA NÃO ENCONTRADA")
            return None

def Serial_CMD(CMD):
    
    ser = conectar_arduino()
    if ser:
        try:
            ser.write(bytes([CMD]));
        except Exception as e:
            try:
                ser.close()
            except Exception:
                pass
            ser = None
            return None
    
def ler_resposta_serial():
    """Função rápida que pode ser chamada no loop do Streamlit para ler logs do Arduino sem travar"""
    ser = conectar_arduino()
    if ser:
        try:
            if ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8', errors='ignore').strip()
                if linha:
                    return linha
        except Exception:
            pass
    




#include <stdio.h>

#define BOMBA_INCENDIO 13
#define BOMBA_EXAUSTOR 12
#define SENSOR_CHAMA_DIGITAl_PIN 9
#define SENSOR_CHAMA_ANALOG_PIN A0
#define BUZZER 11

//#define CMD_ON_BI  0x01 
//#define CMD_OFF_BI 0x02  
//#define CMD_ON_BE  0x03  
//#define CMD_OFF_BE 0x04
#define ALARM_MUTE_ON 0x05
#define ALARM_MUTE_OFF 0x06

//#define MANUAL 0x08
//#define AUTO 0x09
#define Fire_video_detected 0x0A
#define ALARM_RECOGNEZE 0x0B
#define Evacuation_timer 3000



// bombas acionam com negativo
//bool CMD_BOMBA_01 = 0;
//bool CMD_BOMBA_02 = 0;
bool CMD_ALARME = 0;
bool mode = 0; // 0 automático
bool fire_init = 0;
bool Alarm_state = 0;
bool pump_init = 0;
bool Recognize = 0;
bool mute = 0;
bool alarm_state = 0;
static unsigned long timer = 0;
static unsigned long timer_pup = 0;

#define f_min 600
#define f_max 1300
unsigned long previousMillis = 0; 
const long interval = 7; 
unsigned long currentMillis_b;
int freq = 600;
int direcao = 10;



void setup() {
  Serial.begin(9600);
  pinMode(BOMBA_INCENDIO, OUTPUT);
  pinMode(BOMBA_EXAUSTOR, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BOMBA_INCENDIO,HIGH);
}

void som(int pin, bool ligar, bool mute){
  if(!ligar || mute){
    noTone(pin);
    return;
  }
  unsigned long currentMillis_b = millis();

  // Verifica se já passou o tempo do intervalo
  if (currentMillis_b - previousMillis >= interval) {
    previousMillis = currentMillis_b; // ATUALIZA CORRETAMENTE

    // Muda a frequência
    freq += direcao;

    // Inverte a direção se chegar nos limites
    if (freq >= f_max) {
      direcao = -10; // Começa a descer
    } else if (freq <= f_min) {
      direcao = 10;  // Começa a subir
    }

    tone(pin, freq);
  }
}



void loop() {

  int estadoDigital = digitalRead(SENSOR_CHAMA_DIGITAl_PIN);
  if(estadoDigital ==  1){
    if(pump_init == 0){
      fire_init = 1;
      }else{
        timer_pup = millis();
      }
  }


  if (Serial.available() > 0) {
    // Lê o comando até encontrar a quebra de linha (\n)
    byte comando = Serial.read();

    switch (comando){   
    case ALARM_MUTE_ON:
      Serial.println("silenciador de alarme ativado");
      mute = 1;
      break;
    case ALARM_MUTE_OFF:
      Serial.println("silenciador de alarme desativado");
      mute = 0;
      break;
    case ALARM_RECOGNEZE:
      Serial.println("Saindo do modo de alerta");
      Recognize = 1;
      break;
    case Fire_video_detected:
      if(pump_init == 0){
      fire_init = (mode == 0) ? 1 : 0;
      }else{
        timer_pup = millis();
      }
      break;
    default:
      Serial.println("COMANDO DESCONHECIDO");
    }
  }

  if(mode == 0 && fire_init){
    // liga o alarme
    alarm_state = 1;
    if(timer == 0){
    Serial.println("ligando alarme");
    timer = millis();
    }

    if(millis() - timer >= Evacuation_timer){
    fire_init = 0;
    pump_init = 1;
    timer_pup = millis();
    Serial.println("Ligando Bomba ...");
    Serial.println("liga");

    }
  }

  if(mode == 0 && pump_init){
    digitalWrite(BOMBA_INCENDIO,LOW);


    if(millis() - timer_pup >= 5000){
    // obs não vou zerar o timer aqui, porque pode ser um falso negativo
    // resetar o sistema totalmente apenas quando o alarme desligar (fim do perigo)
    pump_init = 0;
    Serial.println("Desligando Bomba de incêncio");
    digitalWrite(BOMBA_INCENDIO,HIGH);
    Serial.println("desliga");
    }
  }

  if(pump_init == 0 && fire_init == 0 && Recognize==1){
    Recognize = 0;
    timer = 0;
    alarm_state = 0;
  }

  som(BUZZER, alarm_state, mute);

}
#include <WiFi.h>
#include <WebServer.h>

// Configuración de red Wi-Fi
const char *ssid = "POCO_X6_Pro_5G";
const char *password = "123456779m";

// Pines
#define PIN_LED_VERDE     21
#define PIN_LED_AMARILLO  22
#define PIN_LED_ROJO      23

WebServer server(80);

// Secuencia
bool secuenciaActiva = false;
unsigned long previousMillis = 0;
int estadoSemaforo = 0;

// Tiempos
unsigned long tiempoVerde = 2000;
unsigned long tiempoAmarillo = 2000;
unsigned long tiempoRojo = 2000;

void setup() {
  Serial.begin(115200);

  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_AMARILLO, OUTPUT);
  pinMode(PIN_LED_ROJO, OUTPUT);

  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("¡Conectado!");
  Serial.println(WiFi.localIP());

  // Control individual de LEDs
  server.on("/led/verde/on", [](){ 
    digitalWrite(PIN_LED_VERDE,HIGH); 
    server.send(200,"text/plain","LED Verde Encendido"); });
  server.on("/led/verde/off", [](){ 
    digitalWrite(PIN_LED_VERDE,LOW); 
    server.send(200,"text/plain","LED Verde Apagado"); });

  server.on("/led/amarillo/on", [](){ 
    digitalWrite(PIN_LED_AMARILLO,HIGH); 
    server.send(200,"text/plain","LED Amarillo Encendido"); });
  server.on("/led/amarillo/off", [](){ 
    digitalWrite(PIN_LED_AMARILLO,LOW); 
    server.send(200,"text/plain","LED Amarillo Apagado"); });

  server.on("/led/rojo/on", [](){ 
    digitalWrite(PIN_LED_ROJO,HIGH); 
    server.send(200,"text/plain","LED Rojo Encendido"); });
  server.on("/led/rojo/off", [](){ 
    digitalWrite(PIN_LED_ROJO,LOW); 
    server.send(200,"text/plain","LED Rojo Apagado"); });

  // Secuencia semáforo
server.on("/led/secuencia/on", [](){ 
    secuenciaActiva = true; 
    estadoSemaforo=0; 
    server.send(200,"text/plain","Secuencia INICIADA"); 
});

  server.on("/led/secuencia/off", [](){ 
    secuenciaActiva = false; 
    digitalWrite(PIN_LED_VERDE,LOW); 
    digitalWrite(PIN_LED_AMARILLO,LOW); 
    digitalWrite(PIN_LED_ROJO,LOW); 
    server.send(200,"text/plain","Secuencia DETENIDA"); });

  // Ajuste de tiempos
  server.on("/set/verde", [](){ 
    if(server.hasArg("t")) tiempoVerde = server.arg("t").toInt(); 
    server.send(200,"text/plain","Tiempo Verde actualizado"); });
  server.on("/set/amarillo", [](){ 
    if(server.hasArg("t")) tiempoAmarillo = server.arg("t").toInt(); 
    server.send(200,"text/plain","Tiempo Amarillo actualizado"); });
  server.on("/set/rojo", [](){ 
    if(server.hasArg("t")) tiempoRojo = server.arg("t").toInt(); 
    server.send(200,"text/plain","Tiempo Rojo actualizado"); });

  server.begin();
  Serial.println("Servidor HTTP iniciado");
}

void loop() {
  server.handleClient();

  if(secuenciaActiva){
    unsigned long currentMillis = millis();

    switch(estadoSemaforo){
      case 0: // Verde
      {
        // Tiempo restante para cambiar a amarillo
        unsigned long tiempoRestante = tiempoVerde - (currentMillis - previousMillis);

        // Hacer parpadear en los últimos 2 segundos
        if(tiempoRestante <= 2000){
          // Parpadeo cada 500 ms
          if((currentMillis / 500) % 2 == 0){
            digitalWrite(PIN_LED_VERDE, HIGH);
          } else {
            digitalWrite(PIN_LED_VERDE, LOW);
          }
        } else {
          digitalWrite(PIN_LED_VERDE, HIGH); // Verde fijo mientras no está en parpadeo
        }

        digitalWrite(PIN_LED_AMARILLO, LOW);
        digitalWrite(PIN_LED_ROJO, LOW);

        // Cambiar a amarillo cuando el tiempo verde termine
        if(currentMillis - previousMillis >= tiempoVerde){
          previousMillis = currentMillis;
          digitalWrite(PIN_LED_VERDE, LOW);
          digitalWrite(PIN_LED_AMARILLO, HIGH);
          estadoSemaforo = 1;
        }
      }
      break;

      case 1: // Amarillo
        if(currentMillis - previousMillis >= tiempoAmarillo){
          previousMillis = currentMillis;
          digitalWrite(PIN_LED_AMARILLO, LOW);
          digitalWrite(PIN_LED_ROJO, HIGH);
          estadoSemaforo = 2;
        }
        break;

      case 2: // Rojo
        if(currentMillis - previousMillis >= tiempoRojo){
          previousMillis = currentMillis;
          digitalWrite(PIN_LED_ROJO, LOW);
          digitalWrite(PIN_LED_VERDE, HIGH);
          estadoSemaforo = 0;
        }
        break;
    }
  }
}


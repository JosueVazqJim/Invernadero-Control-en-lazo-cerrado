#include <WiFi.h>
#include <WebServer.h>

// Configuración de red Wi-Fi
const char *ssid = "BUAP_Trabajadores"; //"Wifi"; //"BUAP_Trabajadores";   // Cambia por tu SSID
const char *password = "BuaPW0rk.2017"; // "12345678"; //"BuaPW0rk.2017";   // Cambia por tu contraseña Wi-Fi

// Crear un servidor web en el puerto 80
WebServer server(80);

// Pines segmentos (a-g)
const int segA = 21;
const int segB = 19;
const int segC = 18;
const int segD = 5;
const int segE = 4;
const int segF = 2;
const int segG = 15;

// Pines cátodos comunes
const int com1 = 22; // Decenas
const int com2 = 23; // Unidades

// Pin LM35
const int pinLM35 = 34;  // Entrada analógica

// Pin ventilador
const int pinVentilador = 25;

// pin Foco
const int pinFoco = 26;

// Mapeo dígitos (a,b,c,d,e,f,g)
const byte numeros[10][7] = {
  {1,1,1,1,1,1,0}, // 0
  {0,1,1,0,0,0,0}, // 1
  {1,1,0,1,1,0,1}, // 2
  {1,1,1,1,0,0,1}, // 3
  {0,1,1,0,0,1,1}, // 4
  {1,0,1,1,0,1,1}, // 5
  {1,0,1,1,1,1,1}, // 6
  {1,1,1,0,0,0,0}, // 7
  {1,1,1,1,1,1,1}, // 8
  {1,1,1,1,0,1,1}  // 9
};

const int segmentos[7] = {segA, segB, segC, segD, segE, segF, segG};

// --- Variables para sensor y tiempo ---
unsigned long ultimaLectura = 0;
int temperatura = 0;  // Valor estable que se mostrará

//variables lazo abierto
bool lazoAbierto = false; 

//variables de temporizador
bool temporizadorVentilador = false; //indica si el ventilador esta en modo temporizador
unsigned long tiempoInicioVentilador = 0; //guarda el tiempo en que se encendio el ventilador
unsigned long tiempoVentilador = 0; //tiempo del temporizador

bool temporizadorFoco = false; //indica si el foco esta en modo temporizador
unsigned long tiempoInicioFoco = 0; //guarda el tiempo en que se encendio el foco
unsigned long tiempoFoco = 0; //tiempo del temporizador

//variables de lazo cerrado 
bool lazoCerrado = false; //indica si el control de temperatura esta activo
int temperaturaDeseada = 25; //valor por defecto de temperatura deseada

void setup() {
  // Iniciar comunicación serial a 115200 baudios
  Serial.begin(115200);
  
  for (int i = 0; i < 7; i++) {
    pinMode(segmentos[i], OUTPUT);
    digitalWrite(segmentos[i], LOW);
  }

  pinMode(com1, OUTPUT);
  pinMode(com2, OUTPUT);
  digitalWrite(com1, HIGH);
  digitalWrite(com2, HIGH);

  analogReadResolution(12); // 12 bits (0-4095)

  //configuracion de los pines del ventilador y foco
  pinMode(pinVentilador, OUTPUT);
  pinMode(pinFoco, OUTPUT);

  digitalWrite(pinVentilador, HIGH); //apaga el ventilador TIENE LOGICA INVERTIDA
  digitalWrite(pinFoco, HIGH); //apaga el foco TIENE LOGICA INVERTIDA

  // Conectar a la red Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("¡Conectado!");
  Serial.println(WiFi.localIP());

  // Iniciar el servidor
  server.begin();
  Serial.println("Servidor HTTP iniciado");


  //-- endpoints para manipular manualmente los actuadores ---
  server.on("/ventilador/on", HTTP_GET, []() {
    // acción manual: cancelar control automático y cualquier temporizador del ventilador
    lazoAbierto = true;
    lazoCerrado = false;
    temporizadorVentilador = false;
    tiempoVentilador = 0;
    digitalWrite(pinVentilador, LOW);  // Enciende el ventilador
    Serial.println("Ventiladores Encendidos (manual)");
    server.send(200, "text/plain", "Ventiladores Encendidos (manual)");
  });

  server.on("/ventilador/off", HTTP_GET, []() {
    // acción manual: cancelar control automático y cualquier temporizador del ventilador
    lazoAbierto = true;
    lazoCerrado = false;
    temporizadorVentilador = false;
    tiempoVentilador = 0;
    digitalWrite(pinVentilador, HIGH);  // Apaga el ventilador
    Serial.println("Ventiladores Apagados (manual)");
    server.send(200, "text/plain", "Ventiladores Apagados (manual)");
  });

  server.on("/foco/on", HTTP_GET, []() {
    // acción manual: cancelar control automático y cualquier temporizador del foco
    lazoAbierto = true;
    lazoCerrado = false;
    temporizadorFoco = false;
    tiempoFoco = 0;
    digitalWrite(pinFoco, LOW);  // Enciende el foco
    Serial.println("Focos Encendidos (manual)");
    server.send(200, "text/plain", "Focos Encendidos (manual)");
  });

  server.on("/foco/off", HTTP_GET, []() {
    // acción manual: cancelar control automático y cualquier temporizador del foco
    lazoAbierto = true;
    lazoCerrado = false;
    temporizadorFoco = false;
    tiempoFoco = 0;
    digitalWrite(pinFoco, HIGH);  // Apaga el foco
    Serial.println("Focos Apagados (manual)");
    server.send(200, "text/plain", "Focos Apagados (manual)");
  });

  server.on("/estado", HTTP_GET, []() {
    unsigned long remVentMs = 0;
    unsigned long remFocoMs = 0;

    unsigned long elapsedVent = millis() - tiempoInicioVentilador;
    unsigned long elapsedFoco = millis() - tiempoInicioFoco;

    if (temporizadorVentilador && tiempoVentilador > elapsedVent) {
      remVentMs = tiempoVentilador - elapsedVent;
    } else {
      remVentMs = 0;
    }

    if (temporizadorFoco && tiempoFoco > elapsedFoco) {
      remFocoMs = tiempoFoco - elapsedFoco;
    } else {
      remFocoMs = 0;
    }

    // opcional: convertir a segundos (enteros)
    unsigned long remVentSec = remVentMs ? (remVentMs + 999) / 1000 : 0;
    unsigned long remFocoSec = remFocoMs ? (remFocoMs + 999) / 1000 : 0;
    unsigned long definidoVentSec = tiempoVentilador / 1000;
    unsigned long definidoFocoSec = tiempoFoco / 1000;

    String json = "{";
    json += "\"temperatura\":" + String(temperatura) + ",";
    json += "\"temperaturaDeseada\":" + String(temperaturaDeseada) + ",";
    json += "\"ventilador\":" + String(digitalRead(pinVentilador) == LOW ? "true" : "false") + ",";
    json += "\"foco\":" + String(digitalRead(pinFoco) == LOW ? "true" : "false") + ",";
    json += "\"temporizadorVentilador\":" + String(temporizadorVentilador ? "true" : "false") + ",";
    json += "\"tiempoDefinidoVentilador_s\":" + String(definidoVentSec) + ",";
    json += "\"tiempoRestanteVentilador_s\":" + String(remVentSec) + ",";
    json += "\"temporizadorFoco\":" + String(temporizadorFoco ? "true" : "false") + ",";
    json += "\"tiempoDefinidoFoco_s\":" + String(definidoFocoSec) + ",";
    json += "\"tiempoRestanteFoco_s\":" + String(remFocoSec) + ",";
    json += "\"lazoAbierto\":" + String(lazoAbierto ? "true" : "false") + ",";
    json += "\"lazoCerrado\":" + String(lazoCerrado ? "true" : "false");
    json += "}";
    server.send(200, "application/json", json);
  });

  // endpoints de temporizador (se interpreta 'tiempo' en segundos en query param)
  server.on("/ventilador/temporizador", HTTP_GET, []() {
    if (!server.hasArg("tiempo")) {
      server.send(400, "text/plain", "Falta el parametro 'tiempo'");
      return;
    }

    // temporizador = modo manual (anula lazo cerrado)
    lazoAbierto = true;
    lazoCerrado = false;

    // apagar antes por si estaba en otro estado
    digitalWrite(pinVentilador, HIGH);

    String tiempoStr = server.arg("tiempo");
    unsigned long segundos = tiempoStr.toInt();
    if (segundos == 0 && tiempoStr != "0") {
      server.send(400, "text/plain", "Parametro 'tiempo' no valido.");
      return;
    }
    tiempoVentilador = segundos * 1000UL; // almacenar en ms
    temporizadorVentilador = true;
    tiempoInicioVentilador = millis();
    digitalWrite(pinVentilador, LOW);  // Enciende el ventilador
    Serial.println("Ventiladores Encendidos con temporizador de " + tiempoStr + " s");
    server.send(200, "text/plain", "Ventiladores Encendidos con temporizador de " + tiempoStr + " s");
  });

  // Pausar temporizador del ventilador (solo este)
  server.on("/ventilador/temporizador/pause", HTTP_GET, []() {
    // Pausar únicamente el temporizador del ventilador
    temporizadorVentilador = false;
    tiempoVentilador = 0;
    // Apagar el ventilador al pausar (lógica invertida: HIGH = apagado)
    digitalWrite(pinVentilador, HIGH);
    Serial.println("Temporizador ventilador pausado");
    server.send(200, "text/plain", "Temporizador ventilador pausado");
  });

  server.on("/foco/temporizador", HTTP_GET, []() {
    if (!server.hasArg("tiempo")) {
      server.send(400, "text/plain", "Falta el parametro 'tiempo'");
      return;
    }

    // temporizador = modo manual (anula lazo cerrado)
    lazoAbierto = true;
    lazoCerrado = false;

    // apagar antes por si estaba en otro estado
    digitalWrite(pinFoco, HIGH);

    String tiempoStr = server.arg("tiempo");
    unsigned long segundos = tiempoStr.toInt();
    if (segundos == 0 && tiempoStr != "0") {
      server.send(400, "text/plain", "Parametro 'tiempo' no valido.");
      return;
    }
    tiempoFoco = segundos * 1000UL; // almacenar en ms
    temporizadorFoco = true;
    tiempoInicioFoco = millis();
    digitalWrite(pinFoco, LOW);  // Enciende el foco
    Serial.println("Focos Encendidos con temporizador de " + tiempoStr + " s");
    server.send(200, "text/plain", "Focos Encendidos con temporizador de " + tiempoStr + " s");
  });

  // Pausar temporizador del foco (solo este)
  server.on("/foco/temporizador/pause", HTTP_GET, []() {
    // Pausar únicamente el temporizador del foco
    temporizadorFoco = false;
    tiempoFoco = 0;
    // Apagar el foco al pausar (lógica invertida: HIGH = apagado)
    digitalWrite(pinFoco, HIGH);
    Serial.println("Temporizador foco pausado");
    server.send(200, "text/plain", "Temporizador foco pausado");
  });

  // temperatura deseada (activa control automático y cancela temporizadores/manuales)
  server.on("/goalTemp", HTTP_GET, []() {
    if (!server.hasArg("temp")) {
      server.send(400, "text/plain", "Falta el parametro 'temp'");
      return;
    }

    String tempStr = server.arg("temp");
    int temp = tempStr.toInt();
    if (temp < 0 || temp > 60) {
      server.send(400, "text/plain", "Parametro 'temp' no valido. Debe estar entre 0 y 60.");
      return;
    }
    // activar control automático y cancelar cualquier temporizador/manual
    temperaturaDeseada = temp;
    lazoAbierto = false;
    lazoCerrado = true;
    temporizadorVentilador = false;
    temporizadorFoco = false;
    tiempoVentilador = 0;
    tiempoFoco = 0;
    digitalWrite(pinVentilador, HIGH);  // Apaga el ventilador
    digitalWrite(pinFoco, HIGH);  // Apaga el foco
    Serial.println("Temperatura deseada establecida a " + tempStr + " (control automático)");
    server.send(200, "text/plain", "Temperatura deseada establecida a " + tempStr + " (control automatico)");
  });

  // Soporte para rutas tipo /ventilador/temporizador/5000 o /foco/temporizador/5000 (ms)
  server.onNotFound([]() {
    String uri = server.uri();
    const String prefV = "/ventilador/temporizador/";
    const String prefF = "/foco/temporizador/";
    if (uri.startsWith(prefV) || uri.startsWith(prefF)) {
      bool isVent = uri.startsWith(prefV);
      String tiempoStr = uri.substring(isVent ? prefV.length() : prefF.length());
      if (tiempoStr.length() == 0) {
        server.send(400, "text/plain", "Parametro de tiempo faltante");
        return;
      }
      // validar dígitos
      for (unsigned int i = 0; i < tiempoStr.length(); ++i) {
        if (!isDigit(tiempoStr.charAt(i))) {
          server.send(400, "text/plain", "Parametro de tiempo no valido");
          return;
        }
      }
      unsigned long ms = tiempoStr.toInt(); // interpretar como milisegundos
      if (isVent) {
        lazoAbierto = true;
        lazoCerrado = false;
        tiempoVentilador = ms;
        temporizadorVentilador = true;
        tiempoInicioVentilador = millis();
        digitalWrite(pinVentilador, LOW);
        Serial.println("Ventiladores Encendidos con temporizador de " + tiempoStr + " ms");
        server.send(200, "text/plain", "Ventiladores Encendidos con temporizador de " + tiempoStr + " ms");
        return;
      } else {
        lazoAbierto = true;
        lazoCerrado = false;
        tiempoFoco = ms;
        temporizadorFoco = true;
        tiempoInicioFoco = millis();
        digitalWrite(pinFoco, LOW);
        Serial.println("Focos Encendidos con temporizador de " + tiempoStr + " ms");
        server.send(200, "text/plain", "Focos Encendidos con temporizador de " + tiempoStr + " ms");
        return;
      }
    }
    server.send(404, "text/plain", "Not found");
  });

}

void loop() {

  // Maneja las solicitudes entrantes
  server.handleClient();

  // --- Actualizar sensor cada 2 segundos ---
  // millis lleva el tiempo desde que se arranco la esp
  //ultima lectura el conteo hasta la ultima lectura
  //calcula si han pasado dos segundo desde la ultima lectura
  if (millis() - ultimaLectura >= 2000) {
    int raw = analogRead(pinLM35);
    float voltaje = raw * (3.3 / 4095.0);
    float tempC = voltaje * 100.0 + 11;
    Serial.print(tempC);
    Serial.println();  

    temperatura = constrain((int)tempC, 0, 99); //limita la temperatura solo de 0 a 99
    ultimaLectura = millis();
  }

  // --- Mostrar en displays (multiplexado continuo) ---
  int decenas = temperatura / 10;
  int unidades = temperatura % 10;

  mostrarDigito(decenas, com1);
  delay(5);
  mostrarDigito(unidades, com2);
  delay(5);

  //control de temporizador del ventilador
  controlTemporizadorVentilador();

  //control de temporizador del foco
  controlTemporizadorFoco();

  //control de lazo cerrado
  controlLazoCerrado();

  
}

void mostrarDigito(int num, int comPin) {
  digitalWrite(com1, HIGH);
  digitalWrite(com2, HIGH);

  for (int i = 0; i < 7; i++) {
    digitalWrite(segmentos[i], numeros[num][i]);
  }

  digitalWrite(comPin, LOW);
}

void controlTemporizadorVentilador() {
  if (temporizadorVentilador && lazoAbierto) {
    if (millis() - tiempoInicioVentilador >= tiempoVentilador) {
      digitalWrite(pinVentilador, HIGH);  // Apaga el ventilador
      temporizadorVentilador = false; //desactiva el temporizador
      Serial.println("Ventiladores Apagados despues de temporizador");
    }
  }
}

void controlTemporizadorFoco() {
  if (temporizadorFoco && lazoAbierto) {
    if (millis() - tiempoInicioFoco >= tiempoFoco) {
      digitalWrite(pinFoco, HIGH);  // Apaga el foco
      temporizadorFoco = false; //desactiva el temporizador
      Serial.println("Focos Apagados despues de temporizador");
    }
  }
}

void controlLazoCerrado() {
  if (lazoCerrado) {
    if (temperatura > temperaturaDeseada + 1) { //histeresis de 1 grado como margen
      digitalWrite(pinVentilador, LOW);  // Enciende el ventilador
      digitalWrite(pinFoco, HIGH);  // Apaga el foco
      Serial.println("Ventiladores Encendidos y Focos Apagados por control de temperatura");
    } else if (temperatura < temperaturaDeseada - 1) {
      digitalWrite(pinVentilador, HIGH);  // Apaga el ventilador
      digitalWrite(pinFoco, LOW);  // Enciende el foco
      Serial.println("Ventiladores Apagados y Focos Encendidos por control de temperatura");
    }
  }
}

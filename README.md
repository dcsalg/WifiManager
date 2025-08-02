# 📡 WifiManager para MicroPython (ESP32)

**Versión:** 1.1.1  
**Autor:** Daniel Salgado  
**Empresa:** Ayresnet  
**Licencia:** MIT  
**Última modificación:** 16/01/2025  

---

## 📘 Descripción

**WifiManager** es una librería para facilitar la conexión WiFi de dispositivos **ESP32** utilizando **MicroPython**. Si no hay una red configurada o el usuario mantiene presionado un botón, el módulo inicia un **portal cautivo con servidor web**, donde se pueden seleccionar redes WiFi y guardar las credenciales directamente desde un navegador.

Ideal para proyectos sin pantalla, dispositivos de IoT, automatización del hogar, y cualquier situación donde se necesite una configuración WiFi amigable.

---

## 🧠 Características

- ✅ Punto de acceso (Access Point) automático
- ✅ Portal cautivo con redirección DNS
- ✅ Interfaz web para seleccionar red y contraseña
- ✅ Guarda las credenciales en `wifi.json`
- ✅ Botón físico para resetear la configuración
- ✅ LED de estado con parpadeos indicativos
- ✅ Código modular, documentado y fácil de usar

---

## ⚙️ Requisitos

- MicroPython v1.20 o superior
- Dispositivo: ESP32
- Archivos HTML: `index.html`, `success.html`, `error.html`

### Pines por defecto (modificables en el código):
- LED: `GPIO2`
- Botón de configuración: `GPIO0`

---

## 📦 Archivos incluidos

| Archivo           | Descripción                                  |
|-------------------|----------------------------------------------|
| `wifimanager.py`  | Código principal del WifiManager             |
| `index.html`      | Página web de selección de red               |
| `success.html`    | Página mostrada tras conexión exitosa        |
| `error.html`      | Página mostrada en caso de error             |
| `wifi.json`       | (Se genera automáticamente con credenciales) |
| `examples/main.py`| Ejemplo de uso (opcional)                    |

---

## 🚀 Instalación

1. Descarga o clona este repositorio.
2. Copia estos archivos a tu ESP32 (usando Thonny, ampy, rshell, etc.):

```
wifimanager.py
index.html
success.html
error.html
```

3. En tu archivo `main.py`, importa y ejecuta WifiManager:

```python
from wifimanager import WifiManager

wm = WifiManager()
wm.run()
```

---

## 🧪 Ejemplo completo

```python
from wifimanager import WifiManager

def main():
    wm = WifiManager()
    wm.run()

if __name__ == "__main__":
    main()
```

---

## 🔧 Uso del botón

Si mantenés presionado el botón físico (GPIO0 por defecto) durante **más de 5 segundos**, se borran las credenciales WiFi almacenadas y el ESP32 se reinicia automáticamente en modo **Access Point**, mostrando la interfaz web para volver a configurar la red.

---

## 🌐 ¿Qué hace el portal cautivo?

- El ESP32 crea una red WiFi con nombre:  
  **`WiFi Managaer Ayresnet`**  
  Contraseña: `123456789`

- Desde cualquier celular o navegador, al conectarse, redirige automáticamente a una página donde se pueden ver las redes disponibles.

- El usuario selecciona una red, ingresa la contraseña y el ESP32 guarda esa información para usarla al iniciar.

- Luego se reinicia y se conecta automáticamente a esa red WiFi.

---

## 💡 Indicaciones con el LED

- 🔄 Parpadeos rápidos: intentando conectar al WiFi  
- ✅ Encendido fijo: conexión WiFi exitosa  
- ⚠️ Parpadeos lentos: sin credenciales o fallo de conexión  
- 🔴 Parpadeo rápido continuo: error crítico  

---

## 🧩 Cómo integrar en tu proyecto

Simplemente importá y ejecutá `WifiManager` antes de inicializar cualquier conexión a Internet o servidor:

```python
from wifimanager import WifiManager

wm = WifiManager()
wm.run()

# A partir de aquí, ya hay WiFi si fue exitoso
```

Podés verificar el estado de conexión o la potencia de señal con:

```python
print("¿Conectado?", wm.check_connection_status())
print("Potencia RSSI:", wm.get_dbm_wifi(), "dBm")
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

- Reportá errores o problemas
- Sugerí nuevas funcionalidades
- Abrí un pull request

---

## 📜 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.  
Podés usarlo, modificarlo y distribuirlo libremente.  
Solo se solicita mantener el crédito al autor original.

---

## ✉️ Contacto

**Daniel Salgado**  
Ayresnet  

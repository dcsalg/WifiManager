#-------------------------------------------------
# Wifi Manager
# Version: 1.1.1
# Desarrollado: Daniel Salgado
# Empresa: Ayresnet
# Fecha: 26/09/2024
#
# Historial de versiones:
#   - 1.1.1 (16/01/2025): Se extiende tiempo de conexion y realiza a 3 intentos.
#   - 1.1.0 (26/09/2024): Se añadió la funcionalidad de DNS.
#   - 1.0.1 (25/03/2024): Correcciones menores.
#   - 1.0.0 (24/03/2024): Versión inicial.
#-------------------------------------------------


import ujson as json
import os
import network
import machine
import socket
import time
import _thread
import re

__version__ = "1.1.0"
__author__ = "Daniel Salgado"
__description__ = "Librería para gestionar configuraciones de WiFi en dispositivos ESP32 utilizando MicroPython."
__created__ = "2024-03-25"
__modified__ = "2024-09-26"
__license__ = "MIT"
__dependencies__ = ["ujson", "network"]

def show_info():
    print("Wifi Manager")
    print("Version:", __version__)
    print("Author:", __author__)
    print("Description:", __description__)
    print("Created:", __created__)
    print("Last Modified:", __modified__)
    print("License:", __license__)
    print("Dependencies:", ", ".join(__dependencies__))

# Para mostrar la información
show_info()

class WifiManager:
    def __init__(self):
        # Configurar el Access Point
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid='WiFi Managaer Ayresnet', password='123456789')
        self.ap.config(authmode=3)  # WPA2 channel=6,

        # Añadir un atributo para el estado de la conexión
        self.connection_status = False
        self.sta_if = None
#         self.__temp_connect = 10

        # Configuración del botón
        self.button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)  # Cambiar a tu pin
        self.setup_button()
        self.estado_boton = False
        
        # Configuración del led estados
        self.led = machine.Pin(2, machine.Pin.OUT)  # Cambiar a tu pin del LED, por defecto en ESP32 el pin GPIO2 se usa como LED
        self.led.off()  # Apagar el LED inicialmente
        
        # Leer los archivos HTML
        self.html_content = self.load_html("index.html")
        self.html_success = self.load_html("success.html")
        self.html_error = self.load_html("error.html")

    def load_html(self, filename):
        """Lee un archivo HTML y devuelve su contenido."""
        try:
            with open(filename, 'r') as file:
                return file.read()
        except OSError as e:
            print(f"Error al leer el archivo {filename}: {e}")
            return "<html><body><h1>Error al cargar el HTML</h1></body></html>"


    def setup_button(self):
        self.button.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.enter_config_mode)

    def enter_config_mode(self, pin):
#         time.sleep(5)  # Esperar 5 segundos
#         if not self.button.value():  # Si el botón sigue presionado
#             self.estado_boton = True
        start_time = time.ticks_ms()
        while not self.button.value():  # Mientras el botón esté presionado
            if time.ticks_diff(time.ticks_ms(), start_time) > 5000:  # Más de 5 segundos
                self.estado_boton = True
                print("Botón presionado por más de 5 segundos. Entrando al modo de configuración.")
                self.erase_credentials()  # Eliminar credenciales
                print("Credenciales borradas. Reiniciando...")
                time.sleep(1)
                machine.reset()  # Reiniciar el ESP32

        print("Botón presionado pero no por suficiente tiempo.")
        

    def turn_led_on(self):
        """Enciende el LED."""
        self.led.on()

    def turn_led_off(self):
        """Apaga el LED."""
        self.led.off()

    def blink_led(self, times=1, delay=0.2):
        """Parpadea el LED un número específico de veces."""
        for _ in range(times):
            self.turn_led_on()
            time.sleep(delay)
            self.turn_led_off()
            time.sleep(delay)
            
    def start_dns_server(self):
        addr = ('0.0.0.0', 53)
        self.dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dns_socket.bind(addr)
        print("Servidor DNS iniciado en el puerto 53...")

        try:
            while True:
                data, addr = self.dns_socket.recvfrom(512)
                dns_response = self.build_dns_response(data)
                self.dns_socket.sendto(dns_response, addr)
        except Exception as e:
            print(f"Error manejando la solicitud DNS: {e}")
        finally:
            self.dns_socket.close()


    def build_dns_response(self, data):
        # Construir una respuesta DNS simple, redirigiendo a 192.168.4.1
        return data[:2] + b'\x81\x80' + data[4:6] * 2 + b'\x00\x00\x00\x00' + data[12:] + b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04\xc0\xa8\x04\x01'


    # Función para guardar las credenciales en un archivo JSON
    def save_credentials(self, credentials):
    #     raise Exception("Error al guardar las credenciales")
        with open('wifi.json', 'w') as f:
            json.dump(credentials, f)

    # Función para eliminar las credenciales
    def erase_credentials(self):
        if 'wifi.json' in os.listdir():
            os.remove('wifi.json')
            print("Credenciales borradas.")
        else:
            print("No se encontraron credenciales para borrar.")
            
    # Función para cargar las credenciales desde el archivo JSON
    def load_credentials(self):
        try:
            with open('wifi.json', 'r') as f:
                return json.load(f)
        except OSError as e:
            print("Error al abrir el archivo wifi.json:", e)
            return None
        except ValueError as e:
            print("Error al cargar las credenciales desde el archivo wifi.json:", e)
            return None        

    # Función para obtener las redes WiFi disponibles y sus señales
    def obtener_redes_wifi(self):
        try:
            redes_wifi = network.WLAN(network.STA_IF)
            redes_wifi.active(True)
            redes_encontradas = redes_wifi.scan()
            redes_ordenadas_por_señal = sorted(redes_encontradas, key=lambda x: x[3], reverse=True)[:5]  
            return [(red[0].decode('utf-8'), red[3]) for red in redes_ordenadas_por_señal if len(red[0]) > 0]
        except Exception as e:
            print(f"Error al obtener redes WiFi: {e}")
            return []


    # Función para generar las opciones de las redes WiFi en el HTML
    def generar_opciones_redes_wifi(self):
        opciones = ""
        redes = self.obtener_redes_wifi()
        for red, potencia in redes:
            opciones += f"<li>{red} - Pot.: {potencia} dBm</li>"
        return opciones


    def handle_request(self, client_socket):
        try:
            # Leer la solicitud HTTP del cliente
            request = client_socket.recv(1024).decode('utf-8')
            print(f"Solicitud recibida: {request}")

            # Extraer el host de la solicitud
            host_match = re.search(r'Host: ([\w\.\-]+)', request)
            if host_match:
                requested_host = host_match.group(1)
                print(f"Host solicitado: {requested_host}")
            else:
                requested_host = ''

            # Manejar la solicitud POST para guardar las credenciales
            if 'POST /save' in request:
                body_index = request.find('\r\n\r\n') + 4
                body = request[body_index:]
                form_data = {}

                # Analizar los datos del formulario
                for item in body.split('&'):
                    key, value = item.split('=')
                    form_data[key] = value

                # Guardar las credenciales
                ssid = form_data.get('ssid', '')
                password = form_data.get('password', '')
                credentials = {'ssid': ssid, 'password': password}
                self.save_credentials(credentials)

                # Enviar respuesta de éxito y reiniciar
                success_response = "HTTP/1.1 200 OK\r\n"
                success_response += "Content-Type: text/html\r\n"
                success_response += "Connection: close\r\n\r\n"
                success_response += self.html_success
                client_socket.send(success_response.encode())
                client_socket.close()
                time.sleep(1)
                machine.reset()
                return

            # Para cualquier solicitud GET o si la solicitud contiene referencias a otros dominios
            else:
                # Verificar si la solicitud es para la página de redirección
                if 'GET' in request and (requested_host == '' or '192.168.4.1' in requested_host):
                    # Responder con la página de configuración
                    response = "HTTP/1.1 200 OK\r\n"
                    response += "Content-Type: text/html\r\n"
                    response += "Connection: close\r\n\r\n"
                    response += self.html_content.replace("<!-- Aquí se agregarán las opciones de las redes WiFi -->", self.generar_opciones_redes_wifi())

                # Cualquier otra solicitud (como favicon o dominios externos), redirigir a la IP local
                else:
                    response = "HTTP/1.1 302 Found\r\n"
                    response += "Location: http://192.168.4.1/\r\n"
                    response += "Connection: close\r\n\r\n"

                # Enviar la respuesta correspondiente
                client_socket.send(response.encode())
                client_socket.close()

        except Exception as e:
            print(f"Error manejando la solicitud: {e}")
            # Enviar la respuesta de error
            error_response = "HTTP/1.1 200 OK\r\n"
            error_response += "Content-Type: text/html\r\n"
            error_response += "Connection: close\r\n\r\n"
            error_response += self.html_error
            client_socket.send(error_response.encode())
            client_socket.close()
            return

#     def connect_to_wifi(self):
#         credentials = self.load_credentials()
#         if credentials:
#             ssid = credentials.get('ssid')
#             password = credentials.get('password')
#             print(f"Intentando conectar a {ssid}...")
#          # Configurar la interfaz WiFi en modo estación (STA)
#             self.sta_if = network.WLAN(network.STA_IF)
#             self.sta_if.active(True)  # Activar la interfaz STA
#             self.sta_if.connect(ssid, password)
# 
#             # Indicar visualmente que el ESP32 está intentando conectar
#             self.blink_led(5, 0.1)
#             
#             timeout = 10  # Tiempo de espera para la conexión
#             while timeout > 0:
#                 if self.sta_if.isconnected():
#                     print("Conectado a WiFi:", self.sta_if.ifconfig())
#                     self.turn_led_on()
#                     return True
#                 timeout -= 1
#                 time.sleep(1)
# #             print("Error al conectar al WiFi. Reiniciando...")
# #             machine.reset()  # Reiniciar si no se pudo conectar
#             print("No se pudo conectar a la red WiFi.")
#             self.blink_led(2, 0.5)  # Parpadeo largo para indicar error
#         else:
#             print("No se encontraron credenciales para conectar.")
#             self.blink_led(1, 1)  # Parpadeo lento para indicar que no hay credenciales
#             
#         return False        

    # Método para verificar el estado de la conexión
    def check_connection_status(self):
        self.connection_status = self.sta_if.isconnected()
        return self.connection_status
 
    def get_dbm_wifi(self):
        return self.sta_if.status('rssi')
    
    def connect_to_wifi(self):
        credentials = self.load_credentials()
        if credentials:
            ssid = credentials.get('ssid')
            password = credentials.get('password')
            print(f"Intentando conectar a {ssid}...")

            # Configurar la interfaz WiFi en modo estación (STA)
            self.sta_if = network.WLAN(network.STA_IF)
            self.sta_if.active(True)
            self.sta_if.connect(ssid, password)

            # Indicar visualmente que el ESP32 está intentando conectar
            self.blink_led(5, 0.1)

            timeout = 30  # Aumentar tiempo de espera a 30 segundos
            while timeout > 0:
                if self.sta_if.isconnected():
                    print("Conectado a WiFi:", self.sta_if.ifconfig())
                    self.turn_led_on()
                    return True
                timeout -= 1
                time.sleep(1)

            print("No se pudo conectar a la red WiFi. Intentando nuevamente...")
            self.sta_if.disconnect()
            time.sleep(5)
        else:
            print("No se encontraron credenciales para conectar.")
            self.blink_led(1, 1)  # Parpadeo lento para indicar que no hay credenciales

        return False


    def start_web_server(self):
        self.turn_led_on()
        addr = ('0.0.0.0', 80)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(addr)
        s.listen(5)

        print("Servidor web iniciado en el puerto 80, esperando conexiones...")

        while True:
            # Aceptar solicitudes del servidor web
            client_socket, client_address = s.accept()
            print(f"Conexión de: {client_address}")
            self.handle_request(client_socket)

#     def run(self):
#         self.blink_led(5)
#         time.sleep(3)
#         self.turn_led_off()
#         if not self.estado_boton:
#             # Dentro de la clase WifiManager, después de guardar las credenciales
#             en_linea = self.connect_to_wifi()  # Llama a esta función para intentar conectarte al WiFi
#             print("se conecto a la red: ", en_linea)
#             if not en_linea:
#                 _thread.start_new_thread(self.start_dns_server, ())
#                 self.start_web_server()
#                 
#         else:
#             _thread.start_new_thread(self.start_dns_server, ())
#             self.start_web_server()

    def run(self):
        self.blink_led(5)  # Indicador visual de inicio
        time.sleep(3)
        self.turn_led_off()

        try:
            # Intentar conectarse a WiFi si el botón no está presionado
            if not self.estado_boton:
                max_retries = 1  # Número de intentos de conexión
                connected = False
                for attempt in range(max_retries):
                    print(f"Intentando conectar al WiFi (Intento {attempt + 1}/{max_retries})...")
                    connected = self.connect_to_wifi()
                    if connected:
                        break
                    time.sleep(2)  # Esperar antes de reintentar

                if connected:
                    print("Conexión WiFi exitosa.")
                    return  # Salir del método si la conexión fue exitosa
                
            credentials = self.load_credentials()
            
            if not credentials:

                # Si no se pudo conectar al WiFi o el botón está activado, iniciar modo de configuración
                print("Iniciando modo de configuración...")
                _thread.start_new_thread(self.start_dns_server, ())
                self.start_web_server()
            

        except Exception as e:
            print(f"Error inesperado en run(): {e}")
            self.blink_led(10, 0.1)  # Indicar un error crítico parpadeando rápido




#-------------------------------------------------
# Wifi Manager
# Version: 1.0.0
# Desarrollado: Daniel Salgado
# Empresa: Ayresnet
# Fecha: 25/03/2024
#-------------------------------------------------

import network
import usocket as socket
import ujson as json
import os
import machine
import time

# Configurar el punto de acceso (AP)
# ap = network.WLAN(network.AP_IF)
# ap.active(True)
# ap.config(essid='WIFIMANAGER-AP') # , password='12345678', authmode=network.AUTH_WPA2_PSK)

class WifiManager:
    def __init__(self):
        # Contenido HTML con estilos CSS incluidos
        self.html_content = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Wifi setup</title>
                <style>

                    body {
                        background-color: #dadada;
                        font-family: Verdana, sans-serif;
                    }

                    .cabecera {
                        padding: 5px 0px;
                        border-radius: 5px;
                        background-color: rgb(23, 33, 119);
                        text-align: center;
                        color: #fff;
                        margin: 5px auto; /* Centra horizontalmente en la página */
                    }

                    .cabecera h1 {
                        font-size: 20px;
                        margin: 0px;
                    }
                    .cabecera h2 {
                        font-size: 16px;
                        margin: 0px;
                    }

                    .contenedor {
                            display: flex;
                            flex-direction: column;
                            align-items: center; /* Centra horizontalmente */
                            max-width: 600px; /* Ancho máximo del contenedor */
                            background-color: #fff;
                            padding: 20px 0px;
                            border-radius: 5px;
                            margin: 0 auto; /* Centra horizontalmente en la página */
                    }

                    /* Estilos generales */
                    .formulario {
                        display: flex;
                        flex-direction: column;
                        gap: 10px;
                    }

                    .entrada {
                        display: flex;
                        gap: 10px;
                        align-items: center;
                    }

                    .entrada label {
                        margin-bottom: 5px; /* Añade un espacio entre el label y el input */
                        text-align: center; /* Centra el texto del label */
                    }

                    .entrada input[type="text"],
                    .entrada input[type="password"] {
                        height: 20px;
                        flex: 2;
                        padding: 5px;
                        border: 1px solid #c7c7c7;
                        border-radius: 5px;
                    }
                    
                    .redes-wifi {
                        margin-bottom: 23px;
                    }
                    
                    .redes-wifi ul {
                        list-style-type: none;
                        padding: 0;
                        margin-top: 15px; /* Añade un margen superior de 5px */
                    }

                    .redes-wifi li {
                        cursor: pointer;
                        margin-bottom: 3px;
                    }
                
                    #toggle-password{
                        width: 20px;
                        padding: 0px;
                    }

                    .contenedor-footer {
                        padding: 5px 0px;
                        border-radius: 5px;
                        background-color: rgb(23, 33, 119);
                        text-align: center;
                        color: #fff;
                        margin: 5px auto; /* Centra horizontalmente en la página */
                    }
                    
                    .footer {
                        text-align: center;
                        font-size: 12px;
                    }

                    /* Estilo del botón "Guardar" */
                    #guardar-button {
                        background-color: blue;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin-top: 20px; /* Añadir margen superior */
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                    }

                    #guardar-button:hover {
                        background-color: rgb(116, 188, 212);
                        color: black;
                    }
                    .derechos {
                        font-size: 9px;
                    }
                </style>
            </head>

            <body>
                <div class="contenedor-cabecera">
                    <header class="cabecera">
                        <h1>WiFi Manager</h1>
                        <h2>Ayresnet</h2>
                    </header>
                </div>
                <div class="contenedor">
                <form method="POST" action="/save">
                    <div class="formulario">
                        <div class="redes-wifi">
                            <label for="wifi-list">Redes WiFi Disponibles:</label>
                            <ul id="wifi-list">
                                <!-- Aquí se agregarán las opciones de las redes WiFi -->
                            </ul>
                        </div>
                        <div class="entrada">
                            <label for="wifi-ssif">SSID:</label>
                            <input type="text" name="ssid" id="wifi-ssif">
                        </div>
                        <div class="entrada">
                            <label for="wifi-password">PASSWORD:</label>
                            <input type="password" name="password" id="wifi-password">
                            <button type="button" id="toggle-password">M</button>
                        </div>
                        <input type="submit" value="Guardar" id="guardar-button">
                    </div>
                </form>
                </div>
                
                <div class="contenedor-footer">
                    <footer class="footer">
                        <p>(c) 2024 - Daniel Salgado - v1.0.0</p>
                    </footer>
                </div>
                <p class="derechos">
                    El contenido de esta página web, incluyendo pero no limitado a texto, gráficos, logotipos, iconos, imágenes, clips de audio y video, así como el diseño y la disposición de los elementos en la página, están protegidos por las leyes de derechos de autor y otras leyes aplicables. Queda estrictamente prohibida cualquier reproducción, distribución, modificación o uso no autorizado de cualquier parte del contenido de este sitio web sin el previo consentimiento por escrito de Daniel Salgado y Ayresnet.
                    Se otorga permiso para copiar y usar fragmentos de código fuente y ejemplos proporcionados en esta página web únicamente con el propósito de configurar y utilizar el software de gestión de Wi-Fi desarrollado por Daniel Salgado y Ayresnet. Sin embargo, cualquier redistribución o reproducción completa o parcial del código fuente de este software está sujeta a los términos y condiciones establecidos en la licencia de código abierto adjunta.
                    El uso de marcas comerciales, nombres comerciales, marcas de servicio y logotipos que aparecen en este sitio web están sujetos a las leyes de propiedad intelectual y no pueden ser utilizados sin el previo consentimiento por escrito de sus propietarios respectivos.
                    Descargo de responsabilidad: Aunque nos esforzamos por proporcionar información precisa y actualizada, no ofrecemos garantías de ningún tipo, expresas o implícitas, sobre la integridad, precisión, confiabilidad, idoneidad o disponibilidad respecto al sitio web o la información, productos, servicios o gráficos relacionados contenidos en el sitio web para cualquier propósito. Cualquier confianza que usted deposite en dicha información es, por lo tanto, estrictamente bajo su propio riesgo.
                    Cualquier pregunta relacionada con los derechos de autor de este sitio web puede dirigirse via email.
                </p>
                
                <script>
                document.addEventListener('DOMContentLoaded', function() {
                    var redesWifi = document.getElementById('wifi-list');
                    redesWifi.addEventListener('click', function(event) {
                        if (event.target.tagName === 'LI') {
                            document.getElementById('wifi-ssif').value = event.target.textContent;
                        }
                    });
                });
                
                document.addEventListener('DOMContentLoaded', function() {
                    var redesWifi = document.getElementById('wifi-list');
                    redesWifi.addEventListener('click', function(event) {
                        if (event.target.tagName === 'LI') {
                            document.getElementById('wifi-ssif').value = event.target.textContent;
                        }
                    });

                    var togglePassword = document.getElementById('toggle-password');
                    var passwordInput = document.getElementById('wifi-password');
                    togglePassword.addEventListener('click', function() {
                        if (passwordInput.type === 'password') {
                            passwordInput.type = 'text';
                            togglePassword.textContent = 'O';
                        } else {
                            passwordInput.type = 'password';
                            togglePassword.textContent = 'M';
                        }
                    });
                });

                </script>
            </body>
            </html>
            """

        self.html_success = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Satisfactorio</title>
                <style>
                    body {
                        height: 100%;
                        margin: 15px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .mensaje {
                        margin-top: 50px;
                        border: 1px solid rgb(221, 221, 221);
                        border-left: 5px solid rgb(13, 196, 13);
                        padding: 10px;
                        text-align: center;
                        font-family: Verdana, sans-serif;
                    }
                </style>
            </head>
            <body>
                    <div class="mensaje">
                        <p>Se crearon las credenciales del WiFi de manera satisfactoria</p>
                    </div>
            </body>
            </html>
            """

        self.html_error = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Satisfactorio</title>
                <style>
                    body {
                        height: 100%;
                        margin: 15px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .mensaje {
                        margin-top: 50px;
                        border: 1px solid rgb(221, 221, 221);
                        border-left: 5px solid rgb(255, 0, 0);
                        padding: 10px;
                        text-align: center;
                        font-family: Verdana, sans-serif;
                    }
                </style>
            </head>
            <body>
                    <div class="mensaje">
                        <p>Se produjo un error al crear las credenciales WiFi</p>
                    </div>
            </body>
            </html>
            """
        self.s = socket.socket()
        self.s.bind(('0.0.0.0', 80))
        self.s.listen(5)
        self.configure_ap()
        
        
    # Función para configurar el punto de acceso (AP)
    def configure_ap(self):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid='WIFIMANAGER-AP')
        
    # Función para obtener las redes WiFi disponibles y sus señales
    def obtener_redes_wifi(self):
        redes_wifi = network.WLAN(network.STA_IF)
        redes_wifi.active(True)
        redes_encontradas = redes_wifi.scan()
        redes_ordenadas_por_señal = sorted(redes_encontradas, key=lambda x: x[3], reverse=True)[:5]  # Obtener las 5 redes con la señal más fuerte
        nombres_redes = [red[0].decode('utf-8') for red in redes_ordenadas_por_señal]
        return nombres_redes

    # Función para generar las opciones de las redes WiFi en el HTML
    def generar_opciones_redes_wifi(self):
        opciones = ""
        redes = self.obtener_redes_wifi()
        for red in redes:
            opciones += f"<li>{red}</li>"
        return opciones


    # Manejar las solicitudes HTTP
    def handle_request(self, client_socket):
    #     request = client_socket.recv(1024) #.decode('utf-8')
    #     
    #     request_parts = request.split(b" ")
    #     method = request_parts[0]
    #     url = request_parts[1]

        request = client_socket.recv(1024).decode('utf-8')
        
        if 'POST /save' in request:
            try:
    #             ssid_index = request.find('ssid=')
    #             password_index = request.find('password=')
    #             ssid_end_index = request.find('&', ssid_index)
    #             password_end_index = request.find('&', password_index)
    # 
    #             # Si no se encuentra el siguiente '&' después de 'password=', se toma el final de la cadena
    #             if password_end_index == -1:
    #                 password_end_index = len(request)
    # 
    #             ssid = request[ssid_index + len('ssid='):ssid_end_index]
    #             password = request[password_index + len('password='):password_end_index]
    # 

                # Obtener el cuerpo de la solicitud
                body_index = request.find('\r\n\r\n') + 4
                body = request[body_index:]

                # Analizar los datos del formulario
                form_data = {}
                for item in body.split('&'):
                    key, value = item.split('=')
                    form_data[key] = value

                # Obtener los valores de los campos 'ssid' y 'password'
                ssid = form_data.get('ssid', '')
                password = form_data.get('password', '')

                # Guardar las credenciales en un archivo JSON
                credentials = {'ssid': ssid, 'password': password}
                self.save_credentials(credentials)
                
                # Enviar la respuesta de éxito
                success_response = "HTTP/1.1 200 OK\r\n"
                success_response += "Content-Type: text/html\r\n"
                success_response += "Connection: close\r\n\r\n"
                success_response += self.html_success
                client_socket.send(success_response.encode())
                client_socket.close()
                
                # Reiniciar el ESP32 para que se conecte automáticamente a la red WiFi
                machine.reset()
                return
            except Exception as e:
                print("Error al guardar las credenciales:", e)
                # Enviar la respuesta de error
                error_response = "HTTP/1.1 200 OK\r\n"
                error_response += "Content-Type: text/html\r\n"
                error_response += "Connection: close\r\n\r\n"
                error_response += self.html_error
                client_socket.send(error_response.encode())
                client_socket.close()
                return
                
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/html\r\n"
        response += "Connection: close\r\n\r\n"
        response += self.html_content.replace("<!-- Aquí se agregarán las opciones de las redes WiFi -->", self.generar_opciones_redes_wifi())

        client_socket.send(response)
        client_socket.close()


    # Función para guardar las credenciales en un archivo JSON
    def save_credentials(self, credentials):
    #     raise Exception("Error al guardar las credenciales")
        with open('wifi.json', 'w') as f:
            json.dump(credentials, f)

    # Función para eliminar las credenciales
    def erase_credentials(self):
        try:
            os.remove('wifi.json')
            return True
        except FileNotFoundError:
            print("El archivo 'wifi.json' no existe.")
            return False
        except OSError as e:
            print(f"Error al eliminar el archivo: {e.strerror}")
            return False
            
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

    # Función para conectar al WiFi con las credenciales proporcionadas
    def connect_to_wifi(self, ssid, password):
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(ssid, password)
        print("Conectando a", ssid)
        
        start_time = time.time()
        while not sta_if.isconnected():
            if time.time() - start_time > 30:
                print("Tiempo de espera agotado. No se pudo conectar al WiFi.")
                break
            time.sleep(1)
            
        if sta_if.isconnected():
            print("Conexión exitosa a", ssid)
        else:
            print("No se pudo conectar al WiFi.")
            
            
    def run(self):
        # Verificar si existe el archivo wifi.json
        if 'wifi.json' in os.listdir():
            # Si existe, cargar las credenciales y conectarse a la red WiFi
            credentials = self.load_credentials()
            if credentials:
                self.connect_to_wifi(credentials['ssid'], credentials['password'])
            else:
                print("No se pudieron cargar las credenciales desde wifi.json.")
        else:
            print("El archivo wifi.json no existe. Configurando AP...")
            while True:
                client, addr = self.s.accept()
                self.handle_request(client)




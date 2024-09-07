"""* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                            *
*                         Developed by Javier Bolanos                        *
*                  https://github.com/javierbolanosllano                     *
*                                                                            *
*                      UAXSAT IV Project - 2024                              *
*                   https://github.com/UAXSat/UAXSat                         *
*                                                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"""

# receiver.py
import time
import psycopg2
from serial.tools import list_ports
from e220 import E220, MODE_NORMAL, AUX, M0, M1, VID_PID_LIST
import json
import logging

# Configuraci  n del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def find_serial_port(vendor_id, product_id):
    """Encuentra y devuelve el puerto serial para un dispositivo con el VID y PID dados"""
    ports = list_ports.comports()
    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

def insert_data_to_db(data):
    """Inserta los datos en la base de datos PostgreSQL"""
    try:
        connection = psycopg2.connect(
            database="sensor_data",
            user="cubesat",
            password="cubesat",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        # Consulta de inserci  n
        insert_query = """
        INSERT INTO sensor_readings (
            acelx, acely, acelz, girox, giroy, giroz, magx, magy, magz,
            uva, uvb, uvc, uv_temp, cpu_usage, ram_usage, total_ram,
            disk_usage, disk_usage_gb, total_disk_gb, temperature
        ) VALUES (
            %(acelx)s, %(acely)s, %(acelz)s, %(girox)s, %(giroy)s, %(giroz)s, %(magx)s, %(magy)s, %(magz)s,
            %(uva)s, %(uvb)s, %(uvc)s, %(uv_temp)s, %(cpu_usage)s, %(ram_usage)s, %(total_ram)s,
            %(disk_usage)s, %(disk_usage_gb)s, %(total_disk_gb)s, %(temperature)s
        )
        """

        # Ejecutar la consulta de insercion
        cursor.execute(insert_query, {
            'acelx': data.get('IMU', {}).get('ACELX'),
            'acely': data.get('IMU', {}).get('ACELY'),
            'acelz': data.get('IMU', {}).get('ACELZ'),
            'girox': data.get('IMU', {}).get('GIROX'),
            'giroy': data.get('IMU', {}).get('GIROY'),
            'giroz': data.get('IMU', {}).get('GIROZ'),
            'magx': data.get('IMU', {}).get('MAGX'),
            'magy': data.get('IMU', {}).get('MAGY'),
            'magz': data.get('IMU', {}).get('MAGZ'),
            'lat': data.get('GPS', {}).get('lat'),
            'lon': data.get('GPS', {}).get('lon'),
            'alt': data.get('GPS', {}).get('alt'),
            'headmot': data.get('GPS', {}).get('headmot'),
            'roll': data.get('GPS', {}).get('roll'),
            'pitch': data.get('GPS', {}).get('pitch'),
            'heading': data.get('GPS', {}).get('heading'),
            'NMEA': data.get('GPS', {}).get('NMEA'),              
            'uva': data.get('UV', {}).get('UVA'),
            'uvb': data.get('UV', {}).get('UVB'),
            'uvc': data.get('UV', {}).get('UVC'),
            'uv_temp': data.get('UV', {}).get('UV Temp'),
            'cpu_usage': data.get('System', {}).get('CPU Usage (%)'),
            'ram_usage': data.get('System', {}).get('RAM Usage (MB)'),
            'total_ram': data.get('System', {}).get('Total RAM (MB)'),
            'disk_usage': data.get('System', {}).get('Disk Usage (%)'),
            'disk_usage_gb': data.get('System', {}).get('Disk Usage (GB)'),
            'temperature': data.get('System', {}).get('Temperature (  C)')
        })

        # Confirmar los cambios en la base de datos
        connection.commit()

    except Exception as error:
        logger.error(f"Error al insertar en la base de datos: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def main():
    uart_port = None
    for vid, pid in VID_PID_LIST:
        uart_port = find_serial_port(vid, pid)
        if uart_port:
            break

    if uart_port is None:
        logger.error("Dispositivo no encontrado. Por favor, verifica tus conexiones.")
        exit(1)

    logger.info(f"Dispositivo encontrado en {uart_port}, inicializando el m  dulo E220...")

    lora_module = None
    try:
        lora_module = E220(m0_pin=M0, m1_pin=M1, aux_pin=AUX, uart_port=uart_port)
        lora_module.set_mode(MODE_NORMAL)

        logger.info("Escuchando mensajes entrantes...")

        buffer = ""  # Buffer para almacenar datos recibidos

        while True:
            received_message = lora_module.receive_data()
            if received_message:
                buffer += received_message  # A  adir datos recibidos al buffer

                # Buscar el marcador de inicio y fin en el buffer
                start_marker = "<<<"
                end_marker = ">>>"
                
                start_index = buffer.find(start_marker)
                end_index = buffer.find(end_marker)

                # Procesar solo si se encuentra un mensaje completo
                if start_index != -1 and end_index != -1 and end_index > start_index:
                    complete_message = buffer[start_index + len(start_marker):end_index]
                    logger.info(f"Mensaje JSON recibido: {complete_message}")

                    # Convertir el mensaje JSON a un diccionario
                    data_dict = json.loads(complete_message)

                    # Insertar los datos en la base de datos
                    insert_data_to_db(data_dict)

                    # Limpiar el buffer hasta el fin del marcador procesado
                    buffer = buffer[end_index + len(end_marker):]
                time.sleep(0.5)


    except KeyboardInterrupt:
        logger.info("Recepcion interrumpida por el usuario.")
    except Exception as e:
        logger.error(f"Se produjo un error: {e}")
    finally:
        if lora_module:
            lora_module.close()
        logger.info("Puerto serial cerrado.")
        time.sleep(1)  # Espera para dar tiempo a que los hilos secundarios se cierren

if __name__ == "__main__":
    main()
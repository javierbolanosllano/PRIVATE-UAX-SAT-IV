sudo -u postgres psql

\c sensor_data

-- Ver la estructura de la tabla 'sensor_readings'
\d sensor_readings

-- Consultar las primeras 10 filas de la tabla
SELECT * FROM sensor_readings LIMIT 10;

watch -n 5 psql -U cubesat -d sensor_data -c "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10;"






Paso 1: Iniciar sesión en PostgreSQL
Inicia sesión en PostgreSQL usando el usuario postgres:

sudo -i -u postgres
psql

Paso 2: Crear el usuario grafana
Una vez dentro del prompt de psql, ejecuta el siguiente comando para crear el usuario grafana con una contraseña. Sustituye yourpassword con la contraseña deseada para el usuario grafana:

CREATE USER grafana WITH PASSWORD 'yourpassword';

Paso 3: Crear la base de datos grafana
Si aún no has creado la base de datos grafana, puedes hacerlo con el siguiente comando:

CREATE DATABASE grafana;

Paso 4: Conceder privilegios al usuario grafana
Otorga al usuario grafana todos los privilegios sobre la base de datos grafana:

GRANT ALL PRIVILEGES ON DATABASE grafana TO grafana;

Paso 5: Salir de psql
Sal del prompt de psql:

\q




sudo -i -u postgres

psql

CREATE SCHEMA grafana_schema AUTHORIZATION grafana;
GRANT CREATE ON SCHEMA grafana_schema TO grafana;

CREATE TABLE grafana_schema.sensor_data (
    acelx FLOAT,
    acely FLOAT,
    acelz FLOAT,
    girox FLOAT,
    giroy FLOAT,
    giroz FLOAT,
    magx FLOAT,
    magy FLOAT,
    magz FLOAT,
    uva FLOAT,
    uvb FLOAT,
    uvc FLOAT,
    uv_temp FLOAT,
    cpu_usage FLOAT,
    ram_usage FLOAT,
    total_ram FLOAT,
    disk_usage FLOAT,
    disk_usage_gb FLOAT,
    total_disk_gb FLOAT,
    temperature FLOAT,
    lat FLOAT,
    lon FLOAT,
    alt FLOAT,
    headmot FLOAT,
    roll FLOAT,
    pitch FLOAT,
    heading FLOAT,
    nmea TEXT,
    lat_hp FLOAT,
    lon_hp FLOAT,
    alt_hp FLOAT,
    gps_error FLOAT,
    pressure FLOAT,
    bmp_temperature FLOAT,
    bmp_altitude FLOAT,
    timestamp TIMESTAMP
);
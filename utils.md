
# Borrar direccion IP
ssh-keygen -R 192.168.1.70



# monitoreo de la tabla de postgree sql
watch -n 10 "psql -U cubesat -d sensor_data -c 'SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 10;'"

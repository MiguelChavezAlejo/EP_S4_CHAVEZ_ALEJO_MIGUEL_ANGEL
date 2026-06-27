# ============================================================
# P4 — Docker Desktop: MongoDB local en contenedor
# ============================================================
# Antes de ejecutar este archivo, primero levanta MongoDB en Docker.
#
# Ejecutar en PowerShell:
#
# docker pull mongo:7.0
#
# docker run -d --name yape-mongo-local -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=yape2026 mongo:7.0
#
# docker ps
#
# Si falta pymongo:
# pip install pymongo
# ============================================================

from pymongo import MongoClient

# Conexión al MongoDB local levantado en Docker
client_docker = MongoClient(
    "mongodb://admin:yape2026@localhost:27017/",
    authSource="admin"
)

db_local = client_docker["yape_local"]
col_local = db_local["comerciantes_test"]

# Limpiar solo el documento de prueba para evitar duplicados
col_local.delete_many({"nombre_comercio": "Bodega Test Docker"})

# Insertar documento de prueba
col_local.insert_one({
    "nombre_comercio": "Bodega Test Docker",
    "tipo": "bodega",
    "distrito": "Lima",
    "monto_mensual_soles": 1500.00,
    "yape_activo": True,
    "entorno": "docker_local"
})

# Verificar inserción
doc = col_local.find_one({"nombre_comercio": "Bodega Test Docker"})

print("✅ Documento guardado en MongoDB Docker:")
print(f"   Nombre:   {doc['nombre_comercio']}")
print(f"   Entorno:  {doc['entorno']}")
print(f"   ID:       {doc['_id']}")

print(f"\nTotal documentos en Docker: {col_local.count_documents({})}")

# ============================================================
# P4.3 — Diferencia entre Docker y Atlas
# ============================================================
#
# a) ¿Cuándo usarías MongoDB en Docker en lugar de MongoDB Atlas?
#
# Usaría MongoDB en Docker para desarrollo local, pruebas rápidas
# y validación de código sin afectar una base en la nube. También
# sirve cuando el equipo necesita un entorno controlado en su propia
# laptop sin instalar MongoDB directamente.
#
# b) ¿Qué ventaja tiene Atlas M0 sobre Docker para el contexto universitario?
#
# Atlas M0 permite tener MongoDB gratis en la nube, accesible desde
# cualquier equipo y con una interfaz web para que el docente pueda
# verificar los documentos insertados. No depende de que mi laptop
# esté encendida o que Docker esté corriendo.
#
# c) ¿Qué sucede con los datos si ejecutas docker stop y docker rm?
#
# Con docker stop el contenedor se detiene, pero los datos siguen
# mientras el contenedor exista. Con docker rm se elimina el contenedor
# y, si no configuré un volumen persistente, los datos se pierden.
# En Atlas los datos permanecen en la nube aunque elimine el contenedor local.
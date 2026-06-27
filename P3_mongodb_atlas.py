# ============================================================
# P3 — MongoDB Atlas: Comerciantes Yape
# ============================================================
# Si lo ejecutas en Google Colab:
# !pip install pymongo dnspython certifi -q
#
# Si lo ejecutas en VS Code:
# pip install pymongo dnspython certifi

from pymongo import MongoClient
import certifi

# IMPORTANTE:
# Reemplaza este texto por tu connection string real de MongoDB Atlas.
# No subas tu contraseña real a GitHub. Para entregar, puedes volver a dejarlo como placeholder.
CONNECTION_STRING = "mongodb+srv://chavezmigjo4_db_user:z25FNSmoqJFXCzLd@yape-big-data.owax1xo.mongodb.net/?appName=yape-big-data"

client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

db = client["yape_db"]
comerciantes = db["comerciantes"]

print("✅ Conectado a MongoDB Atlas")
print(f"   DB: {db.name} | Colección: {comerciantes.name}")

# Limpiar la colección para evitar duplicados si ejecutas varias veces
comerciantes.delete_many({})

# ============================================================
# PASO 2 — Insertar 5 comerciantes con estructura flexible
# ============================================================

lista_comerciantes = [
    {
        "ruc": "10456789012",
        "nombre_comercio": "Bodega La Esquina de Don Mario",
        "tipo": "bodega",
        "propietario": "Mario Quispe Condori",
        "distrito": "San Juan de Lurigancho",
        "departamento": "Lima",
        "calificacion": 4.2,
        "yape_activo": True,
        "monto_mensual_soles": 4500.00,
        "categorias": ["abarrotes", "bebidas", "snacks"],
        "horario": {"apertura": "06:00", "cierre": "22:00"},
        "acepta_delivery": False
    },
    {
        "ruc": "20512345678",
        "nombre_comercio": "Cevichería El Muelle SAC",
        "tipo": "restaurante",
        "representante_legal": "Ana Flores Rojas",
        "distrito": "Miraflores",
        "departamento": "Lima",
        "calificacion": 4.8,
        "yape_activo": True,
        "monto_mensual_soles": 28000.00,
        "carta": [
            {"plato": "Ceviche clásico", "precio": 28.00},
            {"plato": "Leche de tigre",  "precio": 18.00},
            {"plato": "Tiradito",        "precio": 32.00}
        ],
        "capacidad_mesas": 45,
        "num_empleados": 12,
        "horario": {"apertura": "12:00", "cierre": "17:00"},
        "acepta_delivery": True,
        "plataformas_delivery": ["Rappi", "PedidosYa"]
    },
    {
        "ruc": "10789012345",
        "nombre_comercio": "Farmacia San Pablo Express",
        "tipo": "farmacia",
        "propietario": "Carlos Mendoza Ríos",
        "distrito": "Los Olivos",
        "departamento": "Lima",
        "calificacion": 4.5,
        "yape_activo": True,
        "monto_mensual_soles": 12000.00,
        "productos_destacados": ["paracetamol", "ibuprofeno", "vitaminas"],
        "horario": {"apertura": "07:00", "cierre": "23:00"},
        "venta_con_receta": True,
        "codigo_digemid": "F-2023-00456",
        "acepta_delivery": True
    },
    {
        "ruc": "10234567891",
        "nombre_comercio": "Taxi Express — Luis Tapia",
        "tipo": "taxi",
        "propietario": "Luis Tapia Salcedo",
        "distrito": "Callao",
        "departamento": "Lima",
        "calificacion": 4.0,
        "yape_activo": True,
        "monto_mensual_soles": 3200.00,
        "vehiculo": {
            "placa": "ABC-123",
            "modelo": "Toyota Yaris 2022",
            "capacidad": 4
        },
        "zonas_cobertura": ["Callao", "Bellavista", "La Perla", "Miraflores"],
        "acepta_delivery": False
    },
    {
        "ruc": "20987654321",
        "nombre_comercio": "Distribuidora Norte SAC",
        "tipo": "empresa",
        "representante_legal": "Patricia Luna Torres",
        "distrito": "Independencia",
        "departamento": "Lima",
        "calificacion": 3.9,
        "yape_activo": True,
        "monto_mensual_soles": 85000.00,
        "num_empleados": 45,
        "sectores": ["abarrotes", "limpieza", "bebidas"],
        "clientes_mayoristas": 230,
        "horario": {"apertura": "08:00", "cierre": "18:00"},
        "acepta_delivery": True,
        "zonas_despacho": ["Lima Norte", "Lima Centro"]
    }
]

resultado = comerciantes.insert_many(lista_comerciantes)

print(f"\n✅ {len(resultado.inserted_ids)} comerciantes insertados en Atlas")
for i, id_ in enumerate(resultado.inserted_ids):
    print(f"   {lista_comerciantes[i]['tipo'].upper()}: {id_}")

# ============================================================
# PASO 3 — Consultas con filtros
# ============================================================

print("\n" + "=" * 55)
print("CONSULTA 1: Comerciantes premium (calificación > 4.3 y activos)")

premium = list(comerciantes.find(
    {"calificacion": {"$gt": 4.3}, "yape_activo": True},
    {"nombre_comercio": 1, "tipo": 1, "calificacion": 1, "_id": 0}
).sort("calificacion", -1))

for c in premium:
    print(f"  ★ {c['nombre_comercio']} ({c['tipo']}) — {c['calificacion']}")

print("\nCONSULTA 2: Comercios con delivery en Lima que facturan > S/10,000/mes")

alto_valor = list(comerciantes.find(
    {
        "acepta_delivery": True,
        "departamento": "Lima",
        "monto_mensual_soles": {"$gt": 10000}
    },
    {"nombre_comercio": 1, "monto_mensual_soles": 1, "distrito": 1, "_id": 0}
))

for c in alto_valor:
    print(f"  → {c['nombre_comercio']} ({c['distrito']}): S/{c['monto_mensual_soles']:,.0f}/mes")

print("\nCONSULTA 3: Bodegas O farmacias (operador $in)")

bodegas_farmacias = list(comerciantes.find(
    {"tipo": {"$in": ["bodega", "farmacia"]}},
    {"nombre_comercio": 1, "tipo": 1, "_id": 0}
))

for c in bodegas_farmacias:
    print(f"  → [{c['tipo']}] {c['nombre_comercio']}")

# ============================================================
# PASO 4 — Aggregation Pipeline
# ============================================================

pipeline_reporte = [
    # Paso 1: Solo comerciantes activos en Lima
    {"$match": {"yape_activo": True, "departamento": "Lima"}},

    # Paso 2: Agrupar por tipo de comercio
    {"$group": {
        "_id": "$tipo",
        "total_comercios": {"$sum": 1},
        "facturacion_total": {"$sum": "$monto_mensual_soles"},
        "calificacion_prom": {"$avg": "$calificacion"},
        "con_delivery": {"$sum": {"$cond": ["$acepta_delivery", 1, 0]}}
    }},

    # Paso 3: Ordenar por facturación total descendente
    {"$sort": {"facturacion_total": -1}},

    # Paso 4: Formatear la salida
    {"$project": {
        "tipo_comercio": "$_id",
        "total_comercios": 1,
        "facturacion_total": 1,
        "calificacion_prom": {"$round": ["$calificacion_prom", 1]},
        "con_delivery": 1,
        "_id": 0
    }}
]

print("\n📊 REPORTE COMERCIAL YAPE — FACTURACIÓN POR TIPO:")
print(f"{'TIPO':<20} {'COMERCIOS':>9} {'FACTURACIÓN/MES':>16} {'RATING':>7} {'C/DELIVERY':>11}")
print("-" * 67)

for r in comerciantes.aggregate(pipeline_reporte):
    print(
        f"{r['tipo_comercio']:<20} "
        f"{r['total_comercios']:>9} "
        f"S/{r['facturacion_total']:>13,.0f} "
        f"{r['calificacion_prom']:>7} "
        f"{r['con_delivery']:>11}"
    )
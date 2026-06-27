# Databricks notebook source
# ============================================================
# P2 — Pipeline de Transacciones Yape en Databricks
# Arquitectura Medallion: Bronze → Silver → Gold
# ============================================================

# COMMAND ----------

# ============================================================
# CELDA 1: Dataset sintético — 2,000 transacciones Yape
# ============================================================
import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import *

np.random.seed(42)

n = 2000
distritos = ["Miraflores", "San Isidro", "SJL", "Comas", "Villa El Salvador",
             "Los Olivos", "Surco", "Ate", "Callao", "Independencia"]
tipos     = ["persona_a_persona", "persona_a_comercio", "retiro_bcp", "recarga"]
estados   = ["completada", "completada", "completada", "rechazada", "pendiente"]

data = {
    "id_transaccion": [f"YP{i:07d}" for i in range(1, n+1)],
    "fecha":          pd.date_range("2025-01-01", periods=n, freq="1h").strftime("%Y-%m-%d").tolist(),
    "hora":           [f"{h:02d}:{m:02d}" for h, m in zip(np.random.randint(0,24,n), np.random.randint(0,60,n))],
    "monto_soles":    np.round(np.random.exponential(45, n), 2).tolist(),
    "tipo":           np.random.choice(tipos, n).tolist(),
    "distrito_origen":np.random.choice(distritos, n).tolist(),
    "estado":         np.random.choice(estados, n, p=[0.75, 0.1, 0.05, 0.07, 0.03]).tolist(),
    "id_usuario":     [f"USR{np.random.randint(1000,9999)}" for _ in range(n)],
    "es_comercio":    np.random.choice([True, False], n, p=[0.4, 0.6]).tolist()
}

df_pandas = pd.DataFrame(data)
df_bronze = spark.createDataFrame(df_pandas)

df_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("yape_bronze_transacciones")

print(f"✅ Bronze layer: {df_bronze.count()} transacciones guardadas en tabla yape_bronze_transacciones")
df_bronze.show(5)
# COMMAND ----------

# ============================================================
# CELDA 2: Silver — limpiar y transformar
# ============================================================
# ============================================================
# CELDA 2: Silver — limpiar y transformar
# Adaptado: lee desde tabla Bronze y guarda como tabla Silver
# ============================================================

df_bronze = spark.table("yape_bronze_transacciones")

df_silver = (
    df_bronze
    .filter(F.col("estado") == "completada")
    .filter(F.col("monto_soles") > 0)
    .withColumn(
        "categoria_monto",
        F.when(F.col("monto_soles") < 20, "micro")
         .when(F.col("monto_soles") < 100, "medio")
         .otherwise("alto")
    )
    .withColumn(
        "es_hora_pico",
        F.when(F.col("hora").between("12:00", "14:00"), True)
         .when(F.col("hora").between("18:00", "22:00"), True)
         .otherwise(False)
    )
    .withColumn(
        "comision_yape",
        F.when(
            F.col("tipo") == "persona_a_comercio",
            F.round(F.col("monto_soles") * 0.015, 2)
        ).otherwise(0.0)
    )
)

df_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("yape_silver_transacciones_limpias")

print(f"✅ Silver layer: {df_silver.count()} transacciones válidas")
print(f"   Eliminadas: {df_bronze.count() - df_silver.count()} (rechazadas/pendientes/monto cero)")
df_silver.groupBy("categoria_monto").count().show()

# COMMAND ----------

# ============================================================
# CELDA 3: Gold — agregaciones para el dashboard ejecutivo
# ============================================================
# ============================================================
# CELDA 3: Gold — agregaciones para el dashboard ejecutivo
# Adaptado: lee desde tabla Silver y guarda tablas Gold
# ============================================================

df_silver = spark.table("yape_silver_transacciones_limpias")
df_silver.createOrReplaceTempView("transacciones")

gold_distritos = spark.sql("""
    SELECT 
        distrito_origen,
        COUNT(*)                          AS total_transacciones,
        ROUND(SUM(monto_soles), 2)        AS volumen_total_soles,
        ROUND(AVG(monto_soles), 2)        AS ticket_promedio,
        SUM(CASE WHEN es_comercio THEN 1 ELSE 0 END) AS transacciones_comercio
    FROM transacciones
    GROUP BY distrito_origen
    ORDER BY total_transacciones DESC
    LIMIT 5
""")

gold_comisiones = spark.sql("""
    SELECT
        SUBSTRING(hora, 1, 2)             AS hora_dia,
        COUNT(*)                          AS num_transacciones,
        ROUND(SUM(comision_yape), 2)      AS ingresos_yape_soles
    FROM transacciones
    WHERE comision_yape > 0
    GROUP BY SUBSTRING(hora, 1, 2)
    ORDER BY ingresos_yape_soles DESC
""")

gold_distritos.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("yape_gold_top_distritos")

gold_comisiones.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("yape_gold_ingresos_por_hora")

print("📊 TOP 5 DISTRITOS POR VOLUMEN YAPE:")
gold_distritos.show()

print("💰 INGRESOS YAPE POR HORA (comisión comercios):")
gold_comisiones.show(5)
# COMMAND ----------

# ============================================================
# CELDA 4: Visualización — gráfico de barras con matplotlib
# ============================================================
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

gold_distritos = spark.read.parquet("/FileStore/yape/gold/top_distritos").toPandas()
gold_comisiones = spark.read.parquet("/FileStore/yape/gold/ingresos_por_hora").toPandas()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Dashboard Ejecutivo YAPE — Análisis de Transacciones", fontsize=14, fontweight='bold')

# Gráfico 1: Top 5 distritos
axes[0].barh(
    gold_distritos["distrito_origen"],
    gold_distritos["volumen_total_soles"],
    color=["#c41230", "#e63950", "#f47a8a", "#f9b4bc", "#fde8ea"]
)
axes[0].set_xlabel("Volumen total (S/)")
axes[0].set_title("Top 5 Distritos — Volumen de Pagos")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"S/{x:,.0f}"))

# Gráfico 2: Ingresos Yape por hora
gold_comisiones_sorted = gold_comisiones.sort_values("hora_dia")
axes[1].plot(
    gold_comisiones_sorted["hora_dia"],
    gold_comisiones_sorted["ingresos_yape_soles"],
    marker='o',
    color='#c41230',
    linewidth=2
)
axes[1].fill_between(
    gold_comisiones_sorted["hora_dia"],
    gold_comisiones_sorted["ingresos_yape_soles"],
    alpha=0.15,
    color='#c41230'
)
axes[1].set_xlabel("Hora del día")
axes[1].set_ylabel("Comisión recaudada (S/)")
axes[1].set_title("Ingresos Yape por Hora")
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig("/dbfs/FileStore/yape/gold/dashboard_yape.png", dpi=150, bbox_inches='tight')
plt.show()

print("✅ Dashboard guardado en /FileStore/yape/gold/dashboard_yape.png")
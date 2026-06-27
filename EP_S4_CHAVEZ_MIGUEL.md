# Evaluación Parcial Big Data — Yape

**Estudiante:** Miguel Ángel Chávez Alejo  
**Código:** COMPLETAR_CODIGO  
**Curso:** Big Data DD283  
**Docente:** Mg. Rubén Quispe Llacctarimay  

---

## Enlace del video

Pendiente: https://______________________________

---

## Descripción de la solución

En esta evaluación se desarrolló una solución Big Data para el caso Yape, considerando arquitectura, procesamiento distribuido, base de datos NoSQL y contenedores.

### Parte A — Arquitectura

Se diseñó una arquitectura Big Data para Yape considerando:

- Core de pagos con CockroachDB.
- Sesiones activas con Redis.
- Perfil de comerciantes con MongoDB.
- Historial analítico con Databricks y Delta Lake.
- Detección de fraude con Neo4j.
- Dashboard ejecutivo con Power BI.

### Parte B — Databricks

Se implementó un pipeline usando arquitectura Medallion:

- **Bronze:** carga de transacciones originales.
- **Silver:** limpieza, validación y enriquecimiento de datos.
- **Gold:** generación de métricas para dashboard ejecutivo.

El notebook genera métricas de negocio como top distritos por volumen y comisiones por hora.

### Parte C — MongoDB Atlas

Se creó una base de datos documental para comerciantes Yape.  
Se insertaron 5 comerciantes con estructuras flexibles:

- Bodega
- Restaurante
- Farmacia
- Taxi
- Empresa

También se ejecutaron consultas con filtros y un aggregation pipeline para obtener facturación por tipo de comercio.

### Parte D — Docker Desktop

Se levantó MongoDB local en un contenedor Docker usando la imagen oficial `mongo:7.0`.  
Luego se conectó Python al contenedor local y se insertó un documento de prueba.

---

## Uso de IA

Usé ChatGPT como asistente para ordenar la solución, completar código base, validar conceptos y mejorar la redacción.  
La ejecución, adaptación, revisión de outputs y explicación final fueron realizadas por mí.

---

## Evidencias

Las capturas se guardan en la carpeta `screenshots/`:

- `databricks_celda1.png`
- `databricks_celda2.png`
- `databricks_celda3.png`
- `databricks_dashboard.png`
- `atlas_collections.png`
- `atlas_pipeline_output.png`
- `docker_desktop.png`
- `docker_python_output.png`
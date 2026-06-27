# P1 — Arquitectura Big Data para Yape

**Estudiante:** Miguel Ángel Chávez Alejo  
**Código:** COMPLETAR_CODIGO  
**Curso:** Big Data DD283  
**Uso de IA:** Usé ChatGPT como asistente para ordenar la solución, validar conceptos y estructurar las respuestas. La adaptación, revisión y explicación final fueron realizadas por mí.

---

## 1.1 Tabla de arquitectura

| Componente del sistema | Tecnología elegida | Tipo BD/Herramienta | Por qué esta tecnología para Yape |
|---|---|---|---|
| Core de pagos (3.2M transacciones/día, no puede perder dinero) | CockroachDB | NewSQL / Base de datos distribuida ACID | El core de pagos necesita máxima consistencia porque maneja saldos, débitos y créditos. CockroachDB permite escalar horizontalmente sin perder las propiedades ACID necesarias para pagos. |
| Sesiones de login activo (15M usuarios, expira en 30 min) | Redis Cluster | Base de datos Key-Value en memoria | Las sesiones son datos temporales que deben consultarse muy rápido y expirar automáticamente. Redis permite usar TTL, alta velocidad y manejo de millones de sesiones activas. |
| Perfil del comerciante (bodega, restaurante, taxi — atributos distintos) | MongoDB Atlas | Base de datos NoSQL documental | Cada tipo de comercio puede tener campos diferentes, como carta, vehículo, horario o zonas de cobertura. MongoDB permite guardar documentos flexibles sin crear muchas columnas vacías como pasaría en SQL. |
| Historial de transacciones para análisis (18 TB/año) | Databricks + Delta Lake | Data Lakehouse / Procesamiento distribuido | El historial anual es muy grande para analizarlo de forma tradicional. Databricks con Spark permite procesar grandes volúmenes y Delta Lake permite organizar los datos en capas Bronze, Silver y Gold. |
| Red de detección de fraude (ciclo A→B→C→A en < 5 min) | Neo4j | Base de datos de grafos | El fraude puede detectarse por relaciones entre usuarios, comercios y cuentas. Neo4j permite encontrar ciclos y conexiones sospechosas de forma más directa que con múltiples joins en SQL. |
| Dashboard ejecutivo (top 10 distritos, actualización diaria) | Power BI conectado a tablas Gold de Databricks | Herramienta BI / Dashboard | Los ejecutivos necesitan información resumida, visual y fácil de entender. Power BI puede consumir las tablas Gold procesadas y mostrar KPIs, rankings y tendencias actualizadas diariamente. |

---

## 1.2 Teorema CAP

| Componente | Combinación CAP | Propiedad sacrificada | ¿Por qué ese sacrificio es correcto o incorrecto para este caso? |
|---|---|---|---|
| Core de pagos (débito/crédito de saldos) | CP | Disponibilidad | En pagos es preferible detener o rechazar temporalmente una operación antes que aceptar una transacción inconsistente. Si hay una partición de red, no se debe permitir que dos nodos actualicen saldos diferentes. |
| Historial "mis últimas 50 transacciones" | AP | Consistencia fuerte inmediata | Para el historial es aceptable que una transacción aparezca con unos segundos de retraso. El usuario puede seguir usando la aplicación aunque la vista del historial todavía se esté actualizando. |

---

## 1.3 NewSQL

### a) ¿Qué limitación de Oracle resuelve CockroachDB al escalar de 15M a 50M usuarios?

CockroachDB resuelve principalmente la limitación de escalamiento horizontal.  
En un escenario de crecimiento de 15M a 50M usuarios, el sistema necesita distribuir carga, datos y transacciones entre varios nodos. Oracle puede ser muy potente, pero normalmente depende más del escalamiento vertical o de configuraciones más complejas para distribuir la carga. CockroachDB está diseñado para trabajar de forma distribuida desde su arquitectura.

---

### b) ¿Por qué MongoDB NO puede reemplazar a Oracle para el procesamiento de pagos aunque también escala horizontalmente?

MongoDB es adecuado para datos flexibles, como perfiles de comerciantes o catálogos con estructuras distintas.  
Sin embargo, el procesamiento de pagos necesita consistencia fuerte, control transaccional, integridad y operaciones ACID estrictas. En un pago no se puede permitir que el débito se registre y el crédito falle, o que el saldo quede inconsistente. Por eso MongoDB no es la mejor opción para reemplazar el core transaccional de pagos.

---

### c) ¿Qué mecanismo técnico usa CockroachDB para mantener ACID en múltiples nodos distribuidos?

**Raft consensus.**
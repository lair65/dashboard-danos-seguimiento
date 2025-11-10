# Documentación Técnica: Sistema de Control de Seguimiento de Daños

## Resumen Ejecutivo

El **Dashboard de Control de Seguimiento de Daños** es una aplicación web desarrollada con Streamlit que permite al equipo de ejecutivos de AIR (compañía aseguradora) monitorear y gestionar el progreso de reclamos de seguros a través de múltiples etapas de procesamiento. El sistema proporciona seguimiento automatizado de plazos, métricas de desempeño por ejecutivo, y visualización codificada por colores del estado de cumplimiento.

### Propósito Principal
Facilitar el control y seguimiento de las acciones pendientes de los ejecutivos en los diferentes procesos de atención a siniestros, asegurando el cumplimiento de plazos establecidos y mejorando la eficiencia operativa.

---

## 1. Arquitectura del Sistema

### 1.1 Estructura de Archivos

```
danos_seguimientos/
├── dashboard.py              # Aplicación principal (742 líneas)
├── reporte_danos.xlsx        # Fuente de datos
├── requirements.txt          # Dependencias Python
├── README.md                 # Documentación básica
├── airLogo.png              # Logo corporativo
├── backup/                  # Versiones anteriores
└── .devcontainer/           # Configuración de desarrollo
```

### 1.2 Stack Tecnológico

- **Streamlit**: Framework de aplicación web
- **Pandas**: Manipulación y análisis de datos
- **NumPy**: Operaciones numéricas
- **Plotly**: Visualizaciones interactivas
- **OpenPyXL**: Lectura/escritura de archivos Excel
- **Python 3.11**: Lenguaje de programación

---

## 2. Flujo de Trabajo del Sistema

### 2.1 Proceso General

```
┌─────────────────────┐
│  Carga de Datos     │
│  (reporte_danos.xlsx)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Filtrado           │
│  - Cancelaciones    │
│  - Limpieza de datos│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Aplicar Filtros    │
│  - Período/Fecha    │
│  - Ejecutivo        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Procesamiento      │
│  - 7 procesos       │
│  - Cálculo estados  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Visualización      │
│  - Resumen Global   │
│  - Detalle Procesos │
└─────────────────────┘
```

### 2.2 Punto de Entrada

**Archivo**: `dashboard.py`
**Función principal**: `main()` (línea 422)

---

## 3. Gestión de Datos

### 3.1 Carga de Datos (`load_data()`)

**Ubicación**: dashboard.py:17-36

**Proceso**:
1. Lee el archivo Excel `reporte_danos.xlsx`
2. Filtra registros cancelados
3. Limpia nombres de ejecutivos
4. Convierte columnas de fecha

### 3.2 Campo de Cancelaciones

**IMPORTANTE**: El sistema filtra automáticamente los registros cancelados.

**Lógica de Filtrado**:
```python
if 'Cancelaciones' in df.columns:
    df = df[~df['Cancelaciones'].str.upper().str.strip().eq('SI')]
```

**Comportamiento**:
- Si el campo `Cancelaciones` contiene "SI" (sin importar mayúsculas/minúsculas o espacios)
- El registro es **excluido** de todos los análisis y reportes
- Solo se procesan registros donde `Cancelaciones` es diferente de "SI" o está vacío

### 3.3 Estructura de Datos del Excel

#### Campos Principales:

| Campo | Descripción | Tipo | Uso |
|-------|-------------|------|-----|
| `ID` | Identificador único del siniestro | Entero | Identificación de registros |
| `Cliente` | Nombre del cliente asegurado | Texto | Búsqueda, agrupación |
| `Pólizas` | Números de pólizas asociadas | Texto | Búsqueda, referencia |
| `Ejecutivo` | Nombre del ejecutivo responsable | Texto | Filtrado, métricas |
| `PrimaNeta` | Monto de la prima neta | Decimal | Agregaciones monetarias |
| `Moneda` | Tipo de moneda (Dólares/Nacional) | Texto | Separación de montos |
| `SRamoNombre` | Ramo de seguro | Texto | Categorización |
| `Cancelaciones` | Indicador de cancelación | Texto | Filtrado crítico |

#### Campos de Fecha Base (7 procesos):

1. `FEnvío Cap` - Fecha de envío de capital
2. `Carta cobertura` - Fecha de carta de cobertura
3. `30 Días Pres. Cliente` - Fecha de presentación al cliente (30 días)
4. `69 Días Sol. Aseguradora` - Fecha de solicitud a aseguradora (69 días)
5. `74 Días Recepcion de Info. Del cliente` - Fecha de recepción de información del cliente (74 días)
6. `89 Días Env. Info, al cliente` - Fecha de envío de información al cliente (89 días)
7. `100 Días Solicitud Siniestralidad` - Fecha de solicitud de siniestralidad (100 días)

#### Campos de Acción del Ejecutivo:

Para cada proceso existe un campo correspondiente que registra la fecha en que el ejecutivo completó la acción:

1. `Ejecutivo Fcap`
2. `Ejecutivo 5 días`
3. `Ejecutivo 30 días`
4. `Ejecutivo 69 días`
5. `Ejecutivo 74 días `
6. `Ejecutivo 89 días`
7. `Ejecutivo 100 días`

---

## 4. Los 7 Procesos de Seguimiento

El sistema monitorea 7 etapas del ciclo de vida de un siniestro. Cada proceso tiene:
- Una **fecha base** (deadline esperado)
- Una **fecha de ejecución** (cuando el ejecutivo completó la acción)

### Mapeo de Procesos:

| # | Fecha Base | Campo Ejecutivo | Descripción |
|---|-----------|----------------|-------------|
| 1 | `FEnvío Cap` | `Ejecutivo Fcap` | Envío inicial de documentación de capital |
| 2 | `Carta cobertura` | `Ejecutivo 5 días` | Emisión de carta de cobertura (5 días) |
| 3 | `30 Días Pres. Cliente` | `Ejecutivo 30 días` | Presentación al cliente (30 días) |
| 4 | `69 Días Sol. Aseguradora` | `Ejecutivo 69 días` | Solicitud a la aseguradora (69 días) |
| 5 | `74 Días Recepcion de Info. Del cliente` | `Ejecutivo 74 días ` | Recepción de información del cliente (74 días) |
| 6 | `89 Días Env. Info, al cliente` | `Ejecutivo 89 días` | Envío de información al cliente (89 días) |
| 7 | `100 Días Solicitud Siniestralidad` | `Ejecutivo 100 días` | Solicitud de siniestralidad (100 días) |

---

## 5. Cálculo de Estados y Fechas

### 5.1 Algoritmo Principal de Estado

**Ubicación**: dashboard.py:322-415 (`get_all_records_for_process()`)

Para cada registro en cada proceso, el sistema calcula:

#### A. Estado de Tiempo (`Estado Tiempo`)

**Propósito**: Indica si la acción se completó a tiempo o con retraso.

```
SI existe fecha_ejecutivo Y existe fecha_base:
    SI fecha_ejecutivo <= fecha_base:
        Estado = "En Tiempo" (Verde)
    SINO:
        Estado = "Retrasado" (Rojo)

SI existe fecha_ejecutivo PERO NO existe fecha_base:
    Estado = "Sin Fecha Base" (Amarillo)

SI NO existe fecha_ejecutivo:
    Estado = "Pendiente" (Amarillo)
```

**Código**:
```python
if pd.notna(exec_date) and pd.notna(base_date):
    if exec_date.date() <= base_date.date():
        timing_status = "En Tiempo"
        timing_color = "green"
    else:
        timing_status = "Retrasado"
        timing_color = "red"
elif pd.notna(exec_date) and pd.isna(base_date):
    timing_status = "Sin Fecha Base"
    timing_color = "yellow"
else:
    timing_status = "Pendiente"
    timing_color = "yellow"
```

#### B. Prioridad de Color (`Color Priority`)

**Propósito**: Indica la urgencia de la acción pendiente.

```
SI existe fecha_ejecutivo:
    Status = "Completado"
    Color = VERDE

SINO:
    SI NO existe fecha_base:
        Status = "Sin fecha base"
        Color = ROJO
    SINO:
        dias_hasta_deadline = fecha_base - hoy

        SI dias_hasta_deadline > 1:
            Status = "[N] días restantes"
            Color = AMARILLO
        SINO:
            SI dias_hasta_deadline <= 0:
                Status = "[N] días vencido"
            SINO:
                Status = "Vence hoy" o "[N] día(s) restante(s)"
            Color = ROJO
```

**Código**:
```python
if pd.notna(exec_date):
    status = "Completado"
    color_priority = "green"
    formatted_exec_date = exec_date.strftime('%d/%m/%Y')
else:
    if pd.isna(base_date):
        status = "Sin fecha base"
        color_priority = "red"
        formatted_exec_date = "Sin acción"
    else:
        days_until_deadline = (base_date.date() - today).days

        if days_until_deadline > 1:
            status = f"{days_until_deadline} días restantes"
            color_priority = "yellow"
        else:
            if days_until_deadline <= 0:
                status = f"{abs(days_until_deadline)} días vencido"
            else:
                status = "Vence hoy" if days_until_deadline == 0 else f"{days_until_deadline} día(s) restante(s)"
            color_priority = "red"

        formatted_exec_date = "Pendiente"
```

### 5.2 Sistema de Colores

| Color | Significado | Condiciones | Implicación |
|-------|------------|-------------|-------------|
| 🟢 **Verde** | Completado | Fecha ejecutivo existe | Acción finalizada |
| 🟡 **Amarillo** | Pendiente con tiempo | >1 día hasta deadline | Acción pendiente pero no urgente |
| 🔴 **Rojo** | Vencido o urgente | ≤1 día hasta deadline o sin fecha base | Acción vencida, vence hoy, o falta información |

### 5.3 Consideraciones Temporales

**IMPORTANTE**: El sistema usa solo la fecha (sin hora) para comparaciones:

```python
today = datetime.now().date()  # Solo fecha, ignora hora
days_until_deadline = (base_date.date() - today).days
```

**Umbral Crítico**:
- Casos con **más de 1 día restante** = Amarillo (pendiente)
- Casos con **1 día o menos restante** = Rojo (urgente)
- Esta distinción permite priorizar acciones inmediatas

---

## 6. Filtros y Períodos

### 6.1 Tipos de Filtrado

El sistema ofrece dos modos de filtrado:

#### A. Filtrado por Períodos Predefinidos

**Opciones disponibles**:

1. **Semana en Curso**: Lunes a domingo de la semana actual
2. **Semana Pasada**: Los 7 días anteriores a la semana actual
3. **1 Semana Adelante**: Los próximos 7 días después de la semana actual
4. **2 Semanas Pasadas**: Las dos semanas anteriores a la semana actual
5. **2 Semanas Adelante**: Las próximas dos semanas después de la semana actual
6. **Mes Pasado**: Todo el mes anterior
7. **Mes Actual**: Todo el mes en curso
8. **1 Mes Adelante**: Todo el mes siguiente

**Cálculo de semanas**:
```python
def get_week_range(date):
    start = date - timedelta(days=date.weekday())  # Lunes
    end = start + timedelta(days=6)                # Domingo
    return start, end
```

#### B. Filtrado por Rango Personalizado

- Permite seleccionar fechas de inicio y fin arbitrarias
- Usa controles de calendario interactivos
- Se activa con el checkbox "Rango de Fechas"

### 6.2 Filtrado por Ejecutivo

- **Opción "Todos"**: Muestra datos de todos los ejecutivos
- **Selección específica**: Filtra solo los registros del ejecutivo seleccionado
- El filtro se aplica **después** del filtrado por fecha

### 6.3 Lógica de Filtrado

**Ubicación**: dashboard.py:115-150 (`filter_by_period()`)

El filtrado se aplica usando la **fecha base** de cada proceso:

```python
df[(df[base_column] >= start_date) & (df[base_column] <= end_date)]
```

**Esto significa**:
- Se incluyen registros cuyo deadline (fecha base) cae dentro del período seleccionado
- No se filtran por fecha de ejecución del ejecutivo
- Permite ver qué acciones deberían completarse en el período

---

## 7. Métricas y Resúmenes

### 7.1 Resumen Global (Tab 1)

**Ubicación**: dashboard.py:625-669

#### Estadísticas Principales:

1. **Total de Registros**: Suma de todos los registros únicos (por ID) en todos los procesos
2. **Completados**: Registros con color verde (fecha ejecutivo existe)
3. **Pendientes**: Registros con color amarillo o rojo
4. **% Global Completado**: (Completados / Total) × 100
5. **% Global Pendiente**: (Pendientes / Total) × 100

**Eliminación de Duplicados**:
```python
combined_df = pd.concat(all_process_data).drop_duplicates(subset=['ID'])
```
Como un mismo siniestro puede aparecer en múltiples procesos, se eliminan duplicados por ID para el resumen global.

### 7.2 Resumen por Ejecutivo

**Ubicación**: dashboard.py:210-320 (`create_executive_summary()`)

#### Métricas Calculadas por Ejecutivo:

| Métrica | Descripción | Cálculo |
|---------|-------------|---------|
| **Total Casos** | Número de registros asignados | `len(exec_data)` |
| **Clientes Únicos** | Cantidad de clientes diferentes | `exec_data['Cliente'].nunique()` |
| **En Tiempo** | Casos completados antes del deadline | Count donde `Estado Tiempo = "En Tiempo"` |
| **Retrasadas** | Casos completados después del deadline | Count donde `Estado Tiempo = "Retrasado"` |
| **Pendientes** | Casos sin completar + sin fecha base | Count donde `Estado Tiempo = "Pendiente" o "Sin Fecha Base"` |
| **% Completado** | Porcentaje de casos con fecha ejecutivo | `(Completados / Total) × 100` |
| **Prima USD** | Suma de primas en dólares | Suma donde `Moneda = "Dólares"` |
| **Prima Nacional** | Suma de primas en pesos | Suma donde `Moneda = "Nacional"` |

#### Separación de Monedas:

**IMPORTANTE**: El sistema calcula las primas por separado según la moneda:

```python
usd_data = exec_data[exec_data['Moneda'] == 'Dólares']
nacional_data = exec_data[exec_data['Moneda'] == 'Nacional']

prima_usd = usd_data['PrimaNeta_numeric'].sum()
prima_nacional = nacional_data['PrimaNeta_numeric'].sum()
```

**Extracción de Valores Numéricos**:
```python
def extract_numeric_prima(prima_str):
    # Remove 'USD$', '$', commas
    numeric_str = str(prima_str).replace('USD$', '').replace('$', '').replace(',', '')
    return float(numeric_str)
```

---

## 8. Interfaz de Usuario

### 8.1 Diseño Visual

**Inspiración**: Material Design 3
**Fuente**: Roboto (Google Font)
**Tema**: Forzado a modo claro

#### Paleta de Colores:

- **Fondo general**: `#f8f9fa` (gris claro)
- **Tarjetas/contenedores**: `#ffffff` (blanco)
- **Encabezados**: `#0d1b2a` (azul-gris oscuro)
- **Acento primario**: `#005f73` (azul verdoso)
- **Bordes**: `#dee2e6` (gris medio)

#### Efectos Visuales:

- **Sombras**: `box-shadow: 0 4px 12px rgba(0,0,0,0.05)`
- **Hover**: Elevación adicional y sombra más pronunciada
- **Bordes de estado**: Barra de color de 4px a la izquierda de cada fila

### 8.2 Estructura de Tabs

#### Tab 1: Resumen Global

**Contenido**:
1. Estadísticas globales en texto
2. 3 métricas principales (% completado, % pendiente, total)
3. Tabla de resumen por ejecutivo
4. Botón de exportación global

#### Tab 2: Detalle por Proceso

**Contenido** (repetido para cada uno de los 7 procesos):
1. Expander con título y contador de registros
2. Barra de búsqueda por cliente o póliza
3. Tabla con codificación de colores
4. Botón de exportación individual

### 8.3 Codificación Visual de Tablas

**Ubicación**: dashboard.py:709-723 (`highlight_by_priority()`)

Cada fila se colorea uniformemente según su prioridad:

```python
if color_priority == 'green':
    # Verde claro con texto verde oscuro
    return ['background-color: #dcfce7; color: #14532d; border-left: 4px solid #16a34a; font-weight: 600']
elif color_priority == 'yellow':
    # Amarillo claro con texto marrón oscuro
    return ['background-color: #fef3c7; color: #92400e; border-left: 4px solid #d97706; font-weight: 600']
elif color_priority == 'red':
    # Rojo claro con texto rojo oscuro
    return ['background-color: #fee2e2; color: #991b1b; border-left: 4px solid #dc2626; font-weight: 600']
```

**Accesibilidad**:
- Alto contraste entre texto y fondo
- Barra de color adicional para daltonismo
- Fuente en negrita para legibilidad

---

## 9. Funcionalidades de Exportación

### 9.1 Método de Exportación

**Tecnología**: BytesIO (en memoria, sin escritura a disco)

**Ventajas**:
- No requiere permisos de escritura
- Más rápido
- Sin archivos temporales
- Mejor para entornos cloud

**Código**:
```python
output = BytesIO()
df.to_excel(output, index=False, engine='openpyxl')
output.seek(0)

st.download_button(
    label="Exportar",
    data=output,
    file_name=f"reporte_{timestamp}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

### 9.2 Tipos de Exportación

#### A. Exportación Global
- **Contenido**: Todos los registros únicos de todos los procesos
- **Nombre archivo**: `resumen_global_YYYYMMDD_HHMM.xlsx`
- **Columnas**: Todas las columnas del DataFrame combinado

#### B. Exportación por Proceso
- **Contenido**: Registros específicos de un proceso individual
- **Nombre archivo**: `reporte_[NombreProceso]_YYYYMMDD_HHMM.xlsx`
- **Columnas**: Columnas visibles sin campos internos (Color Priority, Timing Color)

### 9.3 Formato de Fechas en Exportación

**Timestamps en nombre de archivo**:
```python
datetime.now().strftime('%Y%m%d_%H%M')
# Ejemplo: 20250107_1430
```

---

## 10. Funcionalidad de Búsqueda

**Ubicación**: dashboard.py:687-698

### 10.1 Ámbito de Búsqueda

- **Búsqueda independiente** por proceso
- Cada proceso tiene su propio campo de búsqueda
- No hay búsqueda global

### 10.2 Campos Buscables

```python
mask = (display_df['Cliente'].str.contains(search_term, case=False, na=False) |
        display_df['Pólizas'].str.contains(search_term, case=False, na=False))
```

**Se busca en**:
1. **Cliente**: Nombre del cliente
2. **Pólizas**: Números de póliza

**Características**:
- **Case-insensitive**: No distingue mayúsculas/minúsculas
- **Búsqueda parcial**: Encuentra coincidencias dentro de la cadena
- **Seguro con NaN**: No arroja error con valores nulos

---

## 11. Formato de Fechas

### 11.1 Formato de Visualización

**Español**: "21 de julio"
**Internacional**: "dd/mm/yyyy"

**Función de formato español**:
```python
def format_date_spanish(date):
    spanish_months = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }

    day = date.day
    month = spanish_months[date.month]
    return f"{day} de {month}"
```

### 11.2 Conversión de Fechas

**En carga de datos**:
```python
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')
```

- `errors='coerce'`: Convierte fechas inválidas a `NaT` (Not a Time)
- Manejo robusto de datos inconsistentes

---

## 12. Casos Especiales y Consideraciones

### 12.1 Registros sin Fecha Base

**Problema**: Un registro no tiene fecha base (deadline) definida

**Tratamiento**:
- **Status**: "Sin fecha base"
- **Color**: Rojo (alta prioridad)
- **Fecha Ejecutivo**: "Sin acción" si tampoco existe
- **Estado Tiempo**: "Sin Fecha Base" (amarillo) si ejecutivo ya actuó

**Implicación**:
- Indica problema en los datos fuente
- Requiere revisión manual
- Se considera prioritario por falta de información

### 12.2 Limpieza de Nombres de Ejecutivo

```python
df['Ejecutivo'] = df['Ejecutivo'].str.strip()
```

**Propósito**:
- Eliminar espacios al inicio y final
- Evitar duplicados por espacios extra
- Asegurar consistencia en filtros y agrupaciones

### 12.3 Valores de Prima Neta

**Formato en Excel**: Puede incluir símbolos de moneda
**Tratamiento**:
```python
numeric_str = str(prima_str).replace('USD$', '').replace('$', '').replace(',', '')
```

**Visualización**:
```python
currency_symbol = '$' if currency == 'Nacional' else 'USD$'
formatted_prima = f"{currency_symbol}{row['PrimaNeta']:,.2f}"
```

### 12.4 Comparación de Fechas

**Normalización a solo fecha**:
```python
exec_date.date() <= base_date.date()
```

**Razón**:
- Evitar problemas con componentes de hora
- Comparaciones más intuitivas
- Consistencia en evaluación de plazos

---

## 13. Evolución del Sistema

### 13.1 Historial de Cambios Principales

Según los commits de Git:

1. **Múltiples actualizaciones de Excel**: Actualización frecuente de datos
2. **Cambios de UI**: Transición a diseño moderno basado en Material Design 3
3. **Expansión de períodos**: De solo semanas a incluir períodos mensuales
4. **Sistema de 7 procesos**: Evolución desde 4 procesos originales

### 13.2 Funcionalidades Añadidas

Comparando con la versión de backup:

- ✅ Modo de selección de rango de fechas
- ✅ Períodos de 2 semanas
- ✅ Períodos mensuales
- ✅ Columna "Estado Tiempo" adicional
- ✅ Exportación en memoria (BytesIO)
- ✅ Diseño visual moderno
- ✅ Sistema de tabs
- ✅ Métricas mejoradas por ejecutivo

---

## 14. Consideraciones de Desempeño

### 14.1 Optimizaciones Implementadas

1. **Deduplicación**: Solo en resumen global para evitar doble conteo
2. **Cálculo bajo demanda**: Métricas se calculan al filtrar
3. **Exportación en memoria**: Evita I/O de disco
4. **Pandas vectorizado**: Operaciones optimizadas en DataFrames

### 14.2 Limitaciones Conocidas

1. **Tamaño de archivo Excel**: 460KB actual, podría crecer con el tiempo
2. **Recarga completa**: Cada cambio de filtro recalcula todo
3. **Sin caché**: No hay persistencia entre sesiones
4. **Cálculo de tiempo de respuesta promedio**: Actualmente simplificado

---

## 15. Flujos de Usuario Típicos

### 15.1 Caso de Uso 1: Revisión Semanal de Ejecutivo

```
1. Usuario abre dashboard
2. Selecciona "Semana en Curso"
3. Selecciona ejecutivo específico
4. Revisa Tab 1 para métricas generales
5. Cambia a Tab 2
6. Expande proceso específico
7. Identifica casos rojos (vencidos)
8. Planifica acciones correctivas
```

### 15.2 Caso de Uso 2: Reporte Mensual

```
1. Usuario abre dashboard
2. Selecciona "Mes Pasado"
3. Mantiene filtro "Todos" los ejecutivos
4. Revisa Tab 1 - Resumen por Ejecutivo
5. Analiza % completado por ejecutivo
6. Identifica ejecutivos con retrasos
7. Exporta resumen global
8. Prepara presentación de resultados
```

### 15.3 Caso de Uso 3: Seguimiento de Cliente Específico

```
1. Usuario abre dashboard
2. Selecciona período amplio (ej: Mes Actual)
3. Va a Tab 2
4. Expande proceso relevante
5. Usa barra de búsqueda con nombre de cliente
6. Revisa estado de todos los procesos del cliente
7. Exporta detalles específicos del proceso
```

---

## 16. Glosario Técnico

### 16.1 Términos del Dominio

- **Siniestro**: Evento asegurado que genera un reclamo
- **Prima Neta**: Monto de la prima de seguro (sin recargos)
- **Ramo**: Tipo o categoría de seguro (ej: Empresariales, Equipo de Contratistas)
- **Cobertura**: Carta que confirma la cobertura del siniestro
- **Siniestralidad**: Solicitud formal del proceso de reclamo

### 16.2 Términos Técnicos

- **Fecha Base**: Deadline esperado para completar una acción
- **Fecha Ejecutivo**: Fecha en que el ejecutivo completó la acción
- **Color Priority**: Código de color para urgencia del caso
- **Estado Tiempo**: Clasificación de puntualidad de la acción
- **Timing Status**: Evaluación de si se cumplió el plazo

### 16.3 Estados del Sistema

- **Completado**: Acción finalizada (existe fecha ejecutivo)
- **Pendiente**: Acción sin completar con tiempo suficiente (>1 día)
- **Vencido**: Acción sin completar después del deadline
- **En Tiempo**: Acción completada antes o en el deadline
- **Retrasado**: Acción completada después del deadline
- **Sin Fecha Base**: Registro sin deadline definido

---

## 17. Fórmulas y Cálculos Clave

### 17.1 Días hasta Deadline

```python
dias_hasta_deadline = (fecha_base.date() - hoy).days
```

**Interpretación**:
- Positivo: Días restantes antes del deadline
- Cero: Vence hoy
- Negativo: Días vencido (pasado el deadline)

### 17.2 Porcentaje de Completado

```python
% = (Casos_Completados / Total_Casos) × 100
```

Donde:
- **Casos Completados**: Registros con `Color Priority == 'green'`
- **Total Casos**: Todos los registros del ejecutivo/proceso

### 17.3 Agregación de Primas

```python
Prima_Total_USD = Σ(PrimaNeta donde Moneda == 'Dólares')
Prima_Total_Nacional = Σ(PrimaNeta donde Moneda == 'Nacional')
```

**Nota**: Las primas NO se convierten entre monedas, se reportan por separado.

---

## 18. Manejo de Errores

### 18.1 Carga de Datos

```python
try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    return
```

**Comportamiento**:
- Muestra mensaje de error en interfaz
- Detiene ejecución del dashboard
- No produce crasheo de aplicación

### 18.2 Conversión de Fechas

```python
pd.to_datetime(df[col], errors='coerce')
```

**Comportamiento**:
- Fechas inválidas se convierten a `NaT`
- Permite continuar procesamiento
- Se manejan como "sin fecha" en lógica posterior

### 18.3 Extracción de Prima Neta

```python
try:
    return float(numeric_str)
except:
    return 0.0
```

**Comportamiento**:
- Valores no numéricos se convierten a 0.0
- Evita errores en agregaciones
- Permite continuar procesamiento

---

## 19. Configuración de Desarrollo

### 19.1 Entorno de Desarrollo (DevContainer)

```json
{
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "postCreateCommand": "pip install -r requirements.txt",
  "postStartCommand": "streamlit run dashboard.py",
  "forwardPorts": [8501]
}
```

**Características**:
- Python 3.11 preconfigurado
- Instalación automática de dependencias
- Servidor Streamlit se inicia automáticamente
- Puerto 8501 expuesto

### 19.2 Dependencias Requeridas

```
streamlit
pandas
numpy
plotly
openpyxl
```

**Instalación**:
```bash
pip install -r requirements.txt
```

---

## 20. Ejecución del Sistema

### 20.1 Inicio Manual

```bash
streamlit run dashboard.py
```

**Resultado**:
- Servidor web local en puerto 8501
- Dashboard accesible en http://localhost:8501
- Auto-refresh al modificar código

### 20.2 Requisitos Previos

1. Python 3.11 instalado
2. Dependencias instaladas
3. Archivo `reporte_danos.xlsx` en el mismo directorio que `dashboard.py`
4. Conexión a Internet (para cargar fuentes de Google)

---

## 21. Mantenimiento y Actualización

### 21.1 Actualización de Datos

**Proceso**:
1. Reemplazar archivo `reporte_danos.xlsx`
2. Asegurar que columnas mantienen los mismos nombres
3. Recargar página del dashboard

**Consideraciones**:
- No modificar nombres de columnas críticas
- Mantener formato de fechas consistente
- Campo `Cancelaciones` debe existir

### 21.2 Agregar Nuevos Procesos

**Pasos**:
1. Agregar columnas de fecha base y ejecutivo al Excel
2. Actualizar lista `date_columns` en `load_data()` (línea 29)
3. Agregar par al diccionario `processes` en `main()` (línea 602)
4. Actualizar diccionario `column_mapping` en `get_missing_dates()` (línea 161)

### 21.3 Modificar Períodos de Filtrado

**Ubicaciones**:
- Lista de opciones: dashboard.py:566
- Lógica de cálculo: `filter_by_period()` (línea 115)
- Formato de visualización: `get_period_range_spanish()` (línea 56)

---

## 22. Preguntas Frecuentes (FAQ)

### Q1: ¿Por qué algunos registros no aparecen?

**R**: Verifique:
1. Campo `Cancelaciones` = "SI" → se excluye automáticamente
2. Fecha base fuera del período seleccionado
3. Filtro de ejecutivo activo

### Q2: ¿Qué significa "Sin fecha base"?

**R**: El registro no tiene fecha de deadline definida en el Excel. Requiere corrección en datos fuente.

### Q3: ¿Cómo se cuentan los casos "En Tiempo"?

**R**: Solo casos donde la fecha de acción del ejecutivo es menor o igual a la fecha base (deadline).

### Q4: ¿Por qué las primas no se suman entre USD y Nacional?

**R**: Son monedas diferentes y se reportan por separado. No hay tasa de conversión configurada.

### Q5: ¿Puedo modificar el umbral de 1 día para casos rojos?

**R**: Sí, modificar la línea 377 de dashboard.py:
```python
if days_until_deadline > [NUEVO_UMBRAL]:
```

### Q6: ¿Los datos exportados incluyen el filtrado aplicado?

**R**: Sí, la exportación solo incluye registros visibles según filtros activos.

---

## 23. Mejoras Futuras Sugeridas

### 23.1 Funcionalidades

- [ ] Dashboard de tendencias históricas
- [ ] Alertas por email para vencimientos próximos
- [ ] Gráficos de desempeño por ejecutivo
- [ ] Búsqueda global (cross-process)
- [ ] Filtros múltiples por ramo de seguro
- [ ] Comentarios/notas por registro
- [ ] Cálculo real de tiempo de respuesta promedio

### 23.2 Optimizaciones

- [ ] Caché de datos cargados
- [ ] Carga incremental de datos
- [ ] Paginación de tablas grandes
- [ ] Índices de base de datos para búsquedas rápidas

### 23.3 Integraciones

- [ ] Autenticación de usuarios
- [ ] Roles y permisos por ejecutivo
- [ ] Conexión directa a base de datos
- [ ] API para sincronización automática
- [ ] Notificaciones push

---

## 24. Contacto y Soporte

Para preguntas técnicas sobre el sistema, consultar:
- **Documentación**: Este documento
- **Código fuente**: `dashboard.py` (comentado)
- **Configuración**: `.devcontainer/devcontainer.json`
- **Dependencias**: `requirements.txt`

---

## 25. Conclusión

El **Dashboard de Control de Seguimiento de Daños** es una herramienta robusta que automatiza el seguimiento de plazos en procesos de siniestros, proporcionando visibilidad inmediata del estado de cumplimiento y facilitando la toma de decisiones operativas.

### Fortalezas:
✅ Filtrado flexible por períodos y ejecutivos
✅ Codificación visual intuitiva por colores
✅ Exportación sencilla a Excel
✅ Métricas comprensivas de desempeño
✅ Interfaz moderna y responsive
✅ Manejo robusto de datos inconsistentes

### Consideraciones Importantes:
⚠️ Registros con `Cancelaciones = "SI"` son excluidos automáticamente
⚠️ Sistema usa fecha base (deadline) para filtrado de períodos
⚠️ Umbral de urgencia es 1 día antes del deadline
⚠️ Primas en diferentes monedas no se consolidan

El sistema está diseñado para evolucionar según las necesidades del negocio, con una arquitectura modular que facilita agregar nuevos procesos, métricas y funcionalidades.

---

**Versión del Documento**: 1.0
**Fecha**: 7 de Enero, 2025
**Sistema**: Dashboard de Control de Seguimiento de Daños v2.0

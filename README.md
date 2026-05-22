# ⚡ OptiAssign — Sistema de Asignación Óptima de Personal

> **Asignatura:** Investigación Operativa e Ingeniería de Sistemas  
> **Método:** Algoritmo Húngaro (Kuhn-Munkres) · Complejidad O(n³)  
> **Tecnología:** Python · Streamlit · Plotly · NumPy · Pandas

---

## 📋 Descripción

**OptiAssign** es un sistema web interactivo que resuelve el **Problema de Asignación Óptima** mediante el **Método Húngaro**. Permite asignar trabajadores a tareas minimizando costos/tiempos o maximizando eficiencia, con visualización paso a paso del algoritmo.

### ¿Qué problemas resuelve?
- Asignación de operarios a máquinas (manufactura)
- Rutas de conductores a zonas de entrega (logística)
- Turnos de personal a departamentos (hospitales, empresas)
- Proyectos a equipos de desarrollo (IT)
- Cualquier problema de asignación uno-a-uno

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Paso 1: Clonar / descargar el proyecto
```bash
# Si tienes git
git clone <url-del-repositorio>
cd asignacion_optima

# O simplemente descarga la carpeta y entra a ella
cd asignacion_optima
```

### Paso 2: (Opcional) Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en:  
**http://localhost:8501**

---

## 📁 Estructura del Proyecto

```
asignacion_optima/
│
├── app.py                 # Aplicación principal (Streamlit UI)
├── algoritmo_hungaro.py   # Implementación del Método Húngaro
├── utils.py               # Utilidades: gráficos, exportación, métricas
├── styles.css             # Estilos personalizados (tema oscuro)
├── requirements.txt       # Dependencias Python
└── README.md              # Documentación
```

---

## ⚙️ Funcionalidades

### Ingreso de Datos
- ✅ Configuración de dimensiones (2×2 hasta 8×8)
- ✅ Nombres personalizados de trabajadores y tareas
- ✅ Ingreso manual de la matriz de costos/eficiencias
- ✅ Carga de 5 ejemplos predefinidos
- ✅ Generación de ejemplos aleatorios
- ✅ Validación automática de datos

### Optimización
- ✅ **Minimización**: costos, tiempos, distancias
- ✅ **Maximización**: eficiencia, rendimiento, beneficio
- ✅ Soporte para matrices no cuadradas (ficticias automáticas)
- ✅ Garantía de solución globalmente óptima

### Resultados
- ✅ Tabla de asignación óptima con badges visuales
- ✅ Valor total óptimo (mínimo o máximo)
- ✅ Resumen ejecutivo textual
- ✅ Métricas estadísticas (ahorro vs. promedio aleatorio)

### Visualizaciones
- ✅ Mapa de calor interactivo de la matriz
- ✅ Grafo bipartito de asignaciones
- ✅ Gráfico de barras comparativo
- ✅ Indicador gauge de optimización

### Trazabilidad
- ✅ Pasos detallados del algoritmo con matrices
- ✅ Explicación textual de cada transformación
- ✅ Indicadores de cobertura de ceros

### Exportación
- ✅ Descarga en Excel (.xlsx) con 4 hojas
- ✅ Descarga en JSON
- ✅ Historial de soluciones (últimas 5)

---

## 🔬 Fundamento Matemático

### Formulación del Problema
```
Minimizar:   Z = Σᵢ Σⱼ cᵢⱼ · xᵢⱼ

Sujeto a:    Σⱼ xᵢⱼ = 1   ∀i  (cada trabajador: 1 sola tarea)
             Σᵢ xᵢⱼ = 1   ∀j  (cada tarea: 1 solo trabajador)
             xᵢⱼ ∈ {0,1}       (asignación binaria)
```

### Pasos del Método Húngaro
1. **Cuadrar la matriz** (agregar ficticias si n ≠ m)
2. **Reducción por filas** — restar mínimo de cada fila
3. **Reducción por columnas** — restar mínimo de cada columna
4. **Asignación de ceros independientes** — buscar matching máximo
5. **Cobertura mínima de ceros** — aplicar Teorema de König
6. **Ajuste de matriz** — crear nuevos ceros con valor θ
7. **Iterar** hasta encontrar n asignaciones independientes

### Complejidad
| Aspecto    | Valor  |
|-----------|--------|
| Tiempo    | O(n³)  |
| Espacio   | O(n²)  |
| Óptimo    | ✅ Sí  |
| Exacto    | ✅ Sí  |

---

## 🎓 Guía para Defensa Universitaria

### Estructura sugerida de la presentación (15-20 min)

**1. Introducción al Problema (2 min)**
- ¿Qué es el Problema de Asignación?
- ¿Por qué es importante en Investigación Operativa?
- Ejemplos de aplicaciones reales

**2. Modelado Matemático (3 min)**
- Mostrar la formulación matemática (tab "Fundamento Teórico")
- Explicar variables de decisión xᵢⱼ ∈ {0,1}
- Explicar las restricciones de flujo

**3. El Método Húngaro (4 min)**
- Historia y relevancia (Harold Kuhn, 1955)
- Explicar los 7 pasos del algoritmo
- Destacar la complejidad O(n³)

**4. Demostración del Software (5 min)**
- Abrir la aplicación en vivo
- Cargar un ejemplo predefinido (ej: "Proyecto de Construcción 4×4")
- Presionar "Resolver Problema"
- Mostrar resultados y gráficos
- Ir al tab "Paso a Paso" y explicar cada paso

**5. Análisis de Resultados (2 min)**
- Interpretar el grafo bipartito
- Explicar el indicador gauge
- Mostrar la exportación a Excel

**6. Conclusiones (2 min)**
- ¿Qué aprendimos?
- ¿Cómo contribuye la IO a la toma de decisiones?
- Limitaciones y extensiones posibles

---

## 📦 Dependencias

| Librería    | Versión mínima | Uso                            |
|------------|----------------|--------------------------------|
| streamlit   | 1.32.0         | Framework web interactivo      |
| numpy       | 1.24.0         | Operaciones matriciales        |
| pandas      | 2.0.0          | Manejo de tablas de datos      |
| plotly      | 5.18.0         | Visualizaciones interactivas   |
| openpyxl    | 3.1.0          | Exportación a Excel            |

---

## 🌐 Despliegue en Streamlit Cloud (gratuito)

1. Sube el proyecto a GitHub (repositorio público o privado)
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio y el archivo `app.py`
5. Click en "Deploy" — ¡listo! URL pública gratuita

---

## 📄 Licencia

Proyecto educativo desarrollado para la asignatura de Investigación Operativa.  
Libre para uso académico y educativo.

---

*OptiAssign v2.0 · Método Húngaro · O(n³) · Investigación Operativa*

"""
=============================================================================
UTILIDADES DEL SISTEMA DE ASIGNACIÓN ÓPTIMA
=============================================================================
Funciones auxiliares para visualización, exportación y análisis de resultados.

Incluye:
- Generación de gráficos con Plotly
- Exportación a Excel
- Métricas estadísticas
- Formateo de resultados
=============================================================================
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZACIONES PLOTLY
# ─────────────────────────────────────────────────────────────────────────────

PALETTE = {
    "fondo":       "#0D1117",
    "superficie":  "#161B22",
    "borde":       "#30363D",
    "acento1":     "#00D4FF",
    "acento2":     "#7EE787",
    "acento3":     "#FF6E40",
    "acento4":     "#F0883E",
    "texto":       "#E6EDF3",
    "texto_sub":   "#8B949E",
    "asignado":    "#238636",
    "no_asignado": "#21262D",
    "cero":        "#1F6FEB",
}


def crear_heatmap_matriz(
    matriz: np.ndarray,
    nombres_filas: list,
    nombres_cols: list,
    titulo: str = "Matriz de Costos",
    asignacion: list = None,
) -> go.Figure:
    """
    Crea un heatmap interactivo de la matriz con la asignación resaltada.
    
    Args:
        matriz: Matriz numérica 2D
        nombres_filas: Etiquetas de filas (trabajadores)
        nombres_cols: Etiquetas de columnas (tareas)
        titulo: Título del gráfico
        asignacion: Lista de tuplas (i, j) con la asignación óptima
    
    Returns:
        Figura Plotly
    """
    n_f, n_c = matriz.shape

    # Crear máscara para resaltar asignación
    mask = np.zeros_like(matriz, dtype=float)
    if asignacion:
        for (i, j) in asignacion:
            if i < n_f and j < n_c:
                mask[i][j] = 1.0

    # Texto personalizado para cada celda
    texto = []
    for i in range(n_f):
        fila_texto = []
        for j in range(n_c):
            val = f"{matriz[i][j]:.1f}"
            if asignacion and (i, j) in asignacion:
                val = f"★ {val}"
            fila_texto.append(val)
        texto.append(fila_texto)

    fig = go.Figure()

    # Capa base del heatmap
    fig.add_trace(go.Heatmap(
        z=matriz,
        x=nombres_cols,
        y=nombres_filas,
        text=texto,
        texttemplate="%{text}",
        textfont={"size": 13, "color": "white", "family": "monospace"},
        colorscale=[
            [0.0, "#0D2137"],
            [0.3, "#0F4C81"],
            [0.7, "#1565C0"],
            [1.0, "#42A5F5"],
        ],
        showscale=True,
        colorbar=dict(
            title=dict(text="Valor", font=dict(color=PALETTE["texto_sub"])),
            tickfont=dict(color=PALETTE["texto_sub"]),
            bgcolor=PALETTE["superficie"],
            bordercolor=PALETTE["borde"],
        ),
    ))

    # Resaltar celdas asignadas con marcadores
    if asignacion:
        xs, ys, vals = [], [], []
        for (i, j) in asignacion:
            if i < n_f and j < n_c:
                xs.append(nombres_cols[j])
                ys.append(nombres_filas[i])
                vals.append(f"<b>{nombres_filas[i]}</b> → <b>{nombres_cols[j]}</b><br>Valor: {matriz[i][j]:.1f}")

        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers",
            marker=dict(
                symbol="star",
                size=22,
                color=PALETTE["acento2"],
                line=dict(color="white", width=1.5),
            ),
            text=vals,
            hoverinfo="text",
            name="Asignación Óptima",
        ))

    fig.update_layout(
        title=dict(text=titulo, font=dict(color=PALETTE["texto"], size=16)),
        paper_bgcolor=PALETTE["fondo"],
        plot_bgcolor=PALETTE["superficie"],
        font=dict(color=PALETTE["texto"]),
        xaxis=dict(
            title="Tareas",
            tickfont=dict(size=11),
            showgrid=False,
            linecolor=PALETTE["borde"],
        ),
        yaxis=dict(
            title="Trabajadores",
            tickfont=dict(size=11),
            showgrid=False,
            linecolor=PALETTE["borde"],
            autorange="reversed",
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        height=350,
        legend=dict(
            font=dict(color=PALETTE["texto_sub"]),
            bgcolor=PALETTE["superficie"],
            bordercolor=PALETTE["borde"],
        ),
    )
    return fig


def crear_grafo_asignacion(
    asignacion: list,
    nombres_trabajadores: list,
    nombres_tareas: list,
    costos: list,
    tipo_opt: str = "minimizar",
) -> go.Figure:
    """
    Crea un grafo bipartito visual de las asignaciones óptimas.
    
    Args:
        asignacion: Lista de tuplas (i, j)
        nombres_trabajadores: Nombres de trabajadores
        nombres_tareas: Nombres de tareas
        costos: Lista de costos/valores por asignación
        tipo_opt: 'minimizar' o 'maximizar'
    
    Returns:
        Figura Plotly del grafo bipartito
    """
    fig = go.Figure()

    n_t = len(nombres_trabajadores)
    n_ta = len(nombres_tareas)

    # Posiciones del grafo bipartito
    y_trabajadores = [i * (10 / max(n_t - 1, 1)) for i in range(n_t)]
    y_tareas = [i * (10 / max(n_ta - 1, 1)) for i in range(n_ta)]

    # Dibujar aristas de asignación
    for idx, (i, j) in enumerate(asignacion):
        if i >= n_t or j >= n_ta:
            continue
        x0, y0 = 0.15, y_trabajadores[i]
        x1, y1 = 0.85, y_tareas[j]
        costo = costos[idx] if idx < len(costos) else 0

        # Línea de conexión
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode="lines",
            line=dict(color=PALETTE["acento2"], width=3, dash="solid"),
            hoverinfo="skip",
            showlegend=False,
        ))

        # Etiqueta de costo en el centro de la arista
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        unidad = "efic." if tipo_opt == "maximizar" else ("costo" if "cost" in tipo_opt else "valor")
        fig.add_annotation(
            x=mx, y=my,
            text=f"<b>{costo:.1f}</b>",
            showarrow=False,
            font=dict(color=PALETTE["acento4"], size=12),
            bgcolor=PALETTE["superficie"],
            bordercolor=PALETTE["borde"],
            borderpad=3,
        )

    # Nodos de trabajadores (izquierda)
    fig.add_trace(go.Scatter(
        x=[0.15] * n_t,
        y=y_trabajadores,
        mode="markers+text",
        marker=dict(
            size=40,
            color=PALETTE["acento1"],
            symbol="circle",
            line=dict(color="white", width=2),
        ),
        text=[f"<b>{n[:12]}</b>" for n in nombres_trabajadores],
        textposition="middle left",
        textfont=dict(color=PALETTE["texto"], size=11),
        hovertext=nombres_trabajadores,
        hoverinfo="text",
        name="Trabajadores",
    ))

    # Nodos de tareas (derecha)
    fig.add_trace(go.Scatter(
        x=[0.85] * n_ta,
        y=y_tareas,
        mode="markers+text",
        marker=dict(
            size=40,
            color=PALETTE["acento3"],
            symbol="square",
            line=dict(color="white", width=2),
        ),
        text=[f"<b>{n[:12]}</b>" for n in nombres_tareas],
        textposition="middle right",
        textfont=dict(color=PALETTE["texto"], size=11),
        hovertext=nombres_tareas,
        hoverinfo="text",
        name="Tareas",
    ))

    fig.update_layout(
        title=dict(
            text="Grafo de Asignación Óptima",
            font=dict(color=PALETTE["texto"], size=16),
        ),
        paper_bgcolor=PALETTE["fondo"],
        plot_bgcolor=PALETTE["superficie"],
        xaxis=dict(
            showticklabels=False, showgrid=False,
            zeroline=False, range=[-0.3, 1.3],
        ),
        yaxis=dict(
            showticklabels=False, showgrid=False,
            zeroline=False,
        ),
        height=max(350, n_t * 60),
        margin=dict(l=120, r=120, t=50, b=20),
        legend=dict(
            font=dict(color=PALETTE["texto_sub"]),
            bgcolor=PALETTE["superficie"],
            bordercolor=PALETTE["borde"],
        ),
    )
    return fig


def crear_grafico_comparacion(
    matriz_original: np.ndarray,
    asignacion: list,
    nombres_trabajadores: list,
    nombres_tareas: list,
) -> go.Figure:
    """
    Crea un gráfico de barras comparando el costo asignado vs. el mínimo posible individual.
    """
    labels, costos_asignados, costos_min = [], [], []

    for (i, j) in asignacion:
        if i >= len(nombres_trabajadores) or j >= len(nombres_tareas):
            continue
        labels.append(f"{nombres_trabajadores[i][:10]}")
        costos_asignados.append(float(matriz_original[i][j]))
        costos_min.append(float(matriz_original[i].min()))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Valor Asignado (Óptimo Global)",
        x=labels,
        y=costos_asignados,
        marker_color=PALETTE["acento1"],
        text=[f"{v:.1f}" for v in costos_asignados],
        textposition="outside",
        textfont=dict(color=PALETTE["texto"]),
    ))

    fig.add_trace(go.Bar(
        name="Mínimo Individual (Fila)",
        x=labels,
        y=costos_min,
        marker_color=PALETTE["acento3"],
        text=[f"{v:.1f}" for v in costos_min],
        textposition="outside",
        textfont=dict(color=PALETTE["texto"]),
        opacity=0.75,
    ))

    fig.update_layout(
        title=dict(
            text="Comparación: Valor Asignado vs. Mínimo Individual",
            font=dict(color=PALETTE["texto"], size=16),
        ),
        barmode="group",
        paper_bgcolor=PALETTE["fondo"],
        plot_bgcolor=PALETTE["superficie"],
        font=dict(color=PALETTE["texto"]),
        xaxis=dict(
            title="Trabajadores", gridcolor=PALETTE["borde"],
            linecolor=PALETTE["borde"],
        ),
        yaxis=dict(
            title="Valor", gridcolor=PALETTE["borde"],
            linecolor=PALETTE["borde"],
        ),
        legend=dict(
            bgcolor=PALETTE["superficie"],
            bordercolor=PALETTE["borde"],
            font=dict(color=PALETTE["texto_sub"]),
        ),
        height=380,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def crear_gauge_eficiencia(costo_total: float, costo_max: float, tipo_opt: str) -> go.Figure:
    """
    Crea un indicador tipo gauge del porcentaje de optimización logrado.
    """
    if tipo_opt == "maximizar":
        pct = min(100, (costo_total / max(costo_max, 1)) * 100)
        label = "Eficiencia Lograda"
    else:
        pct = max(0, 100 - (costo_total / max(costo_max, 1)) * 100)
        label = "% de Optimización"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        title={"text": label, "font": {"color": PALETTE["texto"], "size": 14}},
        number={"suffix": "%", "font": {"color": PALETTE["acento2"], "size": 28}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": PALETTE["texto_sub"],
                "tickfont": {"color": PALETTE["texto_sub"]},
            },
            "bar": {"color": PALETTE["acento2"]},
            "bgcolor": PALETTE["superficie"],
            "borderwidth": 1,
            "bordercolor": PALETTE["borde"],
            "steps": [
                {"range": [0, 33], "color": "#2D1B1B"},
                {"range": [33, 66], "color": "#1B2D1B"},
                {"range": [66, 100], "color": "#0D3B1F"},
            ],
            "threshold": {
                "line": {"color": PALETTE["acento1"], "width": 3},
                "thickness": 0.8,
                "value": pct,
            },
        },
    ))

    fig.update_layout(
        paper_bgcolor=PALETTE["fondo"],
        font=dict(color=PALETTE["texto"]),
        height=260,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# EXPORTACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def exportar_excel(resultado: dict) -> bytes:
    """
    Genera un archivo Excel con todos los resultados del análisis.
    
    Returns:
        Bytes del archivo Excel listo para descargar
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # ── Hoja 1: Resumen Ejecutivo ──────────────────────────
        resumen_data = {
            "Campo": [
                "Fecha de análisis",
                "Tipo de optimización",
                "Número de trabajadores",
                "Número de tareas",
                "Valor óptimo total",
                "Algoritmo utilizado",
                "Complejidad",
            ],
            "Valor": [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                resultado.get("tipo_opt", "N/A").capitalize(),
                resultado.get("n_filas", "N/A"),
                resultado.get("n_cols", "N/A"),
                f"{resultado.get('costo_total', 0):.2f}",
                "Método Húngaro (Kuhn-Munkres)",
                "O(n³)",
            ],
        }
        pd.DataFrame(resumen_data).to_excel(
            writer, sheet_name="Resumen Ejecutivo", index=False
        )

        # ── Hoja 2: Asignación Óptima ─────────────────────────
        tabla = resultado.get("tabla_resultados", [])
        if tabla:
            df_asig = pd.DataFrame(tabla)[["trabajador", "tarea", "costo"]]
            df_asig.columns = ["Trabajador", "Tarea Asignada", "Valor"]
            df_asig.to_excel(writer, sheet_name="Asignación Óptima", index=False)

        # ── Hoja 3: Matriz Original ───────────────────────────
        mat = resultado.get("matriz_original")
        nombres_t = resultado.get("nombres_trabajadores", [])
        nombres_ta = resultado.get("nombres_tareas", [])
        if mat is not None:
            df_mat = pd.DataFrame(
                mat,
                index=nombres_t[:len(mat)],
                columns=nombres_ta[:mat.shape[1]] if hasattr(mat, "shape") else nombres_ta
            )
            df_mat.to_excel(writer, sheet_name="Matriz Original")

        # ── Hoja 4: Pasos del Algoritmo ───────────────────────
        pasos = resultado.get("pasos", [])
        if pasos:
            pasos_data = [
                {
                    "Paso": p.get("numero", i),
                    "Título": p.get("titulo", ""),
                    "Descripción": p.get("descripcion", ""),
                }
                for i, p in enumerate(pasos)
            ]
            pd.DataFrame(pasos_data).to_excel(
                writer, sheet_name="Pasos del Algoritmo", index=False
            )

    return output.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# MÉTRICAS Y ESTADÍSTICAS
# ─────────────────────────────────────────────────────────────────────────────

def calcular_metricas(resultado: dict) -> dict:
    """
    Calcula métricas estadísticas adicionales para el análisis.
    
    Returns:
        Diccionario con métricas computadas
    """
    mat = resultado.get("matriz_original")
    asig = resultado.get("asignacion", [])
    tipo = resultado.get("tipo_opt", "minimizar")
    costo = resultado.get("costo_total", 0)

    if mat is None or len(asig) == 0:
        return {}

    n_filas = resultado.get("n_filas", mat.shape[0])
    n_cols = resultado.get("n_cols", mat.shape[1])

    # Promedio de todos los valores
    promedio_global = float(mat[:n_filas, :n_cols].mean())

    # Suma total si se asignara aleatoriamente (aprox.)
    suma_aleatoria = float(mat[:n_filas, :n_cols].mean() * min(n_filas, n_cols))

    # Porcentaje de ahorro vs suma de mínimos individuales
    suma_minimos_fila = float(mat[:n_filas, :n_cols].min(axis=1).sum())
    suma_max_fila = float(mat[:n_filas, :n_cols].max(axis=1).sum())

    if tipo == "minimizar":
        ahorro_vs_aleatorio = ((suma_aleatoria - costo) / max(suma_aleatoria, 1)) * 100
        ahorro_label = "Ahorro vs. promedio aleatorio"
    else:
        ahorro_vs_aleatorio = ((costo - suma_aleatoria) / max(suma_aleatoria, 1)) * 100
        ahorro_label = "Ganancia vs. promedio aleatorio"

    return {
        "costo_total": costo,
        "promedio_global": promedio_global,
        "suma_aleatoria": suma_aleatoria,
        "suma_minimos_fila": suma_minimos_fila,
        "suma_max_fila": suma_max_fila,
        "ahorro_pct": ahorro_vs_aleatorio,
        "ahorro_label": ahorro_label,
        "n_asignaciones": len(asig),
        "valor_promedio_asignacion": costo / max(len(asig), 1),
    }


def formatear_numero(n: float, decimales: int = 2) -> str:
    """Formatea un número con separadores de miles."""
    if n == int(n):
        return f"{int(n):,}"
    return f"{n:,.{decimales}f}"

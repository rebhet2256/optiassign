"""
=============================================================================
SISTEMA DE ASIGNACIÓN ÓPTIMA DE PERSONAL A TAREAS
=============================================================================
Aplicación principal desarrollada con Streamlit.

Asignatura: Investigación Operativa e Ingeniería de Sistemas
Método:     Algoritmo Húngaro (Kuhn-Munkres)
Versión:    2.0 — Profesional / Dashboard

Ejecución:
    streamlit run app.py

=============================================================================
"""

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime

# ── Módulos internos ──────────────────────────────────────────────────────────
from algoritmo_hungaro import (
    resolver_asignacion,
    EJEMPLOS_PREDEFINIDOS,
    generar_ejemplo_aleatorio,
)
from utils import (
    crear_heatmap_matriz,
    crear_grafo_asignacion,
    crear_grafico_comparacion,
    crear_gauge_eficiencia,
    exportar_excel,
    calcular_metricas,
    formatear_numero,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="OptiAssign | Sistema de Asignación Óptima",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cargar CSS personalizado ──────────────────────────────────────────────────
def cargar_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

cargar_css()

# ═══════════════════════════════════════════════════════════════════════════════
# ESTADO DE SESIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def init_session():
    defaults = {
        "resultado":         None,
        "historial":         [],
        "n_trabajadores":    3,
        "n_tareas":          3,
        "tipo_opt":          "minimizar",
        "nombres_t":         [],
        "nombres_ta":        [],
        "matriz_datos":      None,
        "ejemplo_cargado":   "",
        "mostrar_pasos":     False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header fade-in">
  <div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
    <div style="font-size:2.8rem; line-height:1;">⚡</div>
    <div>
      <div class="app-title">OptiAssign</div>
      <div class="app-subtitle">
        <span class="accent-dot"></span>
        Sistema de Asignación Óptima de Personal · Método Húngaro · Investigación Operativa
      </div>
    </div>
    <div style="margin-left:auto;">
      <span class="status-badge status-optimal">✓ Sistema Activo</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")

    # ── Dimensiones del problema ──────────────────────────────
    st.markdown("**Dimensiones del Problema**")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        n_t = st.number_input(
            "👷 Trabajadores", min_value=2, max_value=8,
            value=st.session_state["n_trabajadores"], step=1, key="inp_nt"
        )
    with col_s2:
        n_ta = st.number_input(
            "📋 Tareas", min_value=2, max_value=8,
            value=st.session_state["n_tareas"], step=1, key="inp_nta"
        )

    st.session_state["n_trabajadores"] = int(n_t)
    st.session_state["n_tareas"] = int(n_ta)

    st.markdown("---")

    # ── Tipo de optimización ──────────────────────────────────
    st.markdown("**Tipo de Optimización**")
    tipo_opt = st.radio(
        label="",
        options=["minimizar", "maximizar"],
        format_func=lambda x: (
            "📉 Minimizar (Costos / Tiempo)"
            if x == "minimizar"
            else "📈 Maximizar (Eficiencia)"
        ),
        index=0 if st.session_state["tipo_opt"] == "minimizar" else 1,
        key="radio_tipo",
    )
    st.session_state["tipo_opt"] = tipo_opt

    st.markdown("---")

    # ── Ejemplos predefinidos ─────────────────────────────────
    st.markdown("**📚 Cargar Ejemplo**")
    opciones_ej = ["— Seleccionar —"] + list(EJEMPLOS_PREDEFINIDOS.keys())
    ej_sel = st.selectbox("", opciones_ej, key="sel_ejemplo")

    if st.button("📥 Cargar Ejemplo", use_container_width=True):
        if ej_sel != "— Seleccionar —":
            ej = EJEMPLOS_PREDEFINIDOS[ej_sel]
            st.session_state["n_trabajadores"] = len(ej["trabajadores"])
            st.session_state["n_tareas"]       = len(ej["tareas"])
            st.session_state["tipo_opt"]       = ej["tipo"]
            st.session_state["nombres_t"]      = ej["trabajadores"].copy()
            st.session_state["nombres_ta"]     = ej["tareas"].copy()
            st.session_state["matriz_datos"]   = np.array(ej["matriz"], dtype=float)
            st.session_state["ejemplo_cargado"] = ej_sel
            st.session_state["resultado"]      = None
            st.rerun()

    if st.button("🎲 Ejemplo Aleatorio", use_container_width=True):
        n = max(st.session_state["n_trabajadores"], st.session_state["n_tareas"])
        ej = generar_ejemplo_aleatorio(n, st.session_state["tipo_opt"])
        st.session_state["n_trabajadores"] = len(ej["trabajadores"])
        st.session_state["n_tareas"]       = len(ej["tareas"])
        st.session_state["nombres_t"]      = ej["trabajadores"].copy()
        st.session_state["nombres_ta"]     = ej["tareas"].copy()
        st.session_state["matriz_datos"]   = np.array(ej["matriz"], dtype=float)
        st.session_state["ejemplo_cargado"] = f"Aleatorio {n}×{n}"
        st.session_state["resultado"]      = None
        st.rerun()

    st.markdown("---")

    # ── Historial ─────────────────────────────────────────────
    st.markdown("**🕒 Historial de Soluciones**")
    if not st.session_state["historial"]:
        st.markdown(
            "<p style='color:#484F58;font-size:0.8rem;'>Sin soluciones previas.</p>",
            unsafe_allow_html=True
        )
    else:
        for idx, h in enumerate(reversed(st.session_state["historial"][-5:])):
            with st.expander(f"#{len(st.session_state['historial'])-idx} · {h['nombre']}", expanded=False):
                st.markdown(
                    f"<span style='color:#8B949E;font-size:0.8rem;'>"
                    f"🕐 {h['fecha']}<br>Valor óptimo: <b style='color:#00D4FF'>{h['costo']:.2f}</b>"
                    f"</span>",
                    unsafe_allow_html=True
                )

    if st.session_state["historial"]:
        if st.button("🗑️ Limpiar Historial", use_container_width=True):
            st.session_state["historial"] = []
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='color:#484F58;font-size:0.75rem;text-align:center;'>"
        "OptiAssign v2.0 · Investigación Operativa<br>"
        "Método Húngaro · O(n³)"
        "</p>",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════════

tab_ingreso, tab_resultado, tab_pasos, tab_teoria = st.tabs([
    "📝 Ingreso de Datos",
    "📊 Resultados",
    "🔍 Paso a Paso",
    "📚 Fundamento Teórico",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: INGRESO DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_ingreso:
    n_t  = st.session_state["n_trabajadores"]
    n_ta = st.session_state["n_tareas"]

    # Inicializar nombres si están vacíos o dimensión cambió
    if len(st.session_state["nombres_t"]) != n_t:
        st.session_state["nombres_t"] = [f"Trabajador {i+1}" for i in range(n_t)]
    if len(st.session_state["nombres_ta"]) != n_ta:
        st.session_state["nombres_ta"] = [f"Tarea {j+1}" for j in range(n_ta)]

    # Inicializar matriz si cambió de tamaño o es None
    mat_actual = st.session_state.get("matriz_datos")
    if (mat_actual is None or
        mat_actual.shape[0] != n_t or
        mat_actual.shape[1] != n_ta):
        st.session_state["matriz_datos"] = np.ones((n_t, n_ta), dtype=float) * 1.0

    # ── Banner del ejemplo cargado ────────────────────────────
    if st.session_state.get("ejemplo_cargado"):
        st.info(
            f"📥 Ejemplo cargado: **{st.session_state['ejemplo_cargado']}** — "
            f"Puedes editar los datos directamente en la tabla."
        )

    # ── Sección: Nombres ──────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 👷 Nombres de Trabajadores")
        nombres_t_nuevos = []
        for i in range(n_t):
            val_actual = (
                st.session_state["nombres_t"][i]
                if i < len(st.session_state["nombres_t"])
                else f"Trabajador {i+1}"
            )
            nombre = st.text_input(
                f"Trabajador {i+1}",
                value=val_actual,
                key=f"nombre_t_{i}",
                placeholder=f"Ej: Ana García",
            )
            nombres_t_nuevos.append(nombre.strip() or f"Trabajador {i+1}")
        st.session_state["nombres_t"] = nombres_t_nuevos

    with col_right:
        st.markdown("### 📋 Nombres de Tareas")
        nombres_ta_nuevos = []
        for j in range(n_ta):
            val_actual = (
                st.session_state["nombres_ta"][j]
                if j < len(st.session_state["nombres_ta"])
                else f"Tarea {j+1}"
            )
            nombre = st.text_input(
                f"Tarea {j+1}",
                value=val_actual,
                key=f"nombre_ta_{j}",
                placeholder=f"Ej: Diseño Web",
            )
            nombres_ta_nuevos.append(nombre.strip() or f"Tarea {j+1}")
        st.session_state["nombres_ta"] = nombres_ta_nuevos

    st.markdown("---")

    # ── Sección: Matriz ───────────────────────────────────────
    lbl_tipo = (
        "Costos / Tiempos" if st.session_state["tipo_opt"] == "minimizar"
        else "Eficiencias / Rendimiento"
    )
    st.markdown(f"### 📊 Matriz de {lbl_tipo}")

    hint_val = "valores más bajos = mejor" if st.session_state["tipo_opt"] == "minimizar" else "valores más altos = mejor"
    st.markdown(
        f"<p style='color:#8B949E;font-size:0.83rem;margin-bottom:1rem;'>"
        f"Ingresa el valor de cada celda ({hint_val}). "
        f"Dimensión: {n_t} trabajadores × {n_ta} tareas."
        f"</p>",
        unsafe_allow_html=True
    )

    # Construir la matriz mediante inputs numéricos en columnas
    mat_nueva = np.zeros((n_t, n_ta), dtype=float)
    nombres_t_display = st.session_state["nombres_t"]
    nombres_ta_display = st.session_state["nombres_ta"]

    # Encabezado de columnas
    cols_header = st.columns([2] + [1] * n_ta)
    with cols_header[0]:
        st.markdown(
            "<p style='color:#8B949E;font-size:0.75rem;text-transform:uppercase;"
            "letter-spacing:0.06em;padding:0.4rem 0;'>Trabajador \\ Tarea</p>",
            unsafe_allow_html=True
        )
    for j in range(n_ta):
        with cols_header[j + 1]:
            st.markdown(
                f"<p style='color:#00D4FF;font-size:0.75rem;text-align:center;"
                f"font-weight:600;letter-spacing:0.04em;padding:0.4rem 0;'>"
                f"{nombres_ta_display[j][:10]}</p>",
                unsafe_allow_html=True
            )

    for i in range(n_t):
        cols_row = st.columns([2] + [1] * n_ta)
        with cols_row[0]:
            st.markdown(
                f"<p style='color:#7EE787;font-size:0.82rem;font-weight:500;"
                f"padding:0.55rem 0;'>{nombres_t_display[i][:16]}</p>",
                unsafe_allow_html=True
            )
        for j in range(n_ta):
            val_prev = float(st.session_state["matriz_datos"][i][j]) if (
                st.session_state["matriz_datos"] is not None and
                i < st.session_state["matriz_datos"].shape[0] and
                j < st.session_state["matriz_datos"].shape[1]
            ) else 1.0
            with cols_row[j + 1]:
                v = st.number_input(
                    label="",
                    value=val_prev,
                    min_value=0.0,
                    max_value=9999.0,
                    step=1.0,
                    format="%.1f",
                    key=f"m_{i}_{j}",
                    label_visibility="collapsed",
                )
                mat_nueva[i][j] = v

    # Actualizar matriz en session state
    st.session_state["matriz_datos"] = mat_nueva

    # ── Preview visual de la matriz ───────────────────────────
    with st.expander("🔍 Vista previa de la Matriz", expanded=False):
        df_preview = pd.DataFrame(
            mat_nueva,
            index=nombres_t_display,
            columns=nombres_ta_display,
        )
        st.dataframe(df_preview.style.highlight_min(axis=1, color="#0F4C81"), use_container_width=True)
        st.markdown(
            "<p style='color:#8B949E;font-size:0.78rem;margin-top:0.5rem;'>"
            "🔵 Resaltado azul: mínimo por fila (base para reducción inicial)"
            "</p>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Botones de acción ─────────────────────────────────────
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

    with col_btn1:
        if st.button("⚡ Resolver Problema", type="primary", use_container_width=True):
            # Validar que la matriz no tenga valores negativos para minimización
            mat = st.session_state["matriz_datos"]
            if st.session_state["tipo_opt"] == "minimizar" and (mat < 0).any():
                st.error("⚠️ Para minimización, todos los valores deben ser ≥ 0.")
            else:
                with st.spinner("🔄 Ejecutando Método Húngaro..."):
                    resultado = resolver_asignacion(
                        matriz=mat.tolist(),
                        tipo_opt=st.session_state["tipo_opt"],
                        nombres_trabajadores=st.session_state["nombres_t"],
                        nombres_tareas=st.session_state["nombres_ta"],
                    )
                    st.session_state["resultado"] = resultado

                    # Agregar al historial
                    entrada_hist = {
                        "nombre": f"{n_t}×{n_ta} · {st.session_state['tipo_opt'].capitalize()}",
                        "fecha":  datetime.now().strftime("%H:%M:%S"),
                        "costo":  resultado["costo_total"],
                        "n_t":    n_t,
                        "n_ta":   n_ta,
                    }
                    st.session_state["historial"].append(entrada_hist)

                st.success("✅ ¡Problema resuelto! Revisa la pestaña **📊 Resultados**.")

    with col_btn2:
        if st.button("🗑️ Limpiar Datos", use_container_width=True):
            n_t_  = st.session_state["n_trabajadores"]
            n_ta_ = st.session_state["n_tareas"]
            st.session_state["matriz_datos"] = np.ones((n_t_, n_ta_), dtype=float)
            st.session_state["nombres_t"]    = [f"Trabajador {i+1}" for i in range(n_t_)]
            st.session_state["nombres_ta"]   = [f"Tarea {j+1}" for j in range(n_ta_)]
            st.session_state["resultado"]    = None
            st.session_state["ejemplo_cargado"] = ""
            st.rerun()

    with col_btn3:
        st.info(f"Dimensión actual: **{n_t}×{n_ta}**", icon="📐")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: RESULTADOS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_resultado:
    resultado = st.session_state.get("resultado")

    if resultado is None:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;color:#484F58;'>
            <div style='font-size:4rem;margin-bottom:1rem;'>📊</div>
            <div style='font-size:1.1rem;font-weight:600;color:#8B949E;margin-bottom:0.5rem;'>
                Sin resultados aún
            </div>
            <div style='font-size:0.85rem;'>
                Ingresa los datos en la pestaña <b>📝 Ingreso de Datos</b>
                y presiona <b>⚡ Resolver Problema</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Métricas principales ───────────────────────────────
        metricas = calcular_metricas(resultado)
        lbl_valor = (
            "Costo Total Mínimo" if resultado["tipo_opt"] == "minimizar"
            else "Eficiencia Total Máxima"
        )

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric(
                lbl_valor,
                f"{formatear_numero(resultado['costo_total'])}",
                delta=f"{metricas.get('ahorro_pct', 0):.1f}% {metricas.get('ahorro_label','').split('vs.')[0].strip()}"
            )
        with col_m2:
            st.metric("Asignaciones Realizadas", metricas.get("n_asignaciones", 0))
        with col_m3:
            st.metric(
                "Promedio por Asignación",
                f"{metricas.get('valor_promedio_asignacion', 0):.2f}"
            )
        with col_m4:
            st.metric(
                "Pasos del Algoritmo",
                len(resultado.get("pasos", []))
            )

        st.markdown("---")

        # ── Tabla de asignación óptima ─────────────────────────
        st.markdown("### 🏆 Asignación Óptima")

        tabla = resultado.get("tabla_resultados", [])
        if tabla:
            # Construir HTML de tabla
            tipo_col = "Costo/Tiempo" if resultado["tipo_opt"] == "minimizar" else "Eficiencia"
            filas_html = ""
            for row in tabla:
                filas_html += f"""<tr>
                  <td>
                    <span class='badge badge-blue'>
                      👷 {row['trabajador']}
                    </span>
                  </td>
                  <td>
                    <span class='badge badge-green'>
                      📋 {row['tarea']}
                    </span>
                  </td>
                  <td style='font-family:var(--font-mono);font-weight:600;color:#00D4FF;text-align:center;'>
                    {row['costo']:.2f}
                  </td>
                </tr>
                """

            st.markdown(f"""
            <div class='resultado-tabla'>
              <table>
                <thead>
                  <tr>
                    <th>Trabajador</th>
                    <th>Tarea Asignada</th>
                    <th style='text-align:center;'>{tipo_col}</th>
                  </tr>
                </thead>
                <tbody>
                  {filas_html}
                </tbody>
              </table>
            </div>
            """, unsafe_allow_html=True)

            # Total
            st.markdown(
                f"<div style='text-align:right;margin-top:0.5rem;'>"
                f"<span class='badge badge-green'>✅ TOTAL ÓPTIMO: "
                f"<b style='font-size:1rem;'>{formatear_numero(resultado['costo_total'])}</b>"
                f"</span></div>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ── Visualizaciones ────────────────────────────────────
        st.markdown("### 📈 Visualizaciones")

        col_viz1, col_viz2 = st.columns(2)

        with col_viz1:
            st.markdown("**Mapa de Calor — Matriz con Asignación**")
            fig_heat = crear_heatmap_matriz(
                matriz=resultado["matriz_original"][:resultado["n_filas"], :resultado["n_cols"]],
                nombres_filas=resultado["nombres_trabajadores"],
                nombres_cols=resultado["nombres_tareas"],
                titulo="Matriz de Costos · ★ = Asignado",
                asignacion=resultado["asignacion"],
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        with col_viz2:
            st.markdown("**Grafo Bipartito de Asignación**")
            costos_asig = [resultado["matriz_original"][i][j] for (i, j) in resultado["asignacion"]]
            fig_grafo = crear_grafo_asignacion(
                asignacion=resultado["asignacion"],
                nombres_trabajadores=resultado["nombres_trabajadores"],
                nombres_tareas=resultado["nombres_tareas"],
                costos=costos_asig,
                tipo_opt=resultado["tipo_opt"],
            )
            st.plotly_chart(fig_grafo, use_container_width=True)

        col_viz3, col_viz4 = st.columns([2, 1])

        with col_viz3:
            st.markdown("**Comparación: Valor Asignado vs. Mínimo por Fila**")
            fig_comp = crear_grafico_comparacion(
                matriz_original=resultado["matriz_original"],
                asignacion=resultado["asignacion"],
                nombres_trabajadores=resultado["nombres_trabajadores"],
                nombres_tareas=resultado["nombres_tareas"],
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        with col_viz4:
            st.markdown("**Indicador de Optimización**")
            mat_orig = resultado["matriz_original"][:resultado["n_filas"], :resultado["n_cols"]]
            if resultado["tipo_opt"] == "maximizar":
                ref = float(mat_orig.max()) * resultado["n_filas"]
            else:
                ref = float(mat_orig.max(axis=1).sum())

            fig_gauge = crear_gauge_eficiencia(
                costo_total=resultado["costo_total"],
                costo_max=ref,
                tipo_opt=resultado["tipo_opt"],
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("---")

        # ── Resumen ejecutivo ──────────────────────────────────
        st.markdown("### 📋 Resumen Ejecutivo")

        tipo_str = "minimización" if resultado["tipo_opt"] == "minimizar" else "maximización"
        asig_str = ", ".join(
            [f"**{resultado['nombres_trabajadores'][i]}** → {resultado['nombres_tareas'][j]}"
             for (i, j) in resultado["asignacion"]]
        )

        st.markdown(f"""
        El Método Húngaro resolvió el problema de {tipo_str} de dimensión
        **{resultado['n_filas']}×{resultado['n_cols']}** en
        **{len(resultado['pasos'])} pasos**,
        encontrando la asignación óptima global con un valor de
        **{formatear_numero(resultado['costo_total'])}**.

        **Asignaciones:** {asig_str}

        La solución garantiza que no existe ninguna otra asignación posible
        que {'reduzca' if resultado['tipo_opt'] == 'minimizar' else 'supere'} este valor.
        El algoritmo opera con complejidad **O(n³)**, siendo eficiente para
        matrices de hasta cientos de trabajadores.
        """)

        st.markdown("---")

        # ── Exportar resultados ────────────────────────────────
        st.markdown("### 💾 Exportar Resultados")

        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            try:
                excel_bytes = exportar_excel(resultado)
                st.download_button(
                    label="📥 Descargar Excel (.xlsx)",
                    data=excel_bytes,
                    file_name=f"asignacion_optima_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Excel no disponible: {e}")

        with col_exp2:
            # Exportar JSON
            resultado_json = {
                "fecha": datetime.now().isoformat(),
                "tipo_opt": resultado["tipo_opt"],
                "costo_total": resultado["costo_total"],
                "asignacion": [
                    {
                        "trabajador": resultado["nombres_trabajadores"][i],
                        "tarea": resultado["nombres_tareas"][j],
                        "valor": float(resultado["matriz_original"][i][j])
                    }
                    for (i, j) in resultado["asignacion"]
                ],
                "pasos": len(resultado["pasos"]),
            }
            st.download_button(
                label="📄 Descargar JSON",
                data=json.dumps(resultado_json, ensure_ascii=False, indent=2),
                file_name=f"resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: PASOS DEL ALGORITMO
# ═══════════════════════════════════════════════════════════════════════════════

with tab_pasos:
    resultado = st.session_state.get("resultado")

    if resultado is None:
        st.markdown("""
        <div style='text-align:center;padding:3rem 2rem;color:#484F58;'>
            <div style='font-size:3rem;margin-bottom:1rem;'>🔍</div>
            <div style='font-size:1rem;color:#8B949E;'>
                Resuelve un problema primero para ver el proceso paso a paso.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        pasos = resultado.get("pasos", [])
        st.markdown(f"### 🔍 Trazabilidad del Algoritmo — {len(pasos)} pasos")
        st.markdown(
            "<p style='color:#8B949E;font-size:0.85rem;margin-bottom:1.5rem;'>"
            "Cada paso muestra la transformación de la matriz y la lógica aplicada "
            "en la ejecución del Método Húngaro.</p>",
            unsafe_allow_html=True
        )

        for paso in pasos:
            num    = paso.get("numero", 0)
            titulo = paso.get("titulo", "")
            desc   = paso.get("descripcion", "")
            mat    = paso.get("matriz")

            is_final = "✅" in titulo or "Óptim" in titulo

            color_accent = "#7EE787" if is_final else "#00D4FF"

            with st.expander(
                f"{'✅' if is_final else '🔢'} Paso {num}: {titulo}",
                expanded=(num <= 2 or is_final)
            ):
                st.markdown(
                    f"<p style='color:#8B949E;font-size:0.85rem;line-height:1.6;'>"
                    f"{desc}</p>",
                    unsafe_allow_html=True
                )

                if mat is not None:
                    n_f = resultado["n_filas"]
                    n_c = resultado["n_cols"]
                    # Tomar solo sub-matriz válida
                    sub_mat = mat[:n_f, :n_c] if mat.shape[0] >= n_f and mat.shape[1] >= n_c else mat

                    asig_paso = paso.get("asignacion") or paso.get("asignacion_parcial")

                    fig_paso = crear_heatmap_matriz(
                        matriz=sub_mat,
                        nombres_filas=resultado["nombres_trabajadores"][:n_f],
                        nombres_cols=resultado["nombres_tareas"][:n_c],
                        titulo=f"Matriz en Paso {num}",
                        asignacion=asig_paso,
                    )
                    st.plotly_chart(fig_paso, use_container_width=True)

                # Información adicional del paso
                if "minimos" in paso:
                    st.markdown(
                        "<p style='color:#8B949E;font-size:0.78rem;'>"
                        f"Valores reducidos: {[f'{v:.1f}' for v in paso['minimos'][:resultado['n_filas']]]}"
                        "</p>", unsafe_allow_html=True
                    )

                if "filas_cubiertas" in paso or "cols_cubiertas" in paso:
                    f_cub = paso.get("filas_cubiertas", [])
                    c_cub = paso.get("cols_cubiertas", [])
                    n_lin = len(f_cub) + len(c_cub)
                    st.markdown(
                        f"<p style='color:#F0883E;font-size:0.82rem;font-weight:600;'>"
                        f"📏 Líneas de cobertura: {n_lin} "
                        f"(Filas: {[r+1 for r in f_cub]} | "
                        f"Columnas: {[c+1 for c in c_cub]})</p>",
                        unsafe_allow_html=True
                    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: FUNDAMENTO TEÓRICO
# ═══════════════════════════════════════════════════════════════════════════════

with tab_teoria:
    st.markdown("## 📚 Fundamento Teórico — Método Húngaro")
    st.markdown("---")

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("""
        ### 🎯 ¿Qué es el Problema de Asignación?

        El **Problema de Asignación** es un caso especial del Problema de Transporte
        en Programación Lineal. Consiste en asignar `n` trabajadores a `n` tareas
        de manera **uno a uno**, minimizando el costo total o maximizando la eficiencia.

        **Formulación matemática:**

        Se tienen:
        - `n` trabajadores: `{W₁, W₂, ..., Wₙ}`
        - `n` tareas: `{T₁, T₂, ..., Tₙ}`
        - Matriz de costos `C` donde `cᵢⱼ` = costo de asignar `Wᵢ` a `Tⱼ`

        **Función objetivo (minimización):**
        """)

        st.markdown("""
        <div class='formula-box'>
        Minimizar: Z = Σᵢ Σⱼ cᵢⱼ · xᵢⱼ
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        **Sujeto a las restricciones:**
        """)

        st.markdown("""
        <div class='formula-box'>
        Σⱼ xᵢⱼ = 1  ∀i  (cada trabajador: 1 tarea)<br>
        Σᵢ xᵢⱼ = 1  ∀j  (cada tarea: 1 trabajador)<br>
        xᵢⱼ ∈ {0, 1}   (decisión binaria)
        </div>
        """, unsafe_allow_html=True)

    with col_t2:
        st.markdown("""
        ### 📜 Historia del Método Húngaro

        El Método Húngaro fue desarrollado por el matemático **Harold W. Kuhn** en **1955**,
        basándose en el trabajo previo del matemático húngaro **Dénes Kőnig** (1916) y
        **Jenő Egerváry** (1931).

        Por eso también se le conoce como el **Algoritmo de Kuhn-Munkres**
        (James Munkres lo refinó en 1957).

        **Importancia histórica:**
        - Primer algoritmo polinomial para el problema de asignación
        - Sentó las bases de la Optimización Combinatoria moderna
        - Revolucionó la Investigación Operativa en logística y planificación
        """)

        st.info("""
        **Complejidad Computacional:**
        - **Tiempo:** O(n³) — eficiente para matrices grandes
        - **Espacio:** O(n²) — almacena la matriz de costos
        - **Optimal:** Garantiza la solución globalmente óptima
        """)

    st.markdown("---")

    # ── Pasos del algoritmo ────────────────────────────────────
    st.markdown("### ⚙️ Pasos del Método Húngaro")

    pasos_teoria = [
        {
            "num": 1,
            "titulo": "Preparación",
            "desc": "Verificar que la matriz sea cuadrada. Si no lo es, agregar filas o columnas ficticias con costo 0. Para problemas de maximización, transformar a minimización restando cada elemento del valor máximo.",
            "formula": "c'ᵢⱼ = Cₘₐₓ - cᵢⱼ  (para maximización)"
        },
        {
            "num": 2,
            "titulo": "Reducción por Filas",
            "desc": "Restar el elemento mínimo de cada fila a todos los elementos de esa fila. Esto garantiza al menos un cero por fila sin alterar la solución óptima.",
            "formula": "c'ᵢⱼ = cᵢⱼ - min(cᵢ₁, cᵢ₂, ..., cᵢₙ)"
        },
        {
            "num": 3,
            "titulo": "Reducción por Columnas",
            "desc": "Restar el elemento mínimo de cada columna a todos los elementos de esa columna. Después de este paso, cada fila y columna tiene al menos un cero.",
            "formula": "c''ᵢⱼ = c'ᵢⱼ - min(c'₁ⱼ, c'₂ⱼ, ..., c'ₙⱼ)"
        },
        {
            "num": 4,
            "titulo": "Asignación de Ceros Independientes",
            "desc": "Encontrar el máximo número de ceros 'independientes' (sin compartir fila ni columna). Si se encuentran n ceros independientes, se ha encontrado la solución óptima.",
            "formula": "Si |Asignación| = n → ÓPTIMO ENCONTRADO"
        },
        {
            "num": 5,
            "titulo": "Cobertura Mínima",
            "desc": "Si no se encontraron n asignaciones, cubrir todos los ceros con el mínimo número de líneas (filas/columnas). Por el Teorema de König, el mínimo de líneas = máximo de ceros independientes.",
            "formula": "Mínimo de líneas = Máximo matching bipartito"
        },
        {
            "num": 6,
            "titulo": "Ajuste de la Matriz",
            "desc": "Encontrar el mínimo elemento no cubierto (θ). Restarlo de todos los no cubiertos y sumarlo a los doblemente cubiertos. Esto crea nuevos ceros para la siguiente iteración.",
            "formula": "Si no cubierto: c -= θ | Si doble cubierto: c += θ"
        },
        {
            "num": 7,
            "titulo": "Iteración",
            "desc": "Repetir pasos 4–6 hasta obtener n ceros independientes. El algoritmo converge en a lo sumo n iteraciones, garantizando O(n³) en total.",
            "formula": "Repetir hasta |Asignación| = n"
        },
    ]

    for p in pasos_teoria:
        with st.expander(f"📌 Paso {p['num']}: {p['titulo']}", expanded=(p['num'] <= 3)):
            col_p1, col_p2 = st.columns([3, 2])
            with col_p1:
                st.markdown(
                    f"<p style='color:#8B949E;font-size:0.85rem;line-height:1.65;'>{p['desc']}</p>",
                    unsafe_allow_html=True
                )
            with col_p2:
                st.markdown(
                    f"<div class='formula-box'>{p['formula']}</div>",
                    unsafe_allow_html=True
                )

    st.markdown("---")

    # ── Casos de uso reales ────────────────────────────────────
    st.markdown("### 🌍 Aplicaciones Reales")

    col_u1, col_u2, col_u3 = st.columns(3)

    casos = [
        ("🏭 Manufactura", "Asignación de operarios a máquinas, minimizando tiempos de setup y maximizando productividad en líneas de ensamblaje."),
        ("🚚 Logística", "Asignación de conductores a rutas de entrega, minimizando distancias recorridas y tiempos de entrega en flotas de transporte."),
        ("🏥 Salud", "Programación de médicos y enfermeras a turnos y servicios hospitalarios, optimizando cobertura y reduciendo horas extras."),
        ("💻 IT / Software", "Asignación de desarrolladores a módulos del proyecto según sus habilidades y estimaciones de tiempo de entrega."),
        ("📊 Finanzas", "Asignación de analistas a carteras de clientes, maximizando el retorno esperado según perfil de riesgo."),
        ("🎓 Educación", "Asignación de docentes a materias y salones, minimizando conflictos de horario y maximizando compatibilidad curricular."),
    ]

    for idx, (titulo, desc) in enumerate(casos):
        col = [col_u1, col_u2, col_u3][idx % 3]
        with col:
            st.markdown(f"""
            <div class='theory-box'>
              <h4>{titulo}</h4>
              <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Ventajas y limitaciones ────────────────────────────────
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("### ✅ Ventajas")
        ventajas = [
            "**Óptimo garantizado**: Siempre encuentra la solución globalmente óptima.",
            "**Eficiente**: Complejidad O(n³), viable para matrices grandes.",
            "**Versátil**: Funciona para minimización y maximización.",
            "**Exacto**: No es heurístico, no depende de parámetros aleatorios.",
            "**Matrices no cuadradas**: Se adapta añadiendo filas/columnas ficticias.",
        ]
        for v in ventajas:
            st.markdown(f"- {v}")

    with col_v2:
        st.markdown("### ⚠️ Limitaciones")
        limitaciones = [
            "**Una asignación por agente**: Cada trabajador recibe exactamente una tarea.",
            "**Sin preferencias múltiples**: No modela prioridades ni restricciones complejas.",
            "**Costos deterministas**: Los valores deben ser conocidos con certeza.",
            "**Escalabilidad**: Para n > 1000, se prefieren heurísticas o metaheurísticas.",
            "**Sin capacidades**: No maneja casos donde un agente puede hacer múltiples tareas.",
        ]
        for l in limitaciones:
            st.markdown(f"- {l}")

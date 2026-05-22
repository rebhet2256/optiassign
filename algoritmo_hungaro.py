"""
=============================================================================
ALGORITMO HÚNGARO - MÉTODO DE ASIGNACIÓN ÓPTIMA
=============================================================================
Implementación completa del Método Húngaro (Kuhn-Munkres Algorithm)
para resolver el Problema de Asignación en Investigación Operativa.

Complejidad temporal: O(n³)
Complejidad espacial: O(n²)

Autor: Sistema de Asignación Óptima de Personal
Materia: Investigación Operativa e Ingeniería de Sistemas
=============================================================================
"""

import numpy as np
import copy


class AlgoritmoHungaro:
    """
    Implementación del Método Húngaro para resolver problemas de asignación.
    
    El Método Húngaro resuelve el Problema de Asignación en tiempo polinomial,
    garantizando la solución óptima global, ya sea para minimización o maximización.
    
    Atributos:
        matriz_original (np.ndarray): Matriz de costos/tiempos/eficiencias original
        n_filas (int): Número de trabajadores (filas)
        n_cols (int): Número de tareas (columnas)
        tipo_opt (str): 'minimizar' o 'maximizar'
        pasos (list): Lista de pasos detallados del algoritmo
        asignacion (list): Lista de tuplas (trabajador, tarea)
        costo_total (float): Valor óptimo de la función objetivo
    """

    def __init__(self, matriz: np.ndarray, tipo_opt: str = "minimizar"):
        """
        Inicializa el solucionador con la matriz de costos.
        
        Args:
            matriz: Matriz de costos/tiempos/eficiencias (puede ser no cuadrada)
            tipo_opt: 'minimizar' para costos/tiempos, 'maximizar' para eficiencia
        """
        self.matriz_original = np.array(matriz, dtype=float)
        self.tipo_opt = tipo_opt.lower()
        self.n_filas = self.matriz_original.shape[0]
        self.n_cols = self.matriz_original.shape[1]
        self.pasos = []
        self.asignacion = []
        self.costo_total = 0
        self.matrices_intermedias = []

    def resolver(self) -> dict:
        """
        Ejecuta el Método Húngaro completo y retorna todos los resultados.
        
        Returns:
            dict con asignacion, costo_total, pasos, matrices_intermedias
        """
        self.pasos = []
        self.matrices_intermedias = []

        # ─────────────────────────────────────────────────
        # PASO 0: Preparación de la matriz
        # ─────────────────────────────────────────────────
        matriz = self.matriz_original.copy()

        self.pasos.append({
            "numero": 0,
            "titulo": "Matriz Original",
            "descripcion": (
                f"Matriz de {'costos/tiempos' if self.tipo_opt == 'minimizar' else 'eficiencias'} "
                f"de dimensión {self.n_filas}×{self.n_cols}. "
                f"Objetivo: {'Minimizar' if self.tipo_opt == 'minimizar' else 'Maximizar'}."
            ),
            "matriz": matriz.copy(),
        })

        # ─────────────────────────────────────────────────
        # PASO 1: Conversión para maximización
        # ─────────────────────────────────────────────────
        if self.tipo_opt == "maximizar":
            maximo = matriz.max()
            matriz = maximo - matriz
            self.pasos.append({
                "numero": 1,
                "titulo": "Conversión a Minimización",
                "descripcion": (
                    f"Para maximizar, restamos cada elemento del valor máximo ({maximo:.2f}). "
                    "Esto convierte el problema de maximización en uno de minimización equivalente."
                ),
                "matriz": matriz.copy(),
            })

        # ─────────────────────────────────────────────────
        # PASO 2: Cuadrar la matriz (si es necesario)
        # ─────────────────────────────────────────────────
        n = max(self.n_filas, self.n_cols)
        if self.n_filas != self.n_cols:
            pad_rows = n - self.n_filas
            pad_cols = n - self.n_cols
            if pad_rows > 0:
                matriz = np.vstack([matriz, np.zeros((pad_rows, self.n_cols))])
            if pad_cols > 0:
                matriz = np.hstack([matriz, np.zeros((n, pad_cols))])
            self.pasos.append({
                "numero": 2,
                "titulo": "Cuadrar la Matriz",
                "descripcion": (
                    f"La matriz no es cuadrada ({self.n_filas}×{self.n_cols}). "
                    f"Se agregan filas/columnas ficticias con costo 0 para hacerla {n}×{n}."
                ),
                "matriz": matriz.copy(),
            })

        # ─────────────────────────────────────────────────
        # PASO 3: Reducción por filas
        # ─────────────────────────────────────────────────
        min_filas = matriz.min(axis=1)
        for i in range(n):
            matriz[i] -= min_filas[i]

        self.pasos.append({
            "numero": 3,
            "titulo": "Reducción por Filas",
            "descripcion": (
                "Se resta el elemento mínimo de cada fila a todos los elementos de esa fila. "
                f"Mínimos por fila: {[f'{v:.1f}' for v in min_filas[:self.n_filas]]}. "
                "Esto garantiza al menos un cero por fila."
            ),
            "matriz": matriz.copy(),
            "minimos": min_filas.tolist(),
        })

        # ─────────────────────────────────────────────────
        # PASO 4: Reducción por columnas
        # ─────────────────────────────────────────────────
        min_cols = matriz.min(axis=0)
        for j in range(n):
            matriz[:, j] -= min_cols[j]

        self.pasos.append({
            "numero": 4,
            "titulo": "Reducción por Columnas",
            "descripcion": (
                "Se resta el elemento mínimo de cada columna a todos los elementos de esa columna. "
                f"Mínimos por columna: {[f'{v:.1f}' for v in min_cols[:self.n_cols]]}. "
                "Esto garantiza al menos un cero por columna."
            ),
            "matriz": matriz.copy(),
            "minimos": min_cols.tolist(),
        })

        # ─────────────────────────────────────────────────
        # PASOS 5+: Iteraciones del algoritmo core
        # ─────────────────────────────────────────────────
        iteracion = 0
        max_iter = 50

        while iteracion < max_iter:
            iteracion += 1

            # Encontrar asignación independiente de ceros
            asignacion_actual = self._asignar_ceros_independientes(matriz, n)

            # Si tenemos n asignaciones, hemos terminado
            if len(asignacion_actual) == n:
                self.pasos.append({
                    "numero": len(self.pasos),
                    "titulo": f"✅ Asignación Óptima Encontrada (Iteración {iteracion})",
                    "descripcion": (
                        f"Se encontraron {n} asignaciones independientes. "
                        "La solución óptima ha sido alcanzada."
                    ),
                    "matriz": matriz.copy(),
                    "asignacion": asignacion_actual,
                })
                break

            # Cobertura mínima de líneas
            filas_cubiertas, cols_cubiertas = self._cubrir_ceros_minimo(
                matriz, asignacion_actual, n
            )
            num_lineas = len(filas_cubiertas) + len(cols_cubiertas)

            self.pasos.append({
                "numero": len(self.pasos),
                "titulo": f"Cobertura de Ceros (Iteración {iteracion})",
                "descripcion": (
                    f"Se necesitan {num_lineas} líneas para cubrir todos los ceros. "
                    f"Filas cubiertas: {[r+1 for r in filas_cubiertas]}, "
                    f"Columnas cubiertas: {[c+1 for c in cols_cubiertas]}. "
                    f"{'No es óptimo aún, continuando...' if num_lineas < n else '¡Óptimo!'}"
                ),
                "matriz": matriz.copy(),
                "filas_cubiertas": list(filas_cubiertas),
                "cols_cubiertas": list(cols_cubiertas),
                "asignacion_parcial": asignacion_actual,
            })

            if num_lineas >= n:
                self.pasos.append({
                    "numero": len(self.pasos),
                    "titulo": "✅ Solución Óptima Verificada",
                    "descripcion": "El número de líneas de cobertura es igual a n. Solución óptima encontrada.",
                    "matriz": matriz.copy(),
                    "asignacion": asignacion_actual,
                })
                break

            # Ajuste: encontrar mínimo no cubierto y reducir/aumentar
            matriz = self._ajustar_matriz(
                matriz, filas_cubiertas, cols_cubiertas, n
            )

            self.pasos.append({
                "numero": len(self.pasos),
                "titulo": f"Ajuste de Matriz (Iteración {iteracion})",
                "descripcion": (
                    "Se resta el mínimo elemento no cubierto de todos los elementos no cubiertos, "
                    "y se suma a los elementos doblemente cubiertos. Esto crea nuevos ceros."
                ),
                "matriz": matriz.copy(),
            })

        # ─────────────────────────────────────────────────
        # CALCULAR COSTO TOTAL ÓPTIMO
        # ─────────────────────────────────────────────────
        asignacion_final = self._asignar_ceros_independientes(matriz, n)
        # Filtrar solo asignaciones válidas (dentro de dimensiones originales)
        asignacion_valida = [
            (i, j) for (i, j) in asignacion_final
            if i < self.n_filas and j < self.n_cols
        ]

        self.asignacion = asignacion_valida
        self.costo_total = sum(
            self.matriz_original[i][j] for (i, j) in asignacion_valida
        )

        return {
            "asignacion": self.asignacion,
            "costo_total": self.costo_total,
            "pasos": self.pasos,
            "tipo_opt": self.tipo_opt,
            "n_filas": self.n_filas,
            "n_cols": self.n_cols,
        }

    # ═══════════════════════════════════════════════════════════════
    # MÉTODOS AUXILIARES INTERNOS
    # ═══════════════════════════════════════════════════════════════

    def _asignar_ceros_independientes(self, matriz: np.ndarray, n: int) -> list:
        """
        Encuentra el conjunto máximo de ceros independientes (sin compartir fila/columna).
        Usa el algoritmo greedy + backtracking.
        """
        asignacion = {}        # fila -> columna
        cols_usadas = set()

        # Primera pasada: asignar ceros únicos en filas
        for i in range(n):
            ceros = [j for j in range(n) if abs(matriz[i][j]) < 1e-10]
            ceros_libres = [j for j in ceros if j not in cols_usadas]
            if len(ceros_libres) == 1:
                asignacion[i] = ceros_libres[0]
                cols_usadas.add(ceros_libres[0])

        # Segunda pasada: asignar filas restantes
        for i in range(n):
            if i not in asignacion:
                ceros = [j for j in range(n) if abs(matriz[i][j]) < 1e-10 and j not in cols_usadas]
                if ceros:
                    asignacion[i] = ceros[0]
                    cols_usadas.add(ceros[0])

        return list(asignacion.items())

    def _cubrir_ceros_minimo(self, matriz: np.ndarray, asignacion: list, n: int):
        """
        Encuentra el número mínimo de líneas (filas/columnas) para cubrir todos los ceros.
        Implementación del algoritmo de cobertura basado en matching bipartito.
        """
        asig_dict = dict(asignacion)          # fila -> columna asignada
        asig_inv = {v: k for k, v in asig_dict.items()}  # columna -> fila

        # Marcar filas sin asignación
        filas_marcadas = set(i for i in range(n) if i not in asig_dict)
        cols_marcadas = set()
        cambio = True

        while cambio:
            cambio = False
            # Marcar columnas con cero en fila marcada
            for i in filas_marcadas:
                for j in range(n):
                    if abs(matriz[i][j]) < 1e-10 and j not in cols_marcadas:
                        cols_marcadas.add(j)
                        cambio = True
            # Marcar filas con asignación en columna marcada
            for j in cols_marcadas:
                if j in asig_inv:
                    i = asig_inv[j]
                    if i not in filas_marcadas:
                        filas_marcadas.add(i)
                        cambio = True

        # Líneas de cobertura:
        filas_cubiertas = set(range(n)) - filas_marcadas
        cols_cubiertas = cols_marcadas

        return filas_cubiertas, cols_cubiertas

    def _ajustar_matriz(
        self,
        matriz: np.ndarray,
        filas_cubiertas: set,
        cols_cubiertas: set,
        n: int
    ) -> np.ndarray:
        """
        Ajusta la matriz restando el mínimo no cubierto y sumándolo en intersecciones dobles.
        """
        mat = matriz.copy()

        # Encontrar mínimo en elementos no cubiertos
        min_val = np.inf
        for i in range(n):
            for j in range(n):
                if i not in filas_cubiertas and j not in cols_cubiertas:
                    if mat[i][j] < min_val:
                        min_val = mat[i][j]

        if min_val == np.inf or min_val == 0:
            return mat

        # Restar a no cubiertos, sumar a doblemente cubiertos
        for i in range(n):
            for j in range(n):
                en_fila = i in filas_cubiertas
                en_col = j in cols_cubiertas
                if not en_fila and not en_col:
                    mat[i][j] -= min_val
                elif en_fila and en_col:
                    mat[i][j] += min_val

        return mat


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN DE CONVENIENCIA
# ─────────────────────────────────────────────────────────────────────────────

def resolver_asignacion(
    matriz: list,
    tipo_opt: str = "minimizar",
    nombres_trabajadores: list = None,
    nombres_tareas: list = None
) -> dict:
    """
    Función principal para resolver un problema de asignación.
    
    Args:
        matriz: Lista de listas con los costos/tiempos/eficiencias
        tipo_opt: 'minimizar' o 'maximizar'
        nombres_trabajadores: Lista de nombres de trabajadores
        nombres_tareas: Lista de nombres de tareas
    
    Returns:
        Diccionario completo con resultados, pasos y metadatos
    """
    alg = AlgoritmoHungaro(np.array(matriz, dtype=float), tipo_opt)
    resultado = alg.resolver()

    n_filas = alg.n_filas
    n_cols = alg.n_cols

    # Nombres por defecto
    if nombres_trabajadores is None:
        nombres_trabajadores = [f"Trabajador {i+1}" for i in range(n_filas)]
    if nombres_tareas is None:
        nombres_tareas = [f"Tarea {j+1}" for j in range(n_cols)]

    # Construir tabla de resultados legible
    tabla_resultados = []
    for (i, j) in resultado["asignacion"]:
        tabla_resultados.append({
            "trabajador_idx": i,
            "tarea_idx": j,
            "trabajador": nombres_trabajadores[i] if i < len(nombres_trabajadores) else f"T{i+1}",
            "tarea": nombres_tareas[j] if j < len(nombres_tareas) else f"Tarea {j+1}",
            "costo": float(alg.matriz_original[i][j]),
        })

    resultado["tabla_resultados"] = tabla_resultados
    resultado["nombres_trabajadores"] = nombres_trabajadores
    resultado["nombres_tareas"] = nombres_tareas
    resultado["matriz_original"] = alg.matriz_original

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# GENERADORES DE EJEMPLOS
# ─────────────────────────────────────────────────────────────────────────────

EJEMPLOS_PREDEFINIDOS = {
    "Ejemplo Básico 3×3": {
        "descripcion": "3 trabajadores, 3 tareas — problema clásico de asignación de costos",
        "tipo": "minimizar",
        "trabajadores": ["Ana García", "Luis Pérez", "María Rodríguez"],
        "tareas": ["Diseño Web", "Base de Datos", "Testing QA"],
        "matriz": [
            [9, 2, 7],
            [3, 6, 3],
            [5, 8, 1]
        ]
    },
    "Proyecto de Construcción 4×4": {
        "descripcion": "4 cuadrillas asignadas a 4 zonas de obra, minimizando días de trabajo",
        "tipo": "minimizar",
        "trabajadores": ["Cuadrilla Norte", "Cuadrilla Sur", "Cuadrilla Este", "Cuadrilla Oeste"],
        "tareas": ["Zona Residencial", "Zona Comercial", "Zona Industrial", "Zona Verde"],
        "matriz": [
            [14, 5, 8, 7],
            [2, 12, 6, 5],
            [7, 8, 3, 9],
            [2, 4, 6, 10]
        ]
    },
    "Equipo de Ventas 4×4": {
        "descripcion": "4 vendedores en 4 regiones — maximizando eficiencia de ventas (0-100%)",
        "tipo": "maximizar",
        "trabajadores": ["Vendedor A", "Vendedor B", "Vendedor C", "Vendedor D"],
        "tareas": ["Región Norte", "Región Sur", "Región Centro", "Región Costa"],
        "matriz": [
            [62, 78, 50, 101],
            [71, 84, 61, 73],
            [87, 92, 111, 71],
            [48, 64, 87, 77]
        ]
    },
    "Logística Express 5×5": {
        "descripcion": "5 conductores asignados a 5 rutas de entrega, minimizando kilómetros",
        "tipo": "minimizar",
        "trabajadores": ["Conductor 1", "Conductor 2", "Conductor 3", "Conductor 4", "Conductor 5"],
        "tareas": ["Ruta Aeropuerto", "Ruta Centro", "Ruta Norte", "Ruta Sur", "Ruta Industrial"],
        "matriz": [
            [10, 19, 8, 15, 19],
            [10, 18, 7, 17, 19],
            [13, 16, 9, 14, 19],
            [12, 19, 8, 18, 19],
            [14, 17, 10, 19, 19]
        ]
    },
    "Hospital - Turnos 3×4": {
        "descripcion": "3 enfermeras en 4 turnos (no cuadrada) — minimizando horas extras",
        "tipo": "minimizar",
        "trabajadores": ["Enfermera Carmen", "Enfermera Rosa", "Enfermera Julia"],
        "tareas": ["Turno Mañana", "Turno Tarde", "Turno Noche", "Turno Urgencias"],
        "matriz": [
            [3, 7, 5, 8],
            [6, 2, 9, 4],
            [5, 8, 3, 6]
        ]
    }
}


def generar_ejemplo_aleatorio(n: int, tipo: str = "minimizar") -> dict:
    """
    Genera una matriz de ejemplo aleatoria de tamaño n×n.
    
    Args:
        n: Tamaño de la matriz (número de trabajadores y tareas)
        tipo: 'minimizar' o 'maximizar'
    
    Returns:
        Diccionario con la configuración del ejemplo generado
    """
    rng = np.random.default_rng()
    if tipo == "minimizar":
        matriz = rng.integers(1, 20, size=(n, n)).tolist()
    else:
        matriz = rng.integers(40, 100, size=(n, n)).tolist()

    trabajadores = [f"Trabajador {chr(65+i)}" for i in range(n)]
    tareas = [f"Tarea {i+1}" for i in range(n)]

    return {
        "descripcion": f"Ejemplo aleatorio {n}×{n} generado automáticamente",
        "tipo": tipo,
        "trabajadores": trabajadores,
        "tareas": tareas,
        "matriz": matriz,
    }

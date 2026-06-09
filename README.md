Copyright © 2026 Agostina Zavia Martínez. All rights reserved.

# Más allá de Lotka-Volterra: Impacto de la estocasticidad y la estructura del paisaje en la extinción de especies mediante Modelos Basados en Individuos

Este repositorio contiene el código fuente y las simulaciones desarrolladas para el Trabajo de Fin de Grado (TFG) en Biología de la Universidad de Málaga. El proyecto contrasta las predicciones deterministas del modelo clásico de Lotka-Volterra con modelos estocásticos espacialmente explícitos, explorando el impacto de la fragmentación del hábitat y la viabilidad de los corredores ecológicos.

🌐 **Web narrativa interactiva:** [agos.github.io/beyond_lotka_volterra](https://agos.github.io/beyond_lotka_volterra) *(enlace pendiente de activar)*

---

## Estructura del Proyecto

```
TFG/
├── predator_prey/
│   ├── agent.py             ← Lógica de comportamiento de los agentes
│   ├── model.py             ← Modelos ABM (entornos y topologías)
│   ├── visualize.py         ← Dashboard interactivo (Solara + Altair)
│   └── beyond_lotka_volterra.ipynb  ← Notebook principal del TFG
(futura carpeta web)
```

### `agent.py`

Define el comportamiento a nivel micro de las entidades biológicas:

- **`SimplePrey` / `SimplePredator`**: Agentes base del modelo análogo a Lotka-Volterra estocástico (Fase IA). Movimiento aleatorio y reproducción/depredación por probabilidad fija.
- **`ParadoxPrey` / `ParadoxPredator`**: Variantes con mayor tasa de crecimiento, usadas para demostrar la paradoja del enriquecimiento (Fase IB).
- **`Prey` / `Predator`**: Agentes con dinámica metabólica completa: sistema de energía, capacidad de carga local y respuesta funcional de Holling tipo II (Fases IIA y IIB).
- **`RefugePredator`**: Extensión de `Predator` que respeta los límites del hábitat refugio (sin acceso a celdas de reserva).
- **`MountainPrey`**: Presa con preferencia estocástica (95%) por hábitat forestal protegido.
- **`TerritorialPredator`**: Depredador apical con alto coste metabólico que domina en ecosistemas insulares.

### `model.py`

Contiene el marco macro-espacial y las reglas topológicas del ecosistema:

- **`LotkaVolterraModel`**: Entorno base estocástico sobre plano toroidal (Fase IA).
- **`LogisticHollingModel`**: Modelo con dinámica metabólica y respuesta funcional de Holling tipo II (Fase IB).
- **`RefugeModel`**: Hábitat fragmentado con parches de refugio aleatorios — demuestra el efecto trampa ecológica (Fase IIA).
- **`SanctuaryModel`**: Reserva contigua que genera dinámicas fuente-sumidero emergentes (Fase IIA).
- **`FilterCorridorModel`**: Doble insularidad conectada por un corredor biológico — valida el efecto rescate en metapoblaciones (Fase IIB).

### `visualize.py`

Interfaz interactiva del simulador mediante componentes reactivos de **Solara** y **Altair/Vega-Lite**:

- **`GridView()`**: Scatter plot que mapea dinámicamente el espacio 2D y la posición de los agentes.
- **`PopulationChart()`**: Serie temporal interactiva de las poblaciones N(t).
- **`Page()`**: Componente raíz que integra los controles, la grid y el gráfico.

### `beyond_lotka_volterra.ipynb`

Documento central del TFG. Integra la narrativa teórica, los experimentos por fases, los componentes Solara incrustados y el análisis estadístico con `batch_run`. Organizado en:

- **Fase IA**: Modelo análogo a Lotka-Volterra — estocasticidad y extinción
- **Fase IB**: Regulación logística y paradoja del enriquecimiento
- **Fase IIA**: Fragmentación del hábitat y estructura espacial
- **Fase IIB**: Metapoblaciones y corredores ecológicos

---

## Tecnologías Utilizadas

| Paquete | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje base |
| [Mesa](https://mesa.readthedocs.io) | 3.0+ | Framework ABM |
| [Solara](https://solara.dev) | 1.57+ | Dashboard interactivo reactivo |
| [Altair](https://altair-viz.github.io) | 6.0+ | Visualización Vega-Lite |
| Pandas | 2.0+ | Análisis y procesamiento de datos |
| pyarrow | — | Backend eficiente para Altair + Solara |
| vegafusion | — | Compatibilidad Altair-Solara |
| Voilà | 0.5+ | Servidor de notebook como aplicación web |
| JupyterLab | 4.0+ | Entorno de desarrollo |

---

## Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/Manteca24/beyond_lotka_volterra.git
cd beyond_lotka_volterra
```

### 2. Crear el entorno virtual

```bash
python3 -m venv tfg-env
source tfg-env/bin/activate        # macOS / Linux
# tfg-env\Scripts\activate         # Windows
```

### 3. Instalar dependencias

```bash
pip install mesa solara altair pandas pyarrow vegafusion jupyterlab voila
```

### 4. Ejecutar el notebook

```bash
jupyter lab beyond_lotka_volterra.ipynb
```

> **Nota:** Las celdas de Solara requieren ejecutar el notebook completo en orden. Si el kernel está limpio, ejecuta *Run All* antes de interactuar con los dashboards.

### 5. Dashboard Solara standalone

```bash
solara run visualize.py
```

### 6. Regenerar las gráficas de la web

```bash
# Desde la raíz del proyecto (TFG/)
python3 web/export_charts.py
```

---

## Fases de Simulación

| Fase | Nombre | Modelo | Pregunta central |
|---|---|---|---|
| **IA** | Modelo clásico estocástico | `LotkaVolterraModel` | ¿La estocasticidad rompe el equilibrio de LV? |
| **IB** | Regulación y paradoja del enriquecimiento | `LogisticHollingModel` | ¿Más recursos implica más estabilidad? |
| **IIA** | Fragmentación del hábitat | `RefugeModel` / `SanctuaryModel` | ¿Importa la geometría del refugio? |
| **IIB** | Corredores y metapoblaciones | `FilterCorridorModel` | ¿Puede el corredor revertir la extinción local? |

---

## Web Narrativa

La carpeta `web/` contiene una página HTML autocontenida que narra los resultados del TFG con gráficas Altair interactivas y el GIF de la simulación. Diseñada para incluirse como enlace en la memoria.

Para actualizarla tras modificar los modelos:

```bash
python3 web/export_charts.py   # regenera los JSON de Vega-Lite
# index.html se actualiza automáticamente
```

---

*Trabajo Fin de Grado en Biología · Universidad de Málaga · Junio 2026*

&copy; 2026 María Agostina Zavia Martínez. Todos los derechos reservados.

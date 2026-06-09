Copyright © 2026 Agostina Zavia Martínez. All rights reserved.

# Más allá de Lotka-Volterra: Impacto de la estocasticidad y la estructura del paisaje en la extinción de especies mediante Modelos Basados en Individuos

Este repositorio contiene el código fuente, la documentación algorítmica y las simulaciones desarrolladas para el Trabajo de Fin de Grado (TFG) en Biología de la Universidad de Málaga. El proyecto contrasta las predicciones deterministas del modelo clásico de Lotka-Volterra con modelos estocásticos espacialmente explícitos (MBI), explorando el impacto de la fragmentación del hábitat, las trampas ecológicas y la viabilidad metapoblacional de los corredores ecológicos.

🌐 **Web interactiva (GitHub Pages):** [manteca24.github.io/beyond_lotka_volterra](https://manteca24.github.io/beyond_lotka_volterra/)  
☁️ **Simulador en la Nube (Hugging Face):** [manteca24/beyond-lotka-volterra](https://huggingface.co/spaces/manteca24/beyond-lotka-volterra)

---

## Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

```text
TFG/
├── agent.py                     ← Lógica de comportamiento de los agentes (presas y depredadores)
├── model.py                     ← Topologías y dinámicas poblacionales del entorno (ABM)
├── visualize.py                 ← Dashboard interactivo (Solara + Altair)
├── beyond_lotka_volterra.ipynb  ← Notebook central del TFG (experimentos y análisis de datos)
├── protocolo_ODD.md             ← Descripción estandarizada del modelo computacional
├── bibliografia.md              ← Referencias bibliográficas empleadas en la investigación
├── hf_space/                    ← Archivos de despliegue para Hugging Face (Dockerfile, requirements)
└── docs/                        ← Web estática desplegada en GitHub Pages (HTML, CSS, JSONs)
```

### Protocolo ODD y Bibliografía
- **`protocolo_ODD.md`**: Siguiendo el estándar internacional ODD (*Overview, Design concepts, Details*), este documento detalla la arquitectura orientada a objetos de la simulación, los parámetros de inicialización y el flujo de ejecución (Scheduling) para garantizar su reproducibilidad algorítmica.
- **`bibliografia.md`**: Recopilación de todos los artículos, libros y fuentes de código utilizadas como base teórica y técnica del proyecto.

### Módulos Principales (`agent.py` y `model.py`)
Contienen las clases que definen el comportamiento microscópico (agentes con respuesta funcional tipo II de Holling, metabolismo y capacidad reproductiva) y el comportamiento macroscópico del paisaje (topologías en cuadrícula, límites reflectantes/toroidales, parches de refugio y corredores ecológicos).

### Interfaz Gráfica (`visualize.py`)
Contiene los componentes reactivos construidos con **Solara** y **Altair** que generan los *dashboards* interactivos. Permiten la manipulación en tiempo real de los parámetros ecológicos ($\alpha$, $\delta$, $K$) y la visualización de los frentes de onda espaciales.

---

## Modos de Ejecución

El proyecto está diseñado para poder ejecutarse tanto en un entorno local (para desarrollo riguroso) como en producción (para su lectura y demostración pública).

### 1. Ejecución en Producción (La Web y la Nube)

La forma más sencilla de experimentar el proyecto es a través de su despliegue público, que no requiere instalación alguna:
- **[La Web Narrativa](https://manteca24.github.io/beyond_lotka_volterra/)**: La carpeta `docs/` contiene el código fuente de la página web narrativa del TFG. Está desplegada automáticamente mediante **GitHub Pages**.
- **Simulador en la Nube**: Dentro de la web, hay varios paneles interactivos de experimentación incrustados mediante *Iframes*. El archivo `visualize.py` corre de forma permanente dentro de un contenedor Docker alojado en **Hugging Face Spaces**. La web se conecta directamente a este servidor para ofrecer la interactividad.

### 2. Ejecución Local (Desarrollo)

Si deseas clonar el proyecto para analizar los datos en profundidad, correr el Notebook o alterar el código fuente en tu máquina:

```bash
git clone https://github.com/Manteca24/beyond_lotka_volterra.git
cd beyond_lotka_volterra

# Crear y activar entorno virtual
python3 -m venv tfg-env
source tfg-env/bin/activate        # macOS / Linux

# Instalar dependencias
pip install mesa solara altair pandas pyarrow jupyterlab
```

#### Analizar el Notebook de Jupyter
El archivo `beyond_lotka_volterra.ipynb` contiene todo el análisis estadístico ejecutado en bloque (con la clase `batch_run` de Mesa).
```bash
jupyter lab beyond_lotka_volterra.ipynb
```

#### Correr el Servidor Solara en Local
Si quieres levantar el simulador en tu propio ordenador (ideal si quieres probar cambios en el código visual de inmediato):
```bash
solara run visualize.py
```
> **Nota de desarrollo web:** Si quieres probar la web localmente abriendo `docs/index.html` y que además se comunique con tu servidor local en vez del de Hugging Face, abre `docs/index.html`, busca el script en la etiqueta `<head>`, comenta la constante `SIM_ENV_URL` apuntada a la nube y descomenta la que apunta a `http://localhost:8765`.

---

## Fases de Simulación

| Fase | Nombre | Modelo en código | Pregunta central |
|---|---|---|---|
| **IA** | Lotka-Volterra Estocástico | `LotkaVolterraModel` | ¿La estocasticidad demográfica rompe el equilibrio de LV? |
| **IB** | Capacidad de Carga y Saciedad | `LogisticHollingModel` | ¿Más recursos implica mayor resiliencia? (Paradoja del Enriquecimiento) |
| **IIA** | Fragmentación del Hábitat | `RefugeModel` / `SanctuaryModel` | ¿Importa la distribución topológica del refugio espacial? |
| **IIB** | Corredores Ecológicos | `FilterCorridorModel` | ¿Puede un corredor biológico rescatar subpoblaciones en extinción? |

---

*Trabajo Fin de Grado en Biología · Universidad de Málaga · Junio 2026*

&copy; 2026 María Agostina Zavia Martínez. Todos los derechos reservados.

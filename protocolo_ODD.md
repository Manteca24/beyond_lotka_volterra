# ANEXO A: Descripción computacional del MBI (Protocolo ODD)

La descripción metodológica del texto principal justifica las decisiones ecológicas del modelo. Este anexo complementa dicha información detallando la arquitectura computacional, los parámetros de inicialización y el flujo de ejecución (Scheduling), siguiendo el estándar ODD (Grimm et al., 2010) para garantizar la reproducibilidad algorítmica.

## 1. Jerarquía de Clases (Arquitectura Orientada a Objetos)

El ecosistema se ha programado en Python utilizando el framework Mesa 3.0, empleando herencia de clases para evitar redundancias y modularizar los experimentos:

### Eje Espacial (Modelos)
- **`LotkaVolterraModel`**: Clase base. Genera el grid toroidal (`MultiGrid`) y el `DataCollector`. Instancia a agentes estocásticos simples.
- **`LogisticHollingModel`**: Añade el cálculo dinámico de la Capacidad de Carga ($K$) y el modo de control espacial (`use_global_k = True/False`). Introduce a los agentes paradójicos o metabólicos estándar.
- **`RefugeModel`**: Hereda de `LogisticHollingModel`. Añade la generación probabilística de refugios ecológicos, creando una lista de coordenadas (`refuge_cells`) inaccesibles para depredadores mediante el parámetro `refuge_density`.
- **`SanctuaryModel`**: Hereda de `LogisticHollingModel`. Sobrescribe la topología para dibujar una estructura fija de santuario contiguo en un porcentaje de la matriz (`refuge_width_pct`), en lugar de distribución aleatoria.
- **`FilterCorridorModel`**: Instancia un grid más amplio (30x30). Dibuja dos islas de hábitat (parches de 5x5) y permite la activación de un corredor diagonal biológico (`corridor_active`).

### Eje Biológico (Agentes)
- **`SimplePrey` / `SimplePredator`**: Agentes probabilísticos base sin estado interno (sin seguimiento de energía). Su supervivencia y reproducción dependen exclusivamente de un factor de azar ($\alpha$ y $\delta$).
- **`ParadoxPrey` / `ParadoxPredator`**: Agentes con restricciones termodinámicas (energía) y una respuesta funcional de tipo II de Holling simulada mediante `handling_time_remaining`, la cual les impide seguir cazando durante un periodo de digestión tras cada captura.
- **`Prey` / `Predator`**: Agentes metabólicos completos con restricción de encuentro sexual. La reproducción evalúa la presencia de coespecíficos en la vecindad de Moore (`partners`).
- **`MountainPrey` / `TerritorialPredator`**: Incorporan funciones de visión espacial condicionada. `MountainPrey` prefiere celdas de refugio (95% de preferencia) y sufre altísima mortalidad fuera de ellas. `TerritorialPredator` restringe su caza a las islas de hábitat en entornos complejos.
- **`RefugePredator`**: Clase heredada que restringe estrictamente sus movimientos, verificando siempre `pos not in self.model.refuge_cells` antes de avanzar.

## 2. Parametrización y Condiciones Iniciales

A menos que se indique lo contrario en el diseño experimental específico de cada fase, los mundos simulados se inicializan con los siguientes valores base:

| Parámetro | Variable en Código | Valor Estándar | Función Computacional |
| :--- | :--- | :--- | :--- |
| **Dimensión del Grid** | `width`, `height` | `15 x 15` (Fases I y IIA) / `30 x 30` (Fase IIB) | Define celdas de simulación. `MultiGrid(torus=True)` |
| **Pob. Inicial Presas** | `N_prey` | `80` (Fase I/IIA) / `50` (Fase IIB) | Agentes inyectados aleatoriamente en $t=0$. |
| **Pob. Inicial Depred.** | `N_predator` | `25` (Fase I/IIA) / `8` (Fase IIB) | Agentes inyectados aleatoriamente en $t=0$. |
| **Energía Inicial (P/D)** | `self.energy` | `10` / `20` (Territoriales: `60`) | Reservas termodinámicas iniciales al instanciarse. |
| **Crecimiento (Presas)** | `alpha_prey_growth` | `0.05` a `0.6` | Probabilidad de reproducción o clonación. |
| **Asimilación (Depred.)** | `delta` / `delta_predator_gain` | `5` a `40` | Energía obtenida por cada presa cazada (`remove()`). |
| **Metabolismo Basal** | `self.energy -= n` | `1` (Estándar) / `2` (Territorial) | Resta de energía incondicional en cada *step*. |
| **Coste Reproductivo** | `self.energy -= n` | `-15` (Predator) / `-100` (Territorial) | Deducción energética equitativa a ambos progenitores. |
| **Límite Energético** | `self.energy > n` | `30` (Predator) / `250` (Territorial) | Umbral mínimo para activar la búsqueda de pareja. |
| **Tiempo Manipulación** | `handling_time_remaining`| `1` a `n` pasos | Tiempo de inactividad obligatoria tras la ingesta. |

## 3. Proceso y Planificación (Secuencia del *Step*)

El motor de Mesa no resuelve las acciones simultáneamente, sino mediante un activador asíncrono aleatorio. En cada paso global del modelo, el motor invoca `self.agents.shuffle_do("step")`, desordenando aleatoriamente la lista de agentes antes de que ejecuten su turno para evitar sesgos de precedencia espacial.

La vida de un agente complejo (ej. `TerritorialPredator`) en un paso discreto ($t \rightarrow t+1$) sigue estrictamente este árbol de decisión interno:

1. **Localización (Check de Presencia):** Verifica si sigue vivo (`if self.pos is None: return`). Esto evita excepciones lógicas si un depredador fue asesinado o una presa ya fue cazada en el mismo *step* por otro agente precedente.
2. **Navegación (Movement):** Identifica celdas adyacentes válidas usando `get_neighborhood(moore=True, include_center=False)`. Filtra restricciones geográficas estructurales (ej. refugios inaccesibles para el depredador) y selecciona una celda estocásticamente (`random.choice()`) para invocar `move_agent()`.
3. **Metabolismo Basal:** Deduce el coste basal incondicional de vivir el paso de tiempo actual (-2 unidades en agentes territoriales, -1 en estándar). 
4. **Respuesta Funcional (Caza):** Escanea los contenidos de su celda actual tras moverse (`get_cell_list_contents([self.pos])`). Si detecta objetos que heredan de la clase `Prey`, elimina solamente a uno del modelo (`remove_agent`) y asimila su valor energético o probabilístico (`delta`).
5. **Inanición (Starvation):** Si tras el metabolismo y la posible caza la energía cae por debajo del umbral mínimo de mantenimiento celular (`self.energy <= 0`), el agente invoca su propia destrucción y se remueve del grid.
6. **Apareamiento Sensible (Mating):** Si la energía supera el altísimo umbral reproductivo fijado, escanea su vecindad de Moore incluyendo la propia celda (`include_center=True`). Si detecta un coespecífico viable y que no sea él mismo (`isinstance(obj, self.__class__) and obj is not self`), deduce la energía reproductiva masiva compartida a ambos individuos y llama a `model.grid.place_agent(baby, self.pos)` para instanciar a la descendencia de forma inmediata.

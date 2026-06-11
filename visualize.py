import solara
import pandas as pd
import altair as alt
alt.data_transformers.disable_max_rows()

# Dark theme removed

import numpy as np
import time
import threading
import warnings
import traceback
import random
from model import LotkaVolterraModel, LogisticHollingModel, FilterCorridorModel
from agent import Prey, Predator



# Variables de usuario para parámetros de entrada
init_prey = solara.reactive(50)
init_predator = solara.reactive(20)
alpha_growth = solara.reactive(0.1)
delta_gain = solara.reactive(5.0)

# Instanciación del objeto contenedor ecológico (dimensión inicial 20x20)
model = solara.reactive(LotkaVolterraModel(
    N_prey=init_prey.value, 
    N_predator=init_predator.value, 
    width=20, 
    height=20,
    alpha=alpha_growth.value,
    delta=delta_gain.value,
    gamma=0.1
))

# Variable discreta para conteo temporal
step_count = solara.reactive(0)

# Bandera booleana de ejecución continua
is_running = solara.reactive(False)

def perform_step():
    if model.value.running:
        model.value.step()
        step_count.value += 1
    else:
        is_running.value = False

def reset_model():
    model.value = LotkaVolterraModel(
        N_prey=init_prey.value, 
        N_predator=init_predator.value, 
        width=20, 
        height=20,
        alpha=alpha_growth.value,
        delta=delta_gain.value,
        gamma=0.1
    )
    step_count.value = 0
    is_running.value = False

@solara.component
def GridView():
    _ = step_count.value 
    
    m = model.value
    
    data = []
    for agent in m.agents:
        agent_type = "Prey" if isinstance(agent, Prey) else "Predator"
        
        data.append({
            "x": agent.pos[0], 
            "y": agent.pos[1], 
            "Agent Type": agent_type
        })
    
    if not data:
        return solara.Markdown("### 💀 Extinción Poblacional")

    df = pd.DataFrame(data)

    chart = alt.Chart(df).mark_circle(size=120, opacity=0.8).encode(
        # Topología Horizontal
        x=alt.X("x", axis=alt.Axis(title="Variable X"), scale=alt.Scale(domain=[-0.5, m.grid.width-0.5])),
        # Topología Vertical
        y=alt.Y("y", axis=alt.Axis(title="Variable Y"), scale=alt.Scale(domain=[-0.5, m.grid.height-0.5])),
        # Representación Cromática Taxonómica
        color=alt.Color("Agent Type", scale=alt.Scale(domain=["Prey", "Predator"], range=["#2ca02c", "#d62728"]))
    ).properties(
        width=450, 
        height=450, 
        # Título dinámico estocástico
        title=f"Estado del Sistema Ecológico (Ticks: {step_count.value})"
    )
    
    spec = chart.to_dict()
    solara.widgets.VegaLite.element(spec=spec)

@solara.component
def PopulationChart():
    _ = step_count.value
    m = model.value
    df = m.datacollector.get_model_vars_dataframe()
    
    if df.empty:
        return solara.Markdown("_Iniciando registro censal de población..._")

    df = df.reset_index().rename(columns={"index": "Step"})
    
    chart = alt.Chart(df).transform_fold(
        ["Prey", "Predator"],
        as_=["Species", "Count"]
    ).mark_line(strokeWidth=3).encode(
        x="Step:Q", 
        y="Count:Q",
        color=alt.Color("Species:N", scale=alt.Scale(domain=["Prey", "Predator"], range=["#2ca02c", "#d62728"]))
    ).properties(
        width=450, 
        height=200,
        title="Dinámica de Componentes Biológicos"
    )

    spec = chart.to_dict()
    solara.widgets.VegaLite.element(spec=spec)

@solara.component
def Page():
    """
    Aplicativo raíz del frontal del simulador (Página Web Interactiva principal).
    
    Funcionalmente ejecuta tres procesos:
    1. Declara un subproceso subyacente (`solara.use_thread`) para alimentar automáticamente 
       el reloj biológico cuando el boolean 'Play/Pausa' es modificado (`is_running`).
    2. Construye modularmente un Panel Lateral (Sidebar) de experimentación iterativa para 
       manipular variables biométricas sin necesidad de recompilar en el terminal.
    3. Construye el Dashboard central (Viewport) donde ensambla el plano espacial y demográfico.
    """
    
    # Ciclo estructurado en sub-proceso asincrónico
    def runner():
        while is_running.value:
            perform_step()      
            time.sleep(0.1)     
            
    result = solara.use_thread(runner, dependencies=[is_running.value])

    # Ensamblaje modular del marco reactivo
    solara.Title("Simulación: Lotka-Volterra vs Realidad Estocástica")
    
    with solara.Columns([4, 8]):
        with solara.Card(title="Control de Variables de Lotka-Volterra", margin=10, elevation=2):
            solara.Markdown("___Parámetros Demográficos___")
            solara.SliderInt(label="Nº Presas Inicial", value=init_prey, min=10, max=200)
            solara.SliderInt(label="Nº Depredadores Inicial", value=init_predator, min=2, max=100)
            
            solara.Markdown("___Parámetros Ecológicos___")
            solara.SliderFloat(label="Tasa Crecimiento Presa (α)", value=alpha_growth, min=0.01, max=1.0, step=0.05)
            solara.SliderFloat(label="Ganancia Depredador (δ)", value=delta_gain, min=1.0, max=25.0, step=1.0)
            
            solara.Markdown("""
            *(Nota: El cambio de parámetros requiere de un Reinicio Estocástico para hacer efecto).*
            """)

        with solara.Column(align="center"): 
            solara.Markdown("### Componente Predictivo Ecuacional de la Interacción Individual")
            
            with solara.Row(justify="center", gap="1em", style={"margin-bottom": "2em"}):
                def toggle_play():
                    is_running.value = not is_running.value
                    
                solara.Button("▶ Iniciar" if not is_running.value else "⏸ Pausa", on_click=toggle_play, color="primary")
                solara.Button("Tick ⏭", on_click=perform_step)
                solara.Button("Reinicio Estocástico ↺", on_click=reset_model, color="grey")

            with solara.Row(justify="space-between", style={"flex-wrap": "wrap", "justify-content": "center", "gap": "20px"}):
                with solara.Column(align="center"):
                    GridView()
                with solara.Column(align="center"):
                    PopulationChart()
                    solara.Markdown("""
                    **Guía de Interpretación:**
                    1. Inicializar iteración estocástica.
                    2. Visualizar perturbaciones probabilísticas.
                    3. Identificar picos poblacionales liminales de $N_t = 0$. 
                    
                    A diferencia del determinismo analítico, que predice oscilaciones incesantes, 
                    la estocasticidad interaccional local empujará iterativamente el marco 
                    hacia extinciones inexorables por ruido demográfico.
                    """)


# Variable de estado global
semilla_multiverso = solara.reactive(0) 

@solara.component
def EstocasticidadDemoFaseIA():
    semilla_actual = semilla_multiverso.value  
    
    # 1. ENCAPSULAMOS LA SIMULACIÓN EN UNA FUNCIÓN PURA
    def correr_simulacion():
        modelo = LotkaVolterraModel(
            N_prey=80, N_predator=10, width=20, height=20, 
            alpha=0.08, delta=0.4, gamma=0.1,
            seed=semilla_actual
        )
        
        for _ in range(200):
            if modelo.running:
                modelo.step()
            else:
                break
                
        df = modelo.datacollector.get_model_vars_dataframe().reset_index().rename(columns={"index": "Tiempo"})
        df_melt = df.melt(id_vars=["Tiempo"], value_vars=["Prey", "Predator"],
                          var_name="Especie", value_name="Población")
        return df, df_melt

    # 2. SOLARA.USE_MEMO: Solo ejecuta 'correr_simulacion' cuando cambia 'semilla_actual'
    df, df_melt = solara.use_memo(correr_simulacion, dependencies=[semilla_actual])
    
    # Renderizado de la gráfica usando el DataFrame fresco
    chart_time = alt.Chart(df_melt).mark_line(strokeWidth=2.5, point=True).encode(
        x=alt.X("Tiempo:Q", title="Tiempo (Ciclos)"), 
        y=alt.Y("Población:Q", title="Número de Individuos"),
        color=alt.Color("Especie:N", scale=alt.Scale(domain=["Prey", "Predator"], range=["blue", "#d62728"]))
    ).properties(
        width=380, 
        height=300, 
        title=f"Evolución Temporal"
    )

    trayectoria_fases = alt.Chart(df).mark_line(strokeWidth=2, opacity=0.8, color="purple").encode(
        x=alt.X("Prey:Q", title="Población de Presas"),
        y=alt.Y("Predator:Q", title="Población de Depredadores"),
        order=alt.Order("Tiempo:Q", sort="ascending")
    )
    
    punto_final = alt.Chart(df.iloc[[-1]]).mark_circle(size=150, color="black").encode(
        x="Prey:Q",
        y="Predator:Q"
    )

    chart_phase = (trayectoria_fases + punto_final).properties(
        width=380, 
        height=300, 
        title=f"Espacio de Fases (Semilla: #{semilla_actual})"
    )
    
    # Interfaz de Usuario
    with solara.Column(align="center"):
        solara.Markdown("### Lotka-Volterra estocástico")
        
        solara.Button(
            "🎲 Generar Nuevo Universo (Estocástico)", 
            on_click=lambda: semilla_multiverso.set(semilla_multiverso.value + 1), 
            color="success"
        )
        
        with solara.Row(gap="20px", style={"flex-wrap": "wrap", "justify-content": "center"}):
            solara.FigureAltair(chart_time)
            solara.FigureAltair(chart_phase)



# Variable de estado global
semilla_multiverso = solara.reactive(0) 

@solara.component
def EstocasticidadDemoFaseIB():
    semilla_actual = semilla_multiverso.value  
    
    # 1. ENCAPSULAMOS LA SIMULACIÓN EN UNA FUNCIÓN PURA
    def correr_simulacion():
        modelo = LogisticHollingModel(
            N_prey=120, N_predator=15, width=35, height=35,
            alpha=0.08, delta=3,
            k_local=2,
            seed=semilla_actual
        )

        for _ in range(600):
            if modelo.running:
                modelo.step()
            else:
                break
                
        df = modelo.datacollector.get_model_vars_dataframe().reset_index().rename(columns={"index": "Tiempo"})
        df_melt = df.melt(id_vars=["Tiempo"], value_vars=["Prey", "Predator"],
                          var_name="Especie", value_name="Población")
        return df, df_melt

    # 2. SOLARA.USE_MEMO: Solo ejecuta 'correr_simulacion' cuando cambia 'semilla_actual'
    df, df_melt = solara.use_memo(correr_simulacion, dependencies=[semilla_actual])
    
    # Renderizado de la gráfica usando el DataFrame fresco
    chart_time = alt.Chart(df_melt).mark_line(strokeWidth=2.5, point=True).encode(
        x=alt.X("Tiempo:Q", title="Tiempo (Ciclos)"), 
        y=alt.Y("Población:Q", title="Número de Individuos"),
        color=alt.Color("Especie:N", scale=alt.Scale(domain=["Prey", "Predator"], range=["blue", "#d62728"]))
    ).properties(
        width=380, 
        height=300, 
        title=f"Evolución Temporal"
    )

    trayectoria_fases = alt.Chart(df).mark_line(strokeWidth=2, opacity=0.8, color="purple").encode(
        x=alt.X("Prey:Q", title="Población de Presas"),
        y=alt.Y("Predator:Q", title="Población de Depredadores"),
        order=alt.Order("Tiempo:Q", sort="ascending")
    )
    
    punto_final = alt.Chart(df.iloc[[-1]]).mark_circle(size=150, color="black").encode(
        x="Prey:Q",
        y="Predator:Q"
    )

    chart_phase = (trayectoria_fases + punto_final).properties(
        width=380, 
        height=300, 
        title=f"Espacio de Fases (Semilla: #{semilla_actual})"
    )
    
    # Interfaz de Usuario
    with solara.Column(align="center"):
        solara.Markdown("### Lotka-Volterra con capacidad de carga y respuesta funcional tipo II (Holling)")
        
        solara.Button(
            "🎲 Generar Nuevo Universo (Estocástico)", 
            on_click=lambda: semilla_multiverso.set(semilla_multiverso.value + 1), 
            color="success"
        )
        
        with solara.Row(gap="20px", style={"flex-wrap": "wrap", "justify-content": "center"}):
            solara.FigureAltair(chart_time)
            solara.FigureAltair(chart_phase)


# Un panel de control reactivo que permite ajustar parámetros ecológicos,
# simular la dinámica espacial en tiempo real 


warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Variables de Parámetros Modificables (Reactivos) ---
n_prey_init = solara.reactive(80)
n_pred_init = solara.reactive(10)
alpha_growth = solara.reactive(0.08)
delta_conversion = solara.reactive(3)
grid_dim = solara.reactive(55)

# --- Estado de la Simulación ---
model_state_lab = solara.reactive(LogisticHollingModel(N_prey=120, N_predator=15, width=35, height=35, alpha=0.08, delta=3, k_local=2))
model_state_lab.value.random = random.Random(42)

step_count_lab = solara.reactive(0)
is_running_lab = solara.reactive(False)
current_seed_lab = solara.reactive(42)

def build_new_model_lab():
    """Crea un modelo nuevo con los parámetros de los deslizadores."""
    seed = random.randint(1, 10000)
    current_seed_lab.value = seed
    
    new_model = LogisticHollingModel(
        N_prey=n_prey_init.value, 
        N_predator=n_pred_init.value, 
        width=grid_dim.value, 
        height=grid_dim.value, 
        alpha=alpha_growth.value, 
        delta=delta_conversion.value
    )
    new_model.random = random.Random(seed)
    
    model_state_lab.value = new_model
    step_count_lab.value = 0
    is_running_lab.value = False
def perform_step_lab():
    """Avanza la simulación un paso de forma manual."""
    mod = model_state_lab.value
    if mod.running:
        mod.step()
        step_count_lab.value += 1
    else:
        is_running_lab.value = False



# --- Gráfico Altair para el visualizador ---
def get_chart_lab():
    mod = model_state_lab.value
    
    # --- ACOPLAMIENTO DE DIMENSIONES SEGURO ---
    # Evita que el gráfico cambie de tamaño antes de aplicar los parámetros de los deslizadores
    current_width = mod.grid.width
    current_height = mod.grid.height
    total_cells = current_width * current_height
    
    prey_data = []
    pred_data = []
    n_presas = 0
    n_depredadores = 0
    
    for a in mod.agents:
        if a.pos is not None:
            name = a.__class__.__name__
            if "Predator" in name:
                n_depredadores += 1
                pred_data.append({"x": a.pos[0], "y": a.pos[1], "Especie": "Depredador", "Tamaño": 60})
            elif "Prey" in name:
                n_presas += 1
                prey_data.append({"x": a.pos[0], "y": a.pos[1], "Especie": "Presa", "Tamaño": 25})
                
    df_prey = pd.DataFrame(prey_data) if prey_data else pd.DataFrame(columns=["x", "y", "Especie", "Tamaño"])
    df_pred = pd.DataFrame(pred_data) if pred_data else pd.DataFrame(columns=["x", "y", "Especie", "Tamaño"])
    df_total = pd.concat([df_prey, df_pred], ignore_index=True) if (prey_data or pred_data) else pd.DataFrame(columns=["x", "y", "Especie", "Tamaño"])
    
    all_occupied = set([(d["x"], d["y"]) for d in prey_data + pred_data])
    empty_pct = (total_cells - len(all_occupied)) / total_cells if total_cells > 0 else 0
    
    dots = alt.Chart(df_total).mark_point(
        filled=True,
        stroke="black",
        strokeWidth=0.4
    ).encode(
        x=alt.X("x:Q", title="Coordenada X (Espacio)", scale=alt.Scale(domain=[-1, current_width])),
        y=alt.Y("y:Q", title="Coordenada Y (Espacio)", scale=alt.Scale(domain=[-1, current_height])),
        color=alt.Color("Especie:N", scale=alt.Scale(
            domain=["Presa", "Depredador"],
            range=["blue", "#d62728"]
        ), legend=alt.Legend(title="Especies", orient="right")),
        size=alt.Size("Tamaño:Q", scale=None),
        tooltip=["Especie:N", "x:Q", "y:Q"]
    )
    
    chart = dots.properties(
        width=400,
        height=400,
        background="white",
        title=alt.TitleParams(
            text=f"Paso: {step_count_lab.value} | Semilla: {current_seed_lab.value}",
            subtitle=[
                f"Presas: {n_presas} | Depredadores: {n_depredadores} | Espacio Vacío: {empty_pct*100:.1f}%",
            ],
            fontSize=14,
            subtitleFontSize=10,
            anchor="middle",
            offset=10
        )
    )
    return chart

# --- Layout y Renderizado del Dashboard ---
@solara.component
def Dashboard():
    def runner():
        while is_running_lab.value:
            perform_step_lab()
            time.sleep(0.12)
            
    solara.use_thread(runner, dependencies=[is_running_lab.value])
    
    def toggle_play():
        is_running_lab.value = not is_running_lab.value


    with solara.Card(margin=10, elevation=3):
        with solara.Column(align="center", style={"width": "100%"}):
            solara.Markdown("### Laboratorio Espacial y Generador de Dinámica Trófica (Durrett-Levin)")
        # El uso de solara.Columns([4, 8]) asegura un layout de rejilla fijo al 33% / 66%
        # sin peligro de colapso o ensanchamientos repentinos al interactuar con deslizadores.
        with solara.Columns([4, 8]):
            
            # Columna Izquierda: Parámetros del Ecosistema (Usamos Cards nativas sin backgrounds forzados 
            # para que hereden el tema de Jupyter Light/Dark correctamente y evitar letras blancas sobre blancas)
            with solara.Card(title="⚙️ Parámetros del Ecosistema", elevation=1):
                solara.SliderInt("Presas Iniciales", value=n_prey_init, min=10, max=300)
                solara.SliderInt("Depredadores Iniciales", value=n_pred_init, min=2, max=50)
                solara.SliderFloat("Crecimiento Presa (alpha)", value=alpha_growth, min=0.01, max=0.20, step=0.01)
                solara.SliderInt("Energía Conversión (delta)", value=delta_conversion, min=1, max=10)
                solara.SliderInt("Tamaño del Mapa (N x N)", value=grid_dim, min=10, max=80)
                
                solara.Button(
                    "↺ Aplicar y Reiniciar", 
                    on_click=build_new_model_lab,
                    color="warning",
                    style="margin-top: 15px; width: 100%;"
                )
                
            
            # Columna Derecha: Simulación e Interfaz Gráfica
            with solara.Column(align="center"):
                with solara.Row(gap="15px", justify="center", style={"margin-bottom": "12px", "flex-wrap": "wrap"}):
                    solara.Button(
                        "▶ Play" if not is_running_lab.value else "⏸ Pausa", 
                        on_click=toggle_play, 
                        color="success" if not is_running_lab.value else "warning"
                    )
                    solara.Button(
                        "⏭ Paso Individual", 
                        on_click=perform_step_lab
                    )
                
                solara.FigureAltair(get_chart_lab())





warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Estado Reactivo Global ---
model_f2 = solara.reactive(FilterCorridorModel(N_prey=50, N_predator=8, corridor_active=False))
step_count_f2 = solara.reactive(0)
is_running_f2 = solara.reactive(False)
use_corridor = solara.reactive(False)



def reset_model_f2():
    is_running_f2.value = False
    model_f2.value = FilterCorridorModel(
        N_prey=50, N_predator=8,
        corridor_active=use_corridor.value
    )
    step_count_f2.value = 0

def on_scenario_change(value):
    reset_model_f2()

# --- Visualización ---
def get_chart_f2():
    mod = model_f2.value        # auto-suscripción a model
    s   = step_count_f2.value   # auto-suscripción a step_count_f2

    hab_data = []
    for (x, y) in mod.refuge_cells:
        tipo = "Isla (Bosque)" if (x, y) in mod.island_cells else "Corredor (Paso)"
        hab_data.append({"x": x, "y": y, "Hábitat": tipo})

    ag_data, n_presas, n_depredadores = [], 0, 0
    for a in mod.agents:
        if a.pos:
            name = a.__class__.__name__
            if "Predator" in name:
                tipo, n_depredadores = "Depredador", n_depredadores + 1
            elif "Prey" in name:
                tipo, n_presas = "Presa", n_presas + 1
            else:
                continue
            ag_data.append({"x": a.pos[0], "y": a.pos[1], "Agente": tipo})

    df_hab = pd.DataFrame(hab_data)
    df_ag  = pd.DataFrame(ag_data) if ag_data else pd.DataFrame({'x': [], 'y': [], 'Agente': []})

    base = alt.Chart(df_hab).mark_square(size=140, opacity=0.4).encode(
        x=alt.X("x:O", axis=None),
        y=alt.Y("y:O", sort="descending", axis=None),
        color=alt.Color("Hábitat", scale=alt.Scale(range=['#006400', '#32CD32']), legend=None)
    )
    dots = alt.Chart(df_ag).mark_circle(size=120, opacity=1).encode(
        x="x:O", y="y:O",
        color=alt.Color("Agente", scale=alt.Scale(domain=['Presa', 'Depredador'], range=['blue', 'red']))
    )
    return (base + dots).resolve_scale(color='independent').properties(
        width=400, height=400,
        title=f"Paso: {s} | Presas: {n_presas} | Depredadores: {n_depredadores}"
    )

def perform_step_f2():
    if model_f2.value.running:
        model_f2.value.step()
        step_count_f2.value += 1
    else:
        is_running_f2.value = False

# --- Componente Principal ---
@solara.component
def PageFase2():
    def runner():
        while is_running_f2.value:
            perform_step_f2()
            time.sleep(0.2)
            
    solara.use_thread(runner, dependencies=[is_running_f2.value])
    
    def toggle_play():
        is_running_f2.value = not is_running_f2.value

    with solara.Column(align="center", gap="20px"):
        solara.Markdown("# Simulador de corredor ecológico ")

        with solara.Row(gap="10px", style={"flex-wrap": "wrap", "justify-content": "center"}):
            solara.Switch(label="Activar Corredor", value=use_corridor, on_value=on_scenario_change)
            solara.Button(
                "⏸ Pausa" if is_running_f2.value else "▶ Play",
                on_click=toggle_play, color="warning" if is_running_f2.value else "success"
            )
            solara.Button("⏭ Paso", on_click=perform_step_f2)
            solara.Button("↺ Reiniciar", on_click=reset_model_f2, color="warning")

        solara.FigureAltair(get_chart_f2())

        if use_corridor.value:
            solara.Success("Escenario CONECTADO: con corredor ecológico.")
        else:
            solara.Error("Escenario AISLADO")





from agent import SimplePrey, SimplePredator

class ExperimentalPrey(SimplePrey):
    def step(self):
        if self.pos is None: return
        self.move()
        
        prob_actual = self.model.alpha
        
        # A/B TEST: Límite Logístico (K)
        if getattr(self.model, 'activar_K', False):
            factor = max(0, 1 - (self.model.num_presas_actuales / self.model.K_limite))
            prob_actual *= factor
            
        if self.random.random() < prob_actual:
            baby = self.__class__(self.model)
            self.model.grid.place_agent(baby, self.pos)

class ExperimentalPredator(SimplePredator):
    def __init__(self, model):
        super().__init__(model)
        self.tiempo_digestion = 0

    def step(self):
        if self.pos is None: return
        
        # A/B TEST: Respuesta Funcional
        if getattr(self.model, 'activar_respuesta', False):
            if self.tiempo_digestion > 0:
                self.tiempo_digestion -= 1
                return 
                
        self.move()
        
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True)
        cellmates = self.model.grid.get_cell_list_contents(neighborhood)
        prey_list = [obj for obj in cellmates if isinstance(obj, SimplePrey)]
        
        if prey_list:
            victim = self.random.choice(prey_list)
            self.model.grid.remove_agent(victim)
            
            if hasattr(victim, 'remove'):
                victim.remove()
                
            if self.random.random() < self.model.delta:
                baby = self.__class__(self.model)
                self.model.grid.place_agent(baby, self.pos)
            
            if getattr(self.model, 'activar_respuesta', False):
                self.tiempo_digestion = self.model.tiempo_manejo
                
        elif self.random.random() < getattr(self.model, 'gamma', 0.1):
            self.model.grid.remove_agent(self)
            if hasattr(self, 'remove'):
                self.remove()

class ExperimentoModel(LotkaVolterraModel):
    def __init__(self, N_prey, N_predator, width, height, alpha, delta, gamma, 
                 activar_K=False, activar_respuesta=False, K_limite=800, tiempo_manejo=3):
        
        super().__init__(N_prey=0, N_predator=0, width=width, height=height, alpha=alpha, delta=delta, gamma=gamma)
        
        self.activar_K = activar_K
        self.activar_respuesta = activar_respuesta
        self.K_limite = K_limite
        self.tiempo_manejo = tiempo_manejo
        self.num_presas_actuales = N_prey 
        
        for _ in range(N_prey):
            a = ExperimentalPrey(self) 
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for _ in range(N_predator):
            a = ExperimentalPredator(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.num_presas_actuales = sum(1 for a in self.agents if isinstance(a, SimplePrey))
        if hasattr(super(), 'step'):
            super().step()
        else:
            self.agents.shuffle_do("step")

chk_K_val = solara.reactive(False)
chk_Resp_val = solara.reactive(False)
slide_K_val = solara.reactive(600)
slide_T_val = solara.reactive(2)
slide_Pasos_val = solara.reactive(300)
fase1_status = solara.reactive("")
fase1_chart = solara.reactive(None)

def generar_universo():
    fase1_status.value = "Calculando simulación con motor Mesa, por favor espera... ⏳"
    
    try:
        modelo = ExperimentoModel(
            N_prey=100, N_predator=30, width=40, height=40, 
            alpha=0.15, delta=0.25, gamma=0.05, 
            activar_K=chk_K_val.value, activar_respuesta=chk_Resp_val.value, 
            K_limite=slide_K_val.value, tiempo_manejo=slide_T_val.value
        )
        
        datos = []
        for t in range(slide_Pasos_val.value):
            modelo.step()
            presas = modelo.num_presas_actuales
            depredadores = sum(1 for a in modelo.agents if isinstance(a, ExperimentalPredator))
            
            datos.append({"Tiempo": t, "Poblacion": presas, "Especie": "Presas"})
            datos.append({"Tiempo": t, "Poblacion": depredadores, "Especie": "Depredadores"})
            
            if presas > 4000:
                fase1_status.value = f"⚠️ Población de presas explotó exponencialmente en el paso {t}. Freno de seguridad."
                break
            if presas == 0 and depredadores == 0:
                fase1_status.value = f"☠️ Extinción total del sistema en el paso {t}."
                break
                
        df = pd.DataFrame(datos)
        
        titulo_grafica = "Fase IA: Lotka-Volterra Teórico"
        if chk_K_val.value and not chk_Resp_val.value: titulo_grafica = "Fase IB: Presas con capacidad de carga (K)"
        if chk_K_val.value and chk_Resp_val.value: titulo_grafica = "Fase IB: capacidad de carga (K) y respuesta funcional tipo II"
        
        chart = alt.Chart(df).mark_line(strokeWidth=2.5).encode(
            x=alt.X('Tiempo:Q', title='Tiempo (Ticks)'),
            y=alt.Y('Poblacion:Q', title='Individuos'),
            color=alt.Color('Especie:N', scale=alt.Scale(domain=['Presas', 'Depredadores'], range=['blue', '#d62728']))
        ).properties(
            width=380, 
            height=280, 
            title=titulo_grafica
        ).configure_title(
            fontSize=16, anchor='start', color='gray'
        )
        
        fase1_chart.value = chart
        if not fase1_status.value.startswith("⚠️") and not fase1_status.value.startswith("☠️"):
            fase1_status.value = "✅ Simulación completada."
            
    except Exception as e:
        fase1_status.value = "❌ ERROR EN LA SIMULACIÓN. Revisa la consola."
        traceback.print_exc()

@solara.component
def PanelFase1():
    with solara.Card(title="Panel Interactivo Fase I", elevation=3, margin=10):
        with solara.Columns([5, 7]):
            with solara.Column():
                solara.Checkbox(label="Activar Límite Logístico (K)", value=chk_K_val)
                solara.SliderInt("Valor K:", value=slide_K_val, min=100, max=2000, step=100)
                solara.Checkbox(label="Activar Respuesta Funcional tipo II", value=chk_Resp_val)
                solara.SliderInt("Tiempo manipulación:", value=slide_T_val, min=1, max=10, step=1)
                solara.SliderInt("Pasos:", value=slide_Pasos_val, min=50, max=1500, step=50)
                
                solara.Button(
                    "🎲 Generar Universo Estocástico", 
                    on_click=generar_universo, 
                    color="success",
                    style={"margin-top": "15px", "width": "100%"}
                )
                
                if fase1_status.value:
                    solara.Markdown(f"**Estado:** {fase1_status.value}")
                    
            with solara.Column(align="center", style={"justify-content": "center", "min-height": "380px"}):
                if fase1_chart.value is not None:
                    solara.FigureAltair(fase1_chart.value)
                else:
                    solara.Markdown("*Haz clic en '🎲 Generar Universo Estocástico' para ejecutar la simulación.*")



@solara.component
def App():
    route, set_route = solara.use_route()
    
    if route == "fase1a":
        EstocasticidadDemoFaseIA()
    elif route == "fase1b":
        EstocasticidadDemoFaseIB()
    elif route == "lab":
        Dashboard()
    elif route == "fase1":
        PanelFase1()
    elif route == "fase2":
        PageFase2()
    else:
        solara.Markdown("### Selecciona un panel desde la web")
        
@solara.component
def Layout(children):
    return solara.Column(children=children)

routes = [
    solara.Route(path="/", component=App, layout=Layout),
    solara.Route(path="fase1a", component=EstocasticidadDemoFaseIA, layout=Layout),
    solara.Route(path="fase1b", component=EstocasticidadDemoFaseIB, layout=Layout),
    solara.Route(path="lab", component=Dashboard, layout=Layout),
    solara.Route(path="fase1", component=PanelFase1, layout=Layout),
    solara.Route(path="fase2", component=PageFase2, layout=Layout),
]


"""
export_charts.py
================
Genera todas las gráficas del TFG como JSON de Vega-Lite para la web.
Ejecutar desde la carpeta raíz del TFG (TFG/):

    tfg-env/bin/python3 web/export_charts.py

Nota: usa siempre el python del entorno virtual, no `python` a secas.
Output: web/charts/*.json
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
import altair as alt
from scipy.integrate import odeint

alt.data_transformers.disable_max_rows()

OUT = os.path.join(os.path.dirname(__file__), 'charts')
os.makedirs(OUT, exist_ok=True)

def save(chart, name):
    path = os.path.join(OUT, f'{name}.json')
    chart.save(path)
    print(f'  ✅ {name}.json')

# ─────────────────────────────────────────────────────────
# 1. LOTKA-VOLTERRA ANALÍTICO
# ─────────────────────────────────────────────────────────
print('\n📐 Chart 1: Lotka-Volterra analítico...')

def lotka_volterra(state, t, alpha, beta, delta, gamma):
    x, y = state
    dxdt = alpha * x - beta * x * y
    dydt = delta * x * y - gamma * y
    return [dxdt, dydt]

t = np.linspace(0, 40, 800)
state0 = [40, 9]
params = (0.1, 0.02, 0.01, 0.1)
sol = odeint(lotka_volterra, state0, t, args=params)

df_lv = pd.DataFrame({
    'Tiempo': np.tile(t, 2),
    'Población': np.concatenate([sol[:, 0], sol[:, 1]]),
    'Especie': ['Presa (Conejos)'] * len(t) + ['Depredador (Lobos)'] * len(t)
})

chart_lv = alt.Chart(df_lv).mark_line(strokeWidth=2.5).encode(
    x=alt.X('Tiempo:Q', title='Tiempo (pasos)'),
    y=alt.Y('Población:Q', title='Tamaño poblacional'),
    color=alt.Color('Especie:N', scale=alt.Scale(
        domain=['Presa (Conejos)', 'Depredador (Lobos)'],
        range=['#2ca02c', '#d62728']
    )),
    tooltip=['Tiempo:Q', 'Especie:N', alt.Tooltip('Población:Q', format='.1f')]
).properties(
    width=600, height=300,
    title=alt.TitleParams(
        text='Modelo Lotka-Volterra: Ciclos depredador-presa',
        subtitle='Solución analítica · Oscilaciones neutralmente estables',
        fontSize=14, subtitleFontSize=11
    )
).interactive()

save(chart_lv, 'lotka_volterra')

# ─────────────────────────────────────────────────────────
# 2. ABM ESTOCÁSTICO - 10 UNIVERSOS (Fase IA)
# ─────────────────────────────────────────────────────────
print('\n🎲 Chart 2: 10 universos estocásticos...')

from mesa.batchrunner import batch_run
from model import FilterCorridorModel  # type: ignore  (sys.path añade la raíz en runtime)

# Usamos el modelo base (sin corredor) como proxy Lotka-Volterra ABM
params_lv = {
    'N_prey': [40],
    'N_predator': [9],
    'corridor_active': [False],
}

print('  Corriendo 10 réplicas...')
results_lv = batch_run(
    FilterCorridorModel,
    parameters={'N_prey': 40, 'N_predator': 9, 'corridor_active': False},
    iterations=10,
    max_steps=200,
    data_collection_period=1,
    number_processes=1,
    display_progress=False,
)

df_abm = pd.DataFrame(results_lv)

# Filtrar columnas relevantes
prey_col  = [c for c in df_abm.columns if 'rey' in c or 'Prey' in c or 'presa' in c.lower()]
pred_col  = [c for c in df_abm.columns if 'red' in c or 'Pred' in c or 'depred' in c.lower()]
step_col  = [c for c in df_abm.columns if 'step' in c.lower() or 'Step' in c]
run_col   = [c for c in df_abm.columns if 'run' in c.lower() or 'Run' in c or 'iter' in c.lower()]

print(f'  Columnas disponibles: {list(df_abm.columns)}')

if prey_col and pred_col and step_col:
    pc, prc, sc = prey_col[0], pred_col[0], step_col[0]
    rc = run_col[0] if run_col else 'RunId'

    rows = []
    for _, row in df_abm.iterrows():
        rows.append({'Paso': row[sc], 'Población': row[pc], 'Especie': 'Presa', 'Réplica': str(row.get(rc, 0))})
        rows.append({'Paso': row[sc], 'Población': row[prc], 'Especie': 'Depredador', 'Réplica': str(row.get(rc, 0))})

    df_10u = pd.DataFrame(rows)

    chart_10u = alt.Chart(df_10u).mark_line(opacity=0.6, strokeWidth=1.5).encode(
        x=alt.X('Paso:Q', title='Paso de simulación'),
        y=alt.Y('Población:Q', title='Nº individuos'),
        color=alt.Color('Especie:N', scale=alt.Scale(
            domain=['Presa', 'Depredador'],
            range=['#2ca02c', '#d62728']
        )),
        detail='Réplica:N',
        tooltip=['Paso:Q', 'Especie:N', 'Población:Q', 'Réplica:N']
    ).properties(
        width=600, height=300,
        title=alt.TitleParams(
            text='La inocencia del azar: 10 universos paralelos',
            subtitle='Cada línea es una réplica con la misma condición inicial · Divergencia estocástica',
            fontSize=14, subtitleFontSize=11
        )
    ).interactive()

    save(chart_10u, 'diez_universos')
else:
    print(f'  ⚠️  No se encontraron columnas esperadas. Disponibles: {list(df_abm.columns)}')

# ─────────────────────────────────────────────────────────
# 3. CORREDOR vs AISLADO (Fase IIB)
# ─────────────────────────────────────────────────────────
print('\n🌿 Chart 3: Corredor vs Aislado...')

def run_scenario(corridor_active, n_steps=300, n_runs=5):
    rows = []
    for run in range(n_runs):
        m = FilterCorridorModel(N_prey=50, N_predator=8, corridor_active=corridor_active)
        for step in range(n_steps):
            if not m.running:
                break
            m.step()
            n_prey = sum(1 for a in m.agents if 'Prey' in a.__class__.__name__ and a.pos)
            n_pred = sum(1 for a in m.agents if 'Predator' in a.__class__.__name__ and a.pos)
            rows.append({
                'Paso': step,
                'Presas': n_prey,
                'Depredadores': n_pred,
                'Escenario': 'Conectado (Corredor)' if corridor_active else 'Aislado (Sin corredor)',
                'Réplica': run
            })
    return rows

print('  Escenario AISLADO...')
rows_aislado = run_scenario(False, n_steps=300, n_runs=5)
print('  Escenario CONECTADO...')
rows_conectado = run_scenario(True, n_steps=300, n_runs=5)

df_corredor = pd.DataFrame(rows_aislado + rows_conectado)

# Media por escenario
df_media = df_corredor.groupby(['Paso', 'Escenario']).agg(
    Presas=('Presas', 'mean'),
    Depredadores=('Depredadores', 'mean')
).reset_index()

df_long = pd.melt(df_media, id_vars=['Paso', 'Escenario'],
                  value_vars=['Presas', 'Depredadores'],
                  var_name='Especie', value_name='Población')

chart_corredor = alt.Chart(df_long).mark_line(strokeWidth=2.5).encode(
    x=alt.X('Paso:Q', title='Paso de simulación'),
    y=alt.Y('Población:Q', title='Nº individuos (media 5 réplicas)'),
    color=alt.Color('Especie:N', scale=alt.Scale(
        domain=['Presas', 'Depredadores'],
        range=['#2ca02c', '#d62728']
    )),
    strokeDash=alt.StrokeDash('Escenario:N', scale=alt.Scale(
        domain=['Conectado (Corredor)', 'Aislado (Sin corredor)'],
        range=[[1, 0], [6, 3]]
    )),
    tooltip=['Paso:Q', 'Especie:N', 'Escenario:N', alt.Tooltip('Población:Q', format='.1f')]
).properties(
    width=600, height=300,
    title=alt.TitleParams(
        text='Efecto del corredor ecológico sobre la persistencia',
        subtitle='Línea continua = con corredor · Discontinua = aislado · Media de 5 réplicas',
        fontSize=14, subtitleFontSize=11
    )
).interactive()

save(chart_corredor, 'corredor_vs_aislado')

print('\n✅ Todas las gráficas generadas en web/charts/')
print('   Ahora ejecuta: open web/index.html')

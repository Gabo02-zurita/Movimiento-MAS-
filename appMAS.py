import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint

# --- Configuración de la Página y Estilo de la UTA / Ingeniería Mecánica ---
st.set_page_config(
    page_title="MAS Simulator - Ingeniería UTA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo UTA
def apply_custom_style():
    # Estilo básico de la UTA (Azul Oscuro, Naranja)
    st.markdown("""
        <style>
        .reportview-container {
            background: #FFFFFF;
        }
        .sidebar .sidebar-content {
            background: #25447C; /* Azul Oscuro UTA */
            color: white;
        }
        .css-1d391kg { /* Estilo del título en el sidebar */
            color: white !important;
        }
        .css-1lcbmhc { /* Estilo general del texto en sidebar */
            color: white;
        }
        .stButton>button {
            background-color: #F89B2B; /* Naranja UTA */
            color: white;
            border-radius: 5px;
        }
        h1, h2, h3 {
            color: #25447C; /* Azul Oscuro UTA */
        }
        .stMarkdown p {
            font-size: 1.05em;
        }
        </style>
        """, unsafe_allow_html=True)
    
apply_custom_style()

st.title("⚙️ Simulador Interactivo de Movimiento Armónico Simple (MAS)")
st.header("Análisis de Fenómenos Físicos para Ingeniería Mecánica (UTA)")
st.markdown("---")

# --- Funciones de Simulación (ODEs) ---

# Ecuación diferencial para el Péndulo Simple (No Lineal)
def pendulum_ode(y, t, g, L):
    theta, omega = y
    dydt = [omega, - (g / L) * np.sin(theta)]
    return dydt

# Ecuación diferencial para el MAS con Amortiguamiento (Modelo Lineal)
def damped_mas_ode(y, t, k, m, c):
    x, v = y
    dydt = [v, - (c / m) * v - (k / m) * x]
    return dydt

# Ecuación diferencial para el MAS Forzado (Modelo Lineal)
def forced_mas_ode(y, t, k, m, c, F0, w_f):
    x, v = y
    dydt = [v, - (c / m) * v - (k / m) * x + (F0 / m) * np.cos(w_f * t)]
    return dydt

# --- Sidebar para Navegación ---
st.sidebar.title("📚 Menú de Análisis")
menu_selection = st.sidebar.radio(
    "Seleccione el Fenómeno a Simular:",
    [
        "1. Simulación Masa-Resorte",
        "2. Simulación Péndulo Simple",
        "3. Análisis de Parámetros ($k$ y $m$)",
        "4. Casos Extendidos (Amortiguado, Forzado, Superposición)"
    ]
)

# --- Contenido Principal basado en la Selección ---

# ----------------------------------------------------
# 1. Simulación Masa-Resorte (Horizontal/Vertical)
# ----------------------------------------------------
if menu_selection == "1. Simulación Masa-Resorte":
    
    st.header("1️⃣ Simulación de Masa-Resorte")
    st.markdown("Este módulo permite analizar las variables cinemáticas y energéticas del sistema masa-resorte.")
    
    st.subheader("📚 Fundamentos Teóricos")
    st.latex(r"x(t) = A \cos(\omega t + \phi)")
    st.latex(r"\omega = \sqrt{\frac{k}{m}} \quad \text{(Frecuencia Angular)}")
    st.latex(r"E_{Total} = E_{Potencial} + E_{Cinética} = \frac{1}{2} k A^2")
    st.markdown("""
    * **Posición ($x$):** Describe la ubicación de la masa en cualquier instante.
    * **Velocidad ($v$):** Máxima en el punto de equilibrio ($x=0$), nula en los extremos.
    * **Aceleración ($a$):** Proporcional a la posición ($a = -\omega^2 x$), dirigida al punto de equilibrio (**Ley de Hooke**).
    """)
    
    st.subheader("🛠️ Parámetros del Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        m = st.number_input("Masa ($m$) [kg]", value=1.0, min_value=0.01, step=0.1, format="%.2f")
    with col2:
        k = st.number_input("Constante Elástica ($k$) [N/m]", value=10.0, min_value=0.01, step=1.0, format="%.2f")
    with col3:
        A = st.number_input("Amplitud ($A$) [m]", value=0.5, min_value=0.01, step=0.05, format="%.2f")
    with col4:
        T_max = st.slider("Tiempo Máximo de Simulación ($t_{max}$) [s]", 1.0, 20.0, 10.0, 1.0)
    
    # Cálculos fundamentales
    omega = np.sqrt(k / m)
    T = 2 * np.pi / omega
    t = np.linspace(0, T_max, 500)
    
    # Ecuaciones del MAS (Asumiendo fase inicial phi=0)
    x = A * np.cos(omega * t)
    v = -A * omega * np.sin(omega * t)
    a = -A * omega**2 * np.cos(omega * t)
    
    # Ecuaciones de Energía
    Ep = 0.5 * k * x**2  # Energía Potencial Elástica
    Ek = 0.5 * m * v**2  # Energía Cinética
    Et = Ek + Ep          # Energía Total (constante)
    
    st.markdown(f"***Frecuencia Angular ($\omega$):*** **{omega:.2f} rad/s** | ***Periodo ($T$):*** **{T:.2f} s**")
    
    
    # --- Gráficas de Cinética (Posición, Velocidad, Aceleración) ---
    st.subheader("📈 Gráficos Cinemáticos vs. Tiempo")
    
    fig_kinematics = go.Figure()
    
    fig_kinematics.add_trace(go.Scatter(x=t, y=x, mode='lines', name='Posición (x)', line=dict(color='#25447C', width=2)))
    fig_kinematics.add_trace(go.Scatter(x=t, y=v, mode='lines', name='Velocidad (v)', line=dict(color='#F89B2B', width=2)))
    fig_kinematics.add_trace(go.Scatter(x=t, y=a, mode='lines', name='Aceleración (a)', line=dict(color='#94B34A', width=2)))
    
    fig_kinematics.update_layout(
        title='Cinemática del MAS',
        xaxis_title='Tiempo (s)',
        yaxis_title='Magnitud (m, m/s, m/s²)',
        hovermode="x unified",
        template='plotly_white'
    )
    st.plotly_chart(fig_kinematics, use_container_width=True)
    
    # --- Gráficas de Energía ---
    st.subheader("⚡ Gráfico de Energía vs. Tiempo")
    
    fig_energy = go.Figure()
    
    fig_energy.add_trace(go.Scatter(x=t, y=Ek, mode='lines', name='Energía Cinética ($E_k$)', line=dict(color='#F89B2B', width=3)))
    fig_energy.add_trace(go.Scatter(x=t, y=Ep, mode='lines', name='Energía Potencial ($E_p$)', line=dict(color='#25447C', width=3)))
    fig_energy.add_trace(go.Scatter(x=t, y=Et, mode='lines', name='Energía Total ($E_t$)', line=dict(color='gray', dash='dash', width=1.5)))
    
    fig_energy.update_layout(
        title='Conservación de la Energía en el MAS',
        xaxis_title='Tiempo (s)',
        yaxis_title='Energía (J)',
        hovermode="x unified",
        template='plotly_white'
    )
    st.plotly_chart(fig_energy, use_container_width=True)
    
# ----------------------------------------------------
# 2. Simulación Péndulo Simple
# ----------------------------------------------------
elif menu_selection == "2. Simulación Péndulo Simple":
    
    st.header("2️⃣ Simulación de Péndulo Simple")
    st.markdown("Análisis de las oscilaciones de un péndulo simple, comparando el modelo lineal (MAS) con la solución no lineal (Ecuación completa).")
    
    st.subheader("🛠️ Parámetros del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        L = st.number_input("Longitud de la Cuerda ($L$) [m]", value=1.0, min_value=0.1, step=0.1, format="%.2f")
    with col2:
        g = st.number_input("Aceleración de Gravedad ($g$) [m/s²]", value=9.81, min_value=0.1, step=0.1, format="%.2f")
    with col3:
        theta_0_deg = st.number_input("Ángulo Inicial ($\Theta_0$) [grados]", value=10.0, min_value=0.1, max_value=179.0, step=5.0, format="%.2f")
    
    T_max = st.slider("Tiempo Máximo de Simulación ($t_{max}$) [s]", 5.0, 30.0, 15.0, 1.0)
    
    theta_0 = np.deg2rad(theta_0_deg)  # Convertir a radianes
    
    # Cálculos fundamentales
    omega_lin = np.sqrt(g / L)
    T_lin = 2 * np.pi / omega_lin
    t = np.linspace(0, T_max, 500)
    
    # Modelo Lineal (MAS)
    theta_lin = theta_0 * np.cos(omega_lin * t)
    
    # Modelo No Lineal (Solución Numérica de la ODE)
    y0 = [theta_0, 0.0]  # [Ángulo inicial, Velocidad angular inicial]
    sol = odeint(pendulum_ode, y0, t, args=(g, L))
    theta_nonlin = sol[:, 0]
    
    st.markdown(f"***Periodo Lineal ($T$):*** **{T_lin:.2f} s**")
    
    # --- Gráfica de Ángulo vs. Tiempo ---
    st.subheader("📊 Comparación: Modelo Lineal vs. No Lineal")
    
    fig_pendulum = go.Figure()
    
    fig_pendulum.add_trace(go.Scatter(x=t, y=np.rad2deg(theta_nonlin), mode='lines', name='Modelo No Lineal (Real)', line=dict(color='#25447C', width=3)))
    fig_pendulum.add_trace(go.Scatter(x=t, y=np.rad2deg(theta_lin), mode='lines', name='Modelo Lineal (MAS)', line=dict(color='#F89B2B', dash='dash', width=2)))
    
    fig_pendulum.update_layout(
        title=f'Ángulo ($\Theta$) vs. Tiempo para Péndulo Simple ($\Theta_0 = {theta_0_deg}^\circ$)',
        xaxis_title='Tiempo (s)',
        yaxis_title='Ángulo ($\Theta$) [grados]',
        hovermode="x unified",
        template='plotly_white'
    )
    st.plotly_chart(fig_pendulum, use_container_width=True)
    
    st.subheader("💡 Explicación Física")
    st.markdown(f"""
    * El **Modelo Lineal** (MAS) es una aproximación válida solo para **ángulos iniciales pequeños** ($\Theta_0 < 10^\circ$), donde $\sin(\Theta) \approx \Theta$.
    * Para ángulos grandes (como los **{theta_0_deg:.2f}°** simulados), el **Modelo No Lineal** es necesario y muestra un periodo ligeramente más largo y una forma de onda menos perfectamente cosenoidal, con una diferencia clara en la gráfica.
    """)

# ----------------------------------------------------
# 3. Análisis de Parámetros (k y m)
# ----------------------------------------------------
elif menu_selection == "3. Análisis de Parámetros ($k$ y $m$)":
    
    st.header("3️⃣ Análisis del Efecto de la Constante Elástica ($k$) y la Masa ($m$)")
    st.markdown("Explore cómo la rigidez del resorte ($k$) y la inercia de la masa ($m$) afectan el Periodo ($T$) del MAS.")
    
    
    st.subheader("📚 Relación Fundamental")
    st.markdown("El periodo de oscilación ($T$) de un sistema masa-resorte está dado por:")
    st.latex(r"T = 2\pi \sqrt{\frac{m}{k}}")
    st.markdown("""
    * **Aumento de $m$ (Masa):** Aumenta la **inercia** del sistema. Esto **aumenta el periodo ($T$)** y disminuye la frecuencia.
    * **Aumento de $k$ (Constante Elástica):** Aumenta la **rigidez** del resorte. Esto **disminuye el periodo ($T$)** y aumenta la frecuencia.
    """)
    
    st.subheader("🔬 Experimentación Virtual")
    
    # Crear un rango de valores para k y m
    k_array = np.linspace(1, 100, 100)
    m_array = np.linspace(0.1, 10, 100)
    
    # Parámetro Fijo

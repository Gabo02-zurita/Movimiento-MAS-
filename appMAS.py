import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint
import time 

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

# --- Configuración de la Página y Estilo de la UTA / Ingeniería Mecánica ---
st.set_page_config(
    page_title="MAS Simulator - Ingeniería UTA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado de sesión para los botones de animación
if 'pendulum_run' not in st.session_state:
    st.session_state.pendulum_run = False
if 'mas_run' not in st.session_state:
    st.session_state.mas_run = False
if 'damped_run' not in st.session_state:
    st.session_state.damped_run = False
if 'forced_run' not in st.session_state:
    st.session_state.forced_run = False

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
            font-weight: bold; /* Hacer el texto del botón más legible */
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


    # --- Sección de Animación Visual de Masa-Resorte ---
    st.subheader("🎬 Animación Visual de Masa-Resorte")

    # Función de callback para el botón
    def start_mas_animation():
        st.session_state.mas_run = True

    # Botón de Play
    if st.button("▶️ Iniciar Animación", key="btn_mas_start"):
        start_mas_animation()

    # Contenedor para la animación
    animation_placeholder = st.empty()

    # Parámetros visuales (Horizontal)
    y_pos = 0  # Movimiento horizontal, y fijo en 0
    range_limit = A * 1.2 # Rango para el eje x, con un margen

    # Solo ejecutar el bucle si el estado es True
    if st.session_state.mas_run:

        st.markdown("Animación en curso. Ajusta los parámetros y vuelve a presionar el botón para reiniciar.")

        # Reducir el número de puntos para una animación más fluida
        t_anim = np.linspace(0, T_max, 50) 
        x_anim = A * np.cos(omega * t_anim) # Posición de la masa (x(t))

        for i in range(len(t_anim)):

            # Crear la figura Plotly para la representación física
            fig_animation = go.Figure()

            # 1. Punto de Anclaje Fijo (La pared)
            fig_animation.add_trace(go.Scatter(
                x=[-range_limit], y=[y_pos],
                mode='markers', name='Anclaje', 
                marker=dict(size=10, color='red', symbol='square')
            ))
            
            # 2. Resorte (Línea simple del anclaje a la masa)
            fig_animation.add_trace(go.Scatter(
                x=[-range_limit, x_anim[i]], y=[y_pos, y_pos],
                mode='lines', name='Resorte', 
                line=dict(color='gray', width=3, dash='dot')
            ))

            # 3. Traza de la Masa (Punto azul grande)
            fig_animation.add_trace(go.Scatter(
                x=[x_anim[i]], y=[y_pos],
                mode='markers', name='Masa', 
                marker=dict(size=30, color='#25447C', symbol='square')
            ))

            # Configuración del layout
            fig_animation.update_layout(
                title=f"Posición Física de la Masa (t={t_anim[i]:.2f}s)",
                xaxis_title='Posición X (m)',
                yaxis_title='',
                xaxis_range=[-range_limit, range_limit],
                yaxis_range=[-0.5, 0.5], 
                showlegend=False,
                template='plotly_white',
                height=300
            )
            fig_animation.update_yaxes(visible=False) # Ocultar eje Y ya que el movimiento es horizontal

            animation_placeholder.plotly_chart(fig_animation, use_container_width=True)

            # Pausa para controlar la velocidad
            time.sleep(0.05) 

        # Al terminar la simulación, reseteamos el estado
        st.session_state.mas_run = False
        st.success("✅ Simulación completa. Ajuste los parámetros para volver a simular.")

    else:
        # Mostramos la posición inicial cuando no está corriendo
        st.markdown("Presione **'Iniciar Animación'** para visualizar el movimiento horizontal.")

        # Posición inicial (x[0] = A, ya que phi=0)
        fig_initial = go.Figure()
        fig_initial.add_trace(go.Scatter(x=[-range_limit], y=[y_pos], mode='markers', marker=dict(size=10, color='red', symbol='square')))
        fig_initial.add_trace(go.Scatter(x=[-range_limit, x[0]], y=[y_pos, y_pos], mode='lines', line=dict(color='gray', width=3, dash='dot')))
        fig_initial.add_trace(go.Scatter(x=[x[0]], y=[y_pos], mode='markers', marker=dict(size=30, color='#25447C', symbol='square')))

        fig_initial.update_layout(
            title="Posición Inicial de la Masa",
            xaxis_title='Posición X (m)', yaxis_title='',
            xaxis_range=[-range_limit, range_limit], yaxis_range=[-0.5, 0.5], 
            showlegend=False, template='plotly_white', height=300
        )
        fig_initial.update_yaxes(visible=False)
        animation_placeholder.plotly_chart(fig_initial, use_container_width=True)

    
# ----------------------------------------------------
# 2. Simulación Péndulo Simple
# ----------------------------------------------------
elif menu_selection == "2. Simulación Péndulo Simple":
    
    st.header("2️⃣ Simulación de Péndulo Simple")
    st.markdown("Análisis de las oscilaciones de un péndulo simple, comparando el modelo lineal (MAS) con la solución no lineal (Ecuación completa).")
    st.subheader("🛠️ Parámetros del Sistema")
    
    # Función de callback para el botón
    def start_pendulum_animation():
        st.session_state.pendulum_run = True

    col1, col2, col3 = st.columns(3)
    
    with col1:
        L = st.number_input("Longitud de la Cuerda ($L$) [m]", value=1.0, min_value=0.1, step=0.1, format="%.2f")
    with col2:
        g = st.number_input("Aceleración de Gravedad ($g$) [m/s²]", value=9.81, min_value=0.1, step=0.1, format="%.2f")
    with col3:
        theta_0_deg = st.number_input("Ángulo Inicial ($\Theta_0$) [grados]", value=30.0, min_value=0.1, max_value=179.0, step=5.0, format="%.2f")
    
    T_max = st.slider("Tiempo Máximo de Simulación ($t_{max}$) [s]", 5.0, 30.0, 15.0, 1.0)
    
    theta_0 = np.deg2rad(theta_0_deg)  # Convertir a radianes
    
    # Cálculos fundamentales y solución de la ODE
    omega_lin = np.sqrt(g / L)
    T_lin = 2 * np.pi / omega_lin
    t = np.linspace(0, T_max, 500)
    
    theta_lin = theta_0 * np.cos(omega_lin * t)
    
    y0 = [theta_0, 0.0]  # [Ángulo inicial, Velocidad angular inicial]
    sol = odeint(pendulum_ode, y0, t, args=(g, L))
    theta_nonlin = sol[:, 0]
    
    st.markdown(f"***Periodo Lineal ($T$):*** **{T_lin:.2f} s**")
    
    # --- Gráfica de Ángulo vs. Tiempo (Simulación Gráfica) ---
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
    
    # --- Sección de Animación Visual ---
    
    st.subheader("🎬 Animación Visual del Péndulo Simple")

    # Botón de Play
    if st.button("▶️ Iniciar Animación", key="btn_pendulum_start"):
        start_pendulum_animation()
    
    # 1. Calcular coordenadas cartesianas (X, Y)
    x_coords = L * np.sin(theta_nonlin)
    y_coords = -L * np.cos(theta_nonlin)

    # Contenedor para la animación
    animation_placeholder = st.empty()
    
    # Solo ejecutar el bucle si el estado es True (el botón fue presionado)
    if st.session_state.pendulum_run:
        
        st.markdown("Animación en curso. Ajusta los parámetros y vuelve a presionar el botón para reiniciar.")
        
        # Reducir el número de puntos para una animación más fluida
        t_anim = np.linspace(0, T_max, 50) 
        x_anim = np.interp(t_anim, t, x_coords)
        y_anim = np.interp(t_anim, t, y_coords)

        for i in range(len(t_anim)):
            
            # Crear la figura Plotly para la representación física
            fig_animation = go.Figure()
            
            # 1. Traza de la Cuerda (Línea desde el origen hasta la masa)
            fig_animation.add_trace(go.Scatter(
                x=[0, x_anim[i]], y=[0, y_anim[i]],
                mode='lines', name='Cuerda (L)', 
                line=dict(color='gray', width=2)
            ))
            
            # 2. Traza de la Masa (Punto)
            fig_animation.add_trace(go.Scatter(
                x=[x_anim[i]], y=[y_anim[i]],
                mode='markers', name='Masa', 
                marker=dict(size=20, color='#25447C')
            ))
            
            # 3. Trayectoria (Para contexto visual)
            fig_animation.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines', name='Trayectoria', 
                line=dict(color='#F89B2B', width=1, dash='dot')
            ))
            
            # Configuración del layout
            fig_animation.update_layout(
                title=f"Posición Física del Péndulo (t={t_anim[i]:.2f}s)",
                xaxis_title='Posición X (m)',
                yaxis_title='Posición Y (m)',
                xaxis_range=[-L*1.1, L*1.1],
                yaxis_range=[-L*1.1, 0.1], 
                showlegend=False,
                template='plotly_white',
                height=400
            )
            fig_animation.update_yaxes(scaleanchor="x", scaleratio=1) 

            animation_placeholder.plotly_chart(fig_animation, use_container_width=True)
            
            # Pausa para controlar la velocidad
            time.sleep(0.05) 
            
        # Al terminar la simulación, reseteamos el estado para que el botón funcione de nuevo
        st.session_state.pendulum_run = False
        st.success("✅ Simulación completa. Ajuste los parámetros para volver a simular.")
        
    else:
        # Mostramos la posición inicial cuando no está corriendo
        st.markdown("Presione **'Iniciar Animación'** para visualizar el movimiento.")
        
        fig_initial = go.Figure()
        fig_initial.add_trace(go.Scatter(x=[0, x_coords[0]], y=[0, y_coords[0]], mode='lines', line=dict(color='gray', width=2)))
        fig_initial.add_trace(go.Scatter(x=[x_coords[0]], y=[y_coords[0]], mode='markers', marker=dict(size=20, color='#25447C')))
        fig_initial.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='lines', line=dict(color='#F89B2B', width=1, dash='dot')))
        fig_initial.update_layout(
            title="Posición Inicial del Péndulo",
            xaxis_title='Posición X (m)', yaxis_title='Posición Y (m)',
            xaxis_range=[-L*1.1, L*1.1], yaxis_range=[-L*1.1, 0.1], 
            showlegend=False, template='plotly_white', height=400
        )
        fig_initial.update_yaxes(scaleanchor="x", scaleratio=1)
        animation_placeholder.plotly_chart(fig_initial, use_container_width=True)


    st.subheader("💡 Explicación Física")
    st.markdown(r"""
    * El **Modelo Lineal** (MAS) es una aproximación válida solo para **ángulos iniciales pequeños** ($\Theta_0 < 10^\circ$), donde se aplica la **aproximación de ángulo pequeño**: $\sin(\Theta) \approx \Theta$. 

[Image of simple pendulum diagram showing small angle approximation]

    * Para ángulos grandes (como los **%s°** simulados), el **Modelo No Lineal** es necesario y muestra un periodo ligeramente más largo y una forma de onda menos perfectamente cosenoidal, con una diferencia clara en la gráfica.
    """ % theta_0_deg)


# ----------------------------------------------------
# 3. Análisis de Parámetros (k y m) - Experimentación Virtual
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
    st.markdown("Ajuste los parámetros fijos para generar los gráficos y ver cómo el periodo ($T$) cambia con respecto a $k$ y $m$.")
    
    # Crear un rango de valores para k y m
    k_array = np.linspace(1, 100, 100)
    m_array = np.linspace(0.1, 10, 100)
    
    # Parámetro Fijo (Controles)
    m_fixed = st.slider("Masa Fija ($m$) [kg] para Gráfico 1 (T vs. k)", 0.1, 5.0, 1.0, 0.1, key="m_fixed_slider")
    k_fixed = st.slider("Constante Elástica Fija ($k$) [N/m] para Gráfico 2 (T vs. m)", 1.0, 100.0, 10.0, 1.0, key="k_fixed_slider")
    
    # --- Gráfico 1: T vs. k (m constante) ---
    T_vs_k = 2 * np.pi * np.sqrt(m_fixed / k_array)
    
    fig_k = go.Figure(data=[
        go.Scatter(x=k_array, y=T_vs_k, mode='lines', line=dict(color='#25447C', width=3))
    ])
    fig_k.update_layout(
        title=f'Periodo ($T$) vs. Constante Elástica ($k$) (Masa $m={m_fixed}$ kg)',
        xaxis_title='Constante Elástica ($k$) [N/m]',
        yaxis_title='Periodo ($T$) [s]',
        template='plotly_white'
    )
    st.plotly_chart(fig_k, use_container_width=True)
    st.markdown("El gráfico muestra una **relación inversa no lineal ($\propto 1/\sqrt{k}$)**. Un resorte más rígido ($k$ alto) da un periodo más corto.")
    
    # --- Gráfico 2: T vs. m (k constante) ---
    T_vs_m = 2 * np.pi * np.sqrt(m_array / k_fixed)
    
    fig_m = go.Figure(data=[
        go.Scatter(x=m_array, y=T_vs_m, mode='lines', line=dict(color='#F89B2B', width=3))
    ])
    fig_m.update_layout(
        title=f'Periodo ($T$) vs. Masa ($m$) (Constante $k={k_fixed}$ N/m)',
        xaxis_title='Masa ($m$) [kg]',
        yaxis_title='Periodo ($T$) [s]',
        template='plotly_white'
    )
    st.plotly_chart(fig_m, use_container_width=True)
    st.markdown("El gráfico muestra una **relación directa no lineal ($\propto \sqrt{m}$)**. Una masa mayor ($m$ alto) da un periodo más largo.")
    

# ----------------------------------------------------
# 4. Casos Extendidos
# ----------------------------------------------------
elif menu_selection == "4. Casos Extendidos (Amortiguado, Forzado, Superposición)":
    
    st.header("4️⃣ Casos Extendidos de Oscilación")
    
    extended_case = st.selectbox(
        "Seleccione el caso avanzado:",
        ["MAS con Amortiguamiento", "MAS Forzado", "Superposición de Oscilaciones"]
    )
    
    st.markdown("---")
    
    # INICIALIZACIÓN DE VARIABLES CRÍTICAS (DEBEN EXISTIR FUERA DE CUALQUIER BLOQUE CONDICIONAL)
    y_pos = 0 # Para animaciones horizontales
    
    # Inicialización de variables de Resonancia y Batido para evitar NameErrors.
    # Usamos valores neutrales.
    omega_n = 0.0
    w_beat = 0.0
    T_beat = 0.0
    
    # ----------------------------------------------------
    # 4.1. MAS con Amortiguamiento
    # ----------------------------------------------------
    if extended_case == "MAS con Amortiguamiento":
        st.subheader("4.1. MAS con Amortiguamiento")
        st.markdown("Se añade una fuerza de arrastre proporcional a la velocidad ($\mathbf{F_c} = -c \mathbf{v}$).")
        
        st.subheader("🛠️ Parámetros y Ecuación")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            m_d = st.number_input("Masa ($m$) [kg] | Amort.", value=1.0, min_value=0.1, step=0.1, key="m_d")
        with col2:
            k_d = st.number_input("Constante Elástica ($k$) [N/m] | Amort.", value=10.0, min_value=1.0, step=1.0, key="k_d")
        with col3:
            c_d = st.number_input("Coeficiente de Amortiguamiento ($c$) [N·s/m]", value=0.5, min_value=0.0, step=0.1, key="c_d")

        T_max_d = st.slider("Tiempo Máximo de Simulación ($t_{max}$) [s] | Amort.", 5.0, 30.0, 20.0, 1.0)
        A_d = st.number_input("Amplitud Inicial ($A_0$) [m] | Amort.", value=1.0, min_value=0.1, step=0.1, key="A_d")
        
        # Simulación
        t_d = np.linspace(0, T_max_d, 500)
        y0_d = [A_d, 0.0]  # [Posición inicial, Velocidad inicial]
        sol_d = odeint(damped_mas_ode, y0_d, t_d, args=(k_d, m_d, c_d))
        x_d = sol_d[:, 0]
        
        # Parámetro crítico (para c_c=2*sqrt(km))
        c_critico = 2 * np.sqrt(k_d * m_d)
        
        # --- Gráfico de Posición vs. Tiempo ---
        st.subheader("📈 Gráfico de Posición vs. Tiempo")
        fig_damped = go.Figure(data=[
            go.Scatter(x=t_d, y=x_d, mode='lines', name=f'Oscilación (c={c_d} N·s/m)', line=dict(color='#25447C', width=3))
        ])
        fig_damped.update_layout(
            title=f'MAS Amortiguado (c_crítico = {c_critico:.2f} N·s/m)',
            xaxis_title='Tiempo (s)',
            yaxis_title='Posición (x) [m]',
            template='plotly_white'
        )
        st.plotly_chart(fig_damped, use_container_width=True)

        # --- Animación Visual Amortiguada ---
        st.subheader("🎬 Animación Visual Amortiguada")

        def start_damped_animation():
            st.session_state.damped_run = True

        if st.button("▶️ Iniciar Animación Amortiguada", key="btn_damped_start"):
            start_damped_animation()

        damped_placeholder = st.empty()
        range_limit = A_d * 1.2 # Rango basado en la amplitud inicial

        if st.session_state.damped_run:
            st.markdown("Animación en curso. La amplitud disminuye con el tiempo.")
            
            # Puntos de la solución ODE para animación (reducidos a 50 puntos)
            t_anim_d = np.linspace(0, T_max_d, 50)
            x_anim_d = np.interp(t_anim_d, t_d, x_d)
            
            for i in range(len(t_anim_d)):
                fig_animation = go.Figure()

                # Anclaje
                fig_animation.add_trace(go.Scatter(
                    x=[-range_limit], y=[y_pos], mode='markers', marker=dict(size=10, color='red', symbol='square')
                ))
                # Resorte
                fig_animation.add_trace(go.Scatter(
                    x=[-range_limit, x_anim_d[i]], y=[y_pos, y_pos],
                    mode='lines', line=dict(color='gray', width=3, dash='dot')
                ))
                # Masa
                fig_animation.add_trace(go.Scatter(
                    x=[x_anim_d[i]], y=[y_pos],
                    mode='markers', marker=dict(size=30, color='#25447C', symbol='square')
                ))

                fig_animation.update_layout(
                    title=f"MAS Amortiguado (t={t_anim_d[i]:.2f}s)",
                    xaxis_title='Posición X (m)', yaxis_title='',
                    xaxis_range=[-range_limit, range_limit], yaxis_range=[-0.5, 0.5], 
                    showlegend=False, template='plotly_white', height=300
                )
                fig_animation.update_yaxes(visible=False) 
                damped_placeholder.plotly_chart(fig_animation, use_container_width=True)
                time.sleep(0.05) 
                
            st.session_state.damped_run = False
            st.success("✅ Simulación amortiguada completa.")
            
        else:
            # Posición inicial estática
            x_initial = x_d[0]
            fig_initial = go.Figure()
            fig_initial.add_trace(go.Scatter(x=[-range_limit], y=[y_pos], mode='markers', marker=dict(size=10, color='red', symbol='square')))
            fig_initial.add_trace(go.Scatter(x=[-range_limit, x_initial], y=[y_pos, y_pos], mode='lines', line=dict(color='gray', width=3, dash='dot')))
            fig_initial.add_trace(go.Scatter(x=[x_initial], y=[y_pos], mode='markers', marker=dict(size=30, color='#25447C', symbol='square')))

            fig_initial.update_layout(
                title="Posición Inicial (Amortiguado)", xaxis_title='Posición X (m)', yaxis_title='',
                xaxis_range=[-range_limit, range_limit], yaxis_range=[-0.5, 0.5], showlegend=False, template='plotly_white', height=300
            )
            fig_initial.update_yaxes(visible=False)
            damped_placeholder.plotly_chart(fig_initial, use_container_width=True)
        
        st.subheader("💡 Clasificación del Movimiento")
        if c_d == 0:
            st.markdown("* **MAS no Amortiguado** (Oscilación persistente)")
        elif c_d < c_critico:
            st.markdown("* **Subamortiguado:** El sistema **oscila** con amplitud decreciente (la curva azul).")
        elif c_d == c_critico:
            st.markdown("* **Amortiguamiento Crítico:** El sistema vuelve al equilibrio **más rápido** sin oscilar.")
        else: # c_d > c_critico
            st.markdown("* **Sobreamortiguado:** El sistema vuelve al equilibrio **lentamente** sin oscilar.")
            
    # ----------------------------------------------------
    # 4.2. MAS Forzado
    # ----------------------------------------------------
    elif extended_case == "MAS Forzado":
        st.subheader("4.2. MAS Forzado")
        st.markdown("Se añade una fuerza externa periódica ($\mathbf{F_{ext}} = F_0 \cos(\omega_f t)$) al sistema amortiguado.")
        
        st.subheader("🛠️ Parámetros y Ecuación")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            m_f = st.number_input("Masa ($m$) [kg] | Forzado", value=1.0, min_value=0.1, step=0.1, key="m_f")
        with col2:
            k_f = st.number_input("Constante Elástica ($k$) [N/m] | Forzado", value=10.0, min_value=1.0, step=1.0, key="k_f")
        with col3:
            c_f = st.number_input("Coef. Amort. ($c$) [N·s/m] | Forzado", value=0.5, min_value=0.0, step=0.1, key="c_f")
        with col4:
            F0 = st.number_input("Amplitud de Fuerza ($F_0$) [N]", value=5.0, min_value=0.1, step=1.0, key="F0")
        with col5:
            w_f = st.number_input("Frecuencia de Fuerza ($\omega_f$) [rad/s]", value=3.5, min_value=0.1, step=0.1, key="w_f")

        T_max_f = st.slider("Tiempo Máximo de Simulación ($t_{max}$) [s] | Forzado", 5.0, 50.0, 30.0, 1.0)
        
        # CÁLCULO DE omega_n (sobrescribe el valor inicial de 0.0)
        omega_n = np.sqrt(k_f / m_f)
        
        # Simulación
        t_f = np.linspace(0, T_max_f, 1000)
        y0_f = [0.0, 0.0]  # [Posición inicial, Velocidad inicial]
        sol_f = odeint(forced_mas_ode, y0_f, t_f, args=(k_f, m_f, c_f, F0, w_f))
        x_f = sol_f[:, 0]
        
        
        # --- Gráfico de Posición vs. Tiempo ---
        st.subheader("📈 Gráfico de Posición vs. Tiempo")
        fig_forced = go.Figure(data=[
            go.Scatter(x=t_f, y=x_f, mode='lines', name=f'Posición (w_f={w_f} rad/s)', line=dict(color='#F89B2B', width=2))
        ])
        fig_forced.update_layout(
            title=f'MAS Forzado (Frecuencia Natural $\omega_n$ = {omega_n:.2f} rad/s)',
            xaxis_title='Tiempo (s)',
            yaxis_title='Posición (x) [m]',
            template='plotly_white'
        )
        st.plotly_chart(fig_forced, use_container_width=True)

        # --- Animación Visual Forzada ---
        st.subheader("🎬 Animación Visual Forzada")

        def start_forced_animation():
            st.session_state.forced_run = True

        if st.button("▶️ Iniciar Animación Forzada", key="btn_forced_start"):
            start_forced_animation()

        forced_placeholder = st.empty()
        
        # Calcular la amplitud máxima alcanzada para el rango de la visualización
        A_max = np.max(np.abs(x_f))
        range_limit_f = A_max * 1.2
        
        if st.session_state.forced_run:
            st.markdown("Animación en curso. La masa se estabiliza oscilando a la frecuencia forzada.")
            
            # Puntos de la solución ODE para animación (reducidos a 100 puntos)
            t_anim_f = np.linspace(0, T_max_f, 100)
            x_anim_f = np.interp(t_anim_f, t_f, x_f)
            
            for i in range(len(t_anim_f)):
                fig_animation = go.Figure()

                # Anclaje
                fig_animation.add_trace(go.Scatter(
                    x=[-range_limit_f], y=[y_pos], mode='markers', marker=dict(size=10, color='red', symbol='square')
                ))
                # Resorte
                fig_animation.add_trace(go.Scatter(
                    x=[-range_limit_f, x_anim_f[i]], y=[y_pos, y_pos],
                    mode='lines', line=dict(color='gray', width=3, dash='dot')
                ))
                # Masa
                fig_animation.add_trace(go.Scatter(
                    x=[x_anim_f[i]], y=[y_pos],
                    mode='markers', marker=dict(size=30, color='#25447C', symbol='square')
                ))

                fig_animation.update_layout(
                    title=f"MAS Forzado (t={t_anim_f[i]:.2f}s)",
                    xaxis_title='Posición X (m)', yaxis_title='',
                    xaxis_range=[-range_limit_f, range_limit_f], yaxis_range=[-0.5, 0.5], 
                    showlegend=False, template='plotly_white', height=300
                )
                fig_animation.update_yaxes(visible=False) 
                forced_placeholder.plotly_chart(fig_animation, use_container_width=True)
                time.sleep(0.05) 
                
            st.session_state.forced_run = False
            st.success("✅ Simulación forzada completa.")
            
        else:
            # Posición inicial estática
            x_initial = x_f[0]
            fig_initial = go.Figure()
            fig_initial.add_trace(go.Scatter(x=[-range_limit_f], y=[y_pos], mode='markers', marker=dict(size=10, color='red', symbol='square')))
            fig_initial.add_trace(go.Scatter(x=[-range_limit_f, x_initial], y=[y_pos, y_pos], mode='lines', line=dict(color='gray', width=3, dash='dot')))
            fig_initial.add_trace(go.Scatter(x=[x_initial], y=[y_pos], mode='markers', marker=dict(size=30, color='#25447C', symbol='square')))

            fig_initial.update_layout(
                title="Posición Inicial (Forzado)", xaxis_title='Posición X (m)', yaxis_title='',
                xaxis_range=[-range_limit_f, range_limit_f], yaxis_range=[-0.5, 0.5], showlegend=False, template='plotly_white', height=300
            )
            fig_initial.update_yaxes(visible=False)
            forced_placeholder.plotly_chart(fig_initial, use_container_width=True)

        st.subheader("💡 Resonancia")
        
        # CORRECCIÓN DE ROBUSTEZ: Solo mostrar el markdown si omega_n no es el valor inicial de 0.0,
        # lo que implica que el caso "MAS Forzado" está seleccionado y se ha calculado la variable.
        if omega_n > 0.0:
            st.markdown(f"""
            * La **Frecuencia Natural** del sistema es $\omega_n = \sqrt{k/m} = **{omega_n:.2f} \text{ rad/s}**$.
            * Si la frecuencia de la fuerza externa ($\omega_f = **{w_f:.2f} \text{ rad/s}**$) se acerca a $\omega_n$, se produce la **Resonancia**, llevando a un gran incremento en la amplitud de oscilación.
            * Se observa el **régimen transitorio** al inicio y el **régimen estacionario** después de un tiempo, donde la masa oscila a la frecuencia de la fuerza externa.
            """)
        else:
            # Fallback en caso de que k_f o m_f sean 0 o negativos al inicio
            st.markdown("* La Frecuencia Natural se calculará al definir $k$ y $m$ con valores positivos.")


    # ----------------------------------------------------
    # 4.3. Superposición de Oscilaciones
    # ----------------------------------------------------
    elif extended_case == "Superposición de Oscilaciones":
        st.subheader("4.3. Superposición de Oscilaciones")
        st.markdown("Se analiza la suma de dos movimientos armónicos simples con frecuencias y amplitudes diferentes. Se pueden generar los fenómenos de **batido** (Beats).")
        
        st.subheader("🛠️ Parámetros de las Dos Oscilaciones")
        
        # Oscilación 1
        st.markdown("**Oscilación 1 ($x_1$):**")
        col1, col2 = st.columns(2)
        with col1:
            A1 = st.number_input("Amplitud ($A_1$) [m]", value=1.0, min_value=0.1, step=0.1, key="A1")
        with col2:
            w1 = st.number_input("Frecuencia Angular ($\omega_1$) [rad/s]", value=10.0, min_value=0.1, step=0.5, key="w1")
            
        # Oscilación 2
        st.markdown("**Oscilación 2 ($x_2$):**")
        col3, col4 = st.columns(2)
        with col3:
            A2 = st.number_input("Amplitud ($A_2$) [m]", value=1.0, min_value=0.1, step=0.1, key="A2")
        with col4:
            w2 = st.number_input("Frecuencia Angular ($\omega_2$) [rad/s]", value=10.5, min_value=0.1, step=0.5, key="w2")

        T_max_s = st.slider("Tiempo Máximo de Simulación ($t_{max}$) [s] | Superposición", 5.0, 10.0, 8.0, 0.5)
        
        # Simulación
        t_s = np.linspace(0, T_max_s, 1000)
        x1 = A1 * np.cos(w1 * t_s)
        x2 = A2 * np.cos(w2 * t_s)
        x_total = x1 + x2
        
        # --- Gráfico ---
        st.subheader("📈 Gráfico de Superposición")
        fig_super = go.Figure()
        
        fig_super.add_trace(go.Scatter(x=t_s, y=x_total, mode='lines', name='Oscilación Resultante ($x_1+x_2$)', line=dict(color='#25447C', width=2)))
        
        if st.checkbox("Mostrar Oscilaciones Individuales"):
             fig_super.add_trace(go.Scatter(x=t_s, y=x1, mode='lines', name='x1', line=dict(color='#94B34A', width=1, dash='dot')))
             fig_super.add_trace(go.Scatter(x=t_s, y=x2, mode='lines', name='x2', line=dict(color='#F89B2B', width=1, dash='dot')))
        
        fig_super.update_layout(
            title='Superposición de Oscilaciones',
            xaxis_title='Tiempo (s)',
            yaxis_title='Posición (x) [m]',
            template='plotly_white'
        )
        st.plotly_chart(fig_super, use_container_width=True)
        
        st.subheader("💡 Fenómeno de Batido (Beats)")
        if abs(w1 - w2) < 2:
            # CÁLCULO DE w_beat y T_beat (sobrescribe los valores iniciales de 0.0)
            w_beat = abs(w1 - w2)
            T_beat = 2 * np.pi / w_beat
            st.markdown(f"""
            * Si las frecuencias ($\omega_1$ y $\omega_2$) son muy cercanas, se produce el fenómeno de **Batido**.
            * La frecuencia de batido es $\omega_{batido} = |\omega_1 - \omega_2| = **{w_beat:.2f} \text{ rad/s}**$. 
            * Esto se manifiesta como una amplitud que varía lentamente, con un periodo de batido de $T_{batido} \approx **{T_beat:.2f} \text{ s}**$.
            """)
        else:
            st.markdown("* Las frecuencias no son lo suficientemente cercanas para producir un fenómeno de batido claro.")

st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado para Ingeniería Mecánica (UTA)")

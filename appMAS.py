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

# Estilo UTA Mejorado con Fondo de Ingeniería
def apply_custom_style():
    # URL de la imagen de fondo generada por la IA
    BACKGROUND_IMAGE_URL = "https://i.imgur.com/gB36j7J.png" 

    st.markdown(f"""
        <style>
        /* Estilo Principal y Fondo de Ingeniería */
        .main {{
            background-image: url({BACKGROUND_IMAGE_URL});
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
        }}
        /* Asegura que el contenido del Streamlit tenga un fondo blanco/claro para la lectura */
        .stApp {{
            background: rgba(255, 255, 255, 0.9); /* Fondo blanco con 90% de opacidad sobre la imagen */
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}

        /* Sidebar: Mantenemos el color corporativo (Azul Oscuro UTA) para contraste */
        .sidebar .sidebar-content {{
            background-color: #25447C; /* Azul Oscuro UTA */
            color: white;
            padding-top: 20px;
        }}
        
        /* Títulos en Sidebar (para asegurar la legibilidad en blanco) */
        .css-1d391kg, .stRadio label, .stSlider label {{
            color: white !important; 
        }}
        
        /* Botones con estilo Naranja/Amarillo (UTA) */
        .stButton>button {{
            background-color: #F89B2B; /* Naranja UTA */
            color: #25447C; /* Texto Azul Oscuro */
            border: 2px solid #25447C;
            border-radius: 8px;
            font-weight: bold; 
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #FFC064; /* Naranja más claro al pasar el ratón */
            border: 2px solid #25447C;
        }}
        
        /* Títulos Principales (Mejor contraste) */
        h1, h2, h3 {{
            color: #25447C; /* Azul Oscuro UTA */
            border-bottom: 2px solid #F89B2B; /* Línea naranja de separación sutil */
            padding-bottom: 5px;
            margin-top: 15px;
        }}
        .stMarkdown p, .stAlert p {{
            font-size: 1.05em;
            color: #333333; /* Color de texto estándar */
        }}
        
        /* Mejorar la apariencia de los inputs numéricos */
        .stNumberInput div[data-baseweb="input"] input {{
            border-radius: 8px;
            border: 1px solid #ccc;
        }}

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
        st.success("✅ Simulación completa. Ajuste los parámetros y vuelve a presionar el botón para reiniciar.")

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
            xaxis_title='Posición X (m)',
            yaxis_title='',
            xaxis_range=[-range_limit, range_limit],
            yaxis_range=[-0.5, 0.5], 
            showlegend=False,
            template='plotly_white',
            height=300
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
    * **Aumento de $k$ (Constante Elástica):** Aumenta la **rigidez** del resistema. Esto **disminuye el periodo ($T$)** y aumenta la frecuencia.
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
    
    # INICIALIZACIÓN DE VARIABLES CRÍTICAS 
    y_pos = 0 
    
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
            c_d = st.

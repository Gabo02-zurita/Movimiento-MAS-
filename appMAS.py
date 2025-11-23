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
        
        # CÁLCULO DE omega_n
        if m_f > 0 and k_f > 0:
            omega_n = np.sqrt(k_f / m_f)
        else:
            omega_n = 0.0 
        
        # Simulación
        t_f = np.linspace(0, T_max_f, 1000)
        y0_f = [0.0, 0.0]  # [Posición inicial, Velocidad inicial]
        sol_f = odeint(forced_mas_ode, y0_f, t_f, args=(k_f, m_f, c_f, F0, w_f))
        x_f = sol_f[:, 0]
        
        
        # --- Gráfico de Posición vs. Tiempo ---
        st.subheader("📈 Gráfico de Posición vs. Tiempo")
        
        title_forced = f'MAS Forzado (Frecuencia Natural $\omega_n$ = {omega_n:.2f} rad/s)'
        if omega_n == 0.0:
            title_forced = 'MAS Forzado (Frecuencia Natural no definida/cero)'
            
        fig_forced = go.Figure(data=[
            go.Scatter(x=t_f, y=x_f, mode='lines', name=f'Posición (w_f={w_f} rad/s)', line=dict(color='#F89B2B', width=2))
        ])
        fig_forced.update_layout(
            title=title_forced,
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
        
        # Uso de str.format() para evitar el NameError en la inicialización de la f-string
        if omega_n > 0.0:
            
            # Texto a mostrar (usando str.format para asegurar la evaluación tardía)
            resonance_text = """
* La **Frecuencia Natural** del sistema es $\omega_n = \sqrt{{k/m}} = **{omega_n:.2f} \text{{ rad/s}}**$.
* Si la frecuencia de la fuerza externa ($\omega_f = **{w_f:.2f} \text{{ rad/s}}**$) se acerca a $\omega_n$, se produce la **Resonancia**, llevando a un gran incremento en la amplitud de oscilación.
* Se observa el **régimen transitorio** al inicio y el **régimen estacionario** después de un tiempo, donde la masa oscila a la frecuencia de la fuerza externa.
            """.format(omega_n=omega_n, w_f=w_f)
        
        else:
            # Texto de fallback si los parámetros no son válidos (k<=0 o m<=0)
            resonance_text = """
* La Frecuencia Natural ($\omega_n$) no se puede calcular. Por favor, asegúrese de que la Masa ($m$) y la Constante Elástica ($k$) sean mayores que cero.
            """
        
        st.markdown(resonance_text) # Mostramos el texto generado condicionalmente.

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
            # CÁLCULO DE w_beat y T_beat
            w_beat = abs(w1 - w2)
            if w_beat != 0:
                T_beat = 2 * np.pi / w_beat
            else:
                T_beat = 99999.0 # Valor grande en lugar de infinito para el formateo
                
            st.markdown(f"""
* Si las frecuencias ($\omega_1$ y $\omega_2$) son muy cercanas, se produce el fenómeno de **Batido**. 
* La frecuencia de batido es $\omega_{batido} = |\omega_1 - \omega_2| = **{w_beat:.2f} \text{{ rad/s}}**$. 
* Esto se manifiesta como una amplitud que varía lentamente, con un periodo de batido de $T_{batido} \approx **{T_beat:.2f} \text{{ s}}**$.
            """)
        else:
            st.markdown("* Las frecuencias no son lo suficientemente cercanas para producir un fenómeno de batido claro.")

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

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
from io import BytesIO

# Set page config
st.set_page_config(page_title="TCP Congestion Control Simulator", layout="wide")

# Title and description
st.title("TCP Congestion Control Simulator")
st.markdown("""
This simulator demonstrates the behavior of TCP Tahoe and Reno congestion control algorithms.
Adjust the parameters below to see how each algorithm responds to packet loss.
""")

# Sidebar controls
with st.sidebar:
    st.header("Simulation Parameters")
    simulation_time = st.slider("Simulation Time (RTTs)", 10, 100, 50)
    loss_probability = st.slider("Packet Loss Probability (%)", 1, 30, 10)
    initial_window = st.slider("Initial Window Size", 1, 10, 1)
    threshold = st.slider("Initial Threshold", 5, 30, 16)
    seed = st.number_input("Random Seed", value=42)
    
    st.markdown("---")
    st.markdown("**Algorithm Selection**")
    show_tahoe = st.checkbox("Show TCP Tahoe", value=True)
    show_reno = st.checkbox("Show TCP Reno", value=True)
    
    st.markdown("---")
    st.markdown("**Visualization Options**")
    show_individual = st.checkbox("Show Individual Plots", value=False)
    show_combined = st.checkbox("Show Combined Plot", value=True)
    
    if st.button("Run Simulation"):
        st.session_state.run_simulation = True

# Initialize session state
if 'run_simulation' not in st.session_state:
    st.session_state.run_simulation = False

# TCP Congestion Control Algorithms
def tcp_tahoe(cwnd, ssthresh, packet_loss):
    if packet_loss:
        ssthresh = max(cwnd // 2, 2)
        cwnd = 1
        return cwnd, ssthresh, "Timeout"
    elif cwnd < ssthresh:
        cwnd *= 2  # Slow start
        return cwnd, ssthresh, "Slow Start"
    else:
        cwnd += 1  # Congestion avoidance
        return cwnd, ssthresh, "Congestion Avoidance"

def tcp_reno(cwnd, ssthresh, packet_loss, in_fast_recovery=False, dup_acks=0):
    if packet_loss:
        if dup_acks >= 3:  # Fast retransmit
            ssthresh = max(cwnd // 2, 2)
            cwnd = ssthresh + 3
            return cwnd, ssthresh, "Fast Recovery", True, dup_acks
        else:  # Timeout
            ssthresh = max(cwnd // 2, 2)
            cwnd = 1
            return cwnd, ssthresh, "Timeout", False, 0
    elif in_fast_recovery:
        cwnd += 1  # Fast recovery
        return cwnd, ssthresh, "Fast Recovery", True, dup_acks
    elif cwnd < ssthresh:
        cwnd *= 2  # Slow start
        return cwnd, ssthresh, "Slow Start", False, dup_acks
    else:
        cwnd += 1  # Congestion avoidance
        return cwnd, ssthresh, "Congestion Avoidance", False, dup_acks

# Run simulation when button is pressed
if st.session_state.run_simulation:
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Initialize variables
    time_steps = range(simulation_time)
    results = {"Tahoe": {"cwnd": [], "state": [], "ssthresh": []}, 
               "Reno": {"cwnd": [], "state": [], "ssthresh": []}}
    
    # Initial conditions
    cwnd_tahoe = initial_window
    ssthresh_tahoe = threshold
    
    cwnd_reno = initial_window
    ssthresh_reno = threshold
    in_fast_recovery = False
    dup_acks = 0
    
    # Run simulation
    for t in time_steps:
        # Simulate packet loss (10% probability)
        loss = random.random() < (loss_probability / 100)
        
        # For Reno, simulate duplicate ACKs (3 needed for fast retransmit)
        if loss and random.random() < 0.7:  # 70% chance of dup ack vs timeout
            dup_acks += 1
        else:
            dup_acks = 0
        
        # TCP Tahoe
        if show_tahoe:
            cwnd_tahoe, ssthresh_tahoe, state = tcp_tahoe(cwnd_tahoe, ssthresh_tahoe, loss)
            results["Tahoe"]["cwnd"].append(cwnd_tahoe)
            results["Tahoe"]["state"].append(state)
            results["Tahoe"]["ssthresh"].append(ssthresh_tahoe)
        
        # TCP Reno
        if show_reno:
            cwnd_reno, ssthresh_reno, state, in_fast_recovery, dup_acks = tcp_reno(
                cwnd_reno, ssthresh_reno, loss, in_fast_recovery, dup_acks)
            results["Reno"]["cwnd"].append(cwnd_reno)
            results["Reno"]["state"].append(state)
            results["Reno"]["ssthresh"].append(ssthresh_reno)
    
    # Create plots
    if show_individual:
        cols = st.columns(2)
        
        if show_tahoe:
            with cols[0]:
                st.subheader("TCP Tahoe")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(time_steps, results["Tahoe"]["cwnd"], label="Congestion Window")
                ax.plot(time_steps, results["Tahoe"]["ssthresh"], 'r--', label="Slow Start Threshold")
                
                # Mark loss events
                loss_indices = [i for i, state in enumerate(results["Tahoe"]["state"]) if "Timeout" in state]
                for idx in loss_indices:
                    ax.axvline(x=idx, color='gray', linestyle=':', alpha=0.5)
                
                ax.set_xlabel("Time (RTTs)")
                ax.set_ylabel("Window Size (packets)")
                ax.set_title("TCP Tahoe Congestion Window")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)
                
                # Add state information
                st.markdown("**States:**")
                states = ", ".join(set(results["Tahoe"]["state"]))
                st.markdown(f"`{states}`")
        
        if show_reno:
            with cols[1]:
                st.subheader("TCP Reno")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(time_steps, results["Reno"]["cwnd"], label="Congestion Window")
                ax.plot(time_steps, results["Reno"]["ssthresh"], 'r--', label="Slow Start Threshold")
                
                # Mark loss events
                loss_indices = [i for i, state in enumerate(results["Reno"]["state"]) if "Timeout" in state or "Fast" in state]
                for idx in loss_indices:
                    ax.axvline(x=idx, color='gray', linestyle=':', alpha=0.5)
                
                ax.set_xlabel("Time (RTTs)")
                ax.set_ylabel("Window Size (packets)")
                ax.set_title("TCP Reno Congestion Window")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)
                
                # Add state information
                st.markdown("**States:**")
                states = ", ".join(set(results["Reno"]["state"]))
                st.markdown(f"`{states}`")
    
    if show_combined and show_tahoe and show_reno:
        st.subheader("Comparison of TCP Tahoe and Reno")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(time_steps, results["Tahoe"]["cwnd"], label="TCP Tahoe Window")
        ax.plot(time_steps, results["Tahoe"]["ssthresh"], 'r:', label="Tahoe Threshold")
        
        ax.plot(time_steps, results["Reno"]["cwnd"], 'g', label="TCP Reno Window")
        ax.plot(time_steps, results["Reno"]["ssthresh"], 'g:', label="Reno Threshold")
        
        # Mark loss events
        tahoe_loss = [i for i, state in enumerate(results["Tahoe"]["state"]) if "Timeout" in state]
        reno_loss = [i for i, state in enumerate(results["Reno"]["state"]) if "Timeout" in state or "Fast" in state]
        
        for idx in tahoe_loss:
            ax.axvline(x=idx, color='blue', linestyle=':', alpha=0.3)
        for idx in reno_loss:
            ax.axvline(x=idx, color='green', linestyle=':', alpha=0.3)
        
        ax.set_xlabel("Time (RTTs)")
        ax.set_ylabel("Window Size (packets)")
        ax.set_title("TCP Congestion Control Algorithms Comparison")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
    
    # Analysis section
    st.subheader("Performance Analysis")
    
    if show_tahoe and show_reno:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**TCP Tahoe**")
            avg_window = np.mean(results["Tahoe"]["cwnd"])
            st.metric("Average Window Size", f"{avg_window:.2f} packets")
            
            timeouts = results["Tahoe"]["state"].count("Timeout")
            st.metric("Timeout Events", timeouts)
        
        with col2:
            st.markdown("**TCP Reno**")
            avg_window = np.mean(results["Reno"]["cwnd"])
            st.metric("Average Window Size", f"{avg_window:.2f} packets")
            
            timeouts = results["Reno"]["state"].count("Timeout")
            fast_recovery = results["Reno"]["state"].count("Fast Recovery")
            st.metric("Timeout Events", timeouts)
            st.metric("Fast Recovery Events", fast_recovery)
    
    # Download results
    st.markdown("---")
    st.subheader("Export Results")
    
    # Create a downloadable plot
    if show_combined and show_tahoe and show_reno:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(time_steps, results["Tahoe"]["cwnd"], label="TCP Tahoe Window")
        ax.plot(time_steps, results["Reno"]["cwnd"], 'g', label="TCP Reno Window")
        ax.set_xlabel("Time (RTTs)")
        ax.set_ylabel("Window Size (packets)")
        ax.set_title("TCP Congestion Control Comparison")
        ax.legend()
        ax.grid(True)
        
        buf = BytesIO()
        fig.savefig(buf, format="png")
        st.download_button(
            label="Download Comparison Plot",
            data=buf.getvalue(),
            file_name="tcp_comparison.png",
            mime="image/png"
        )
    
    # Explanation of results
    st.markdown("---")
    st.subheader("Algorithm Behavior Explanation")
    
    st.markdown("""
    **TCP Tahoe**:
    - When packet loss is detected (via timeout), Tahoe:
      1. Sets the slow start threshold (ssthresh) to half the current window size
      2. Resets the congestion window (cwnd) to 1 packet
      3. Enters slow start phase
    - Grows exponentially (cwnd *= 2) during slow start until ssthresh is reached
    - Then grows linearly (cwnd += 1) during congestion avoidance
    
    **TCP Reno**:
    - Similar to Tahoe but adds Fast Retransmit/Fast Recovery:
      1. After 3 duplicate ACKs (indicating packet loss but some packets getting through):
        - Sets ssthresh to half the current window
        - Retransmits the lost packet without waiting for timeout
        - Continues transmitting new packets if allowed by window
      2. Only resets to slow start on timeout (like Tahoe)
    """)
    
    st.markdown("""
    **Key Differences**:
    - Reno generally performs better in environments with random packet loss
    - Tahoe is more aggressive in reducing congestion but may underutilize bandwidth
    - Reno's Fast Recovery helps maintain higher throughput during temporary packet loss
    """)

# Initial state before running simulation
else:
    st.info("Configure the simulation parameters in the sidebar and click 'Run Simulation' to start.")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Tcp.png/800px-Tcp.png", 
             caption="TCP Congestion Window Behavior (Source: Wikipedia)")
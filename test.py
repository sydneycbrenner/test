import streamlit as st
import pickle
from itertools import product
import os
import time  # For simulating processing

def generate_model_keys(implementations, leverages):
    """Generate all combinations of implementations and leverages"""
    return [f"{impl}_{lev}" for impl, lev in product(implementations, leverages)]

def save_parameters(params, filename='parameters.pkl'):
    """Save parameters to pickle file"""
    with open(filename, 'wb') as f:
        pickle.dump(params, f)
    return os.path.abspath(filename)

def load_parameters(filename='parameters.pkl'):
    """Load parameters from pickle file"""
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return None

def summarize_parameters():
    """Simulate parameter summarization"""
    # This is a placeholder - replace with your actual summarization logic
    time.sleep(2)  # Simulate processing
    return True

def main():
    st.set_page_config(layout="wide")  # Use wide layout for landscape mode
    st.title("Model Configuration Tool")
    
    # Initialize session states
    if 'run_status' not in st.session_state:
        st.session_state.run_status = {}
    if 'custom_implementations' not in st.session_state:
        st.session_state.custom_implementations = [""]
    if 'custom_leverages' not in st.session_state:
        st.session_state.custom_leverages = [""]
    if 'frontier_points' not in st.session_state:
        st.session_state.frontier_points = [{"key": "", "value": ""}]
    
    # Create three main columns for layout
    col1, col2, col3, col4 = st.columns(4)
    
    # Predefined options
    universe_options = ["US", "UK", "EU", "GLOBAL", "APAC", "LATAM", "EMEA"]
    environment_options = ["PROD", "UAT", "DEV", "TEST"]
    MODEL_IMPLEMENTATIONS = ["RC", "LS", "BLS", "CLS"]
    MODEL_LEVERAGES = ["EDI", "AE", "AEP", "AEPP", "AEPPP"]
    
    # Column 1: Basic Configuration
    with col1:
        st.header("1. Basic Configuration")
        
        universe = st.multiselect("UNIVERSE", options=universe_options, default=None)
        db_table = st.text_input("DB TABLE")
        environment = st.selectbox("ENVIRONMENT", options=environment_options)
        backtest_user = st.text_input("BACKTEST USER")
        
        st.subheader("START YEARS")
        year_col1, year_col2 = st.columns(2)
        with year_col1:
            start_year_begin = st.number_input("Begin", min_value=1900, max_value=2100, value=2020)
        with year_col2:
            start_year_end = st.number_input("End", min_value=1900, max_value=2100, value=2024)
        start_years = f"{start_year_begin}-{start_year_end}"
        
        st.subheader("MODEL KEYS")
        
        # Model Implementations
        st.write("**Implementations:**")
        selected_implementations = []
        for impl in MODEL_IMPLEMENTATIONS:
            if st.checkbox(impl, key=f"impl_{impl}"):
                selected_implementations.append(impl)
                
        # Model Leverages
        st.write("**Leverages:**")
        selected_leverages = []
        for lev in MODEL_LEVERAGES:
            if st.checkbox(lev, key=f"lev_{lev}"):
                selected_leverages.append(lev)
                
        # Generate model keys
        model_keys = generate_model_keys(selected_implementations, selected_leverages)
        if model_keys:
            st.write("**Generated Keys:**")
            st.write(", ".join(model_keys))

    # Column 2: Frontier Points
    with col2:
        st.header("2. Frontier Points")
        
        for i in range(len(st.session_state.frontier_points)):
            point = st.session_state.frontier_points[i]
            
            # Create unique key for status tracking
            status_key = f"frontier_point_{i}"
            if status_key not in st.session_state.run_status:
                st.session_state.run_status[status_key] = "pending"
            
            cols = st.columns([2, 2, 1])
            with cols[0]:
                point["key"] = st.text_input("Key", key=f"frontier_key_{i}")
            with cols[1]:
                point["value"] = st.text_input("Value", key=f"frontier_value_{i}")
            with cols[2]:
                if i > 0:
                    if st.button(f"Remove", key=f"remove_point_{i}"):
                        st.session_state.frontier_points.pop(i)
                        st.rerun()
        
        if st.button("Add Frontier Point"):
            st.session_state.frontier_points.append({"key": "", "value": ""})
            st.rerun()

    # Column 3: String Format Builder
    with col3:
        st.header("3. String Format Builder")
        
        variables = {
            "UNIVERSE": ", ".join(universe) if universe else "",
            "DB_TABLE": db_table,
            "ENVIRONMENT": environment,
            "BACKTEST_USER": backtest_user,
            "MODEL_KEYS": ", ".join(model_keys),
            "START_YEARS": start_years
        }
        
        # Add frontier points to variables
        for point in st.session_state.frontier_points:
            if point["key"] and point["value"]:
                variables[f"FRONTIER_{point['key']}"] = point["value"]
        
        template = st.text_area(
            "Template string",
            "Example: Model for {UNIVERSE} in {ENVIRONMENT}"
        )
        
        selected_vars = st.multiselect(
            "Variables to include",
            list(variables.keys())
        )
        
        if st.button("Preview"):
            try:
                format_dict = {k: variables[k] for k in selected_vars if k in variables}
                formatted_string = template.format(**format_dict)
                st.success("Formatted String:")
                st.write(formatted_string)
            except KeyError as e:
                st.error(f"Error: Missing variable {e}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Column 4: Run Summarization
    with col4:
        st.header("4. Run Summarization")
        
        # Collect all parameters
        parameters = {
            "universe": universe,
            "db_table": db_table,
            "environment": environment,
            "backtest_user": backtest_user,
            "start_years": start_years,
            "model_keys": model_keys,
            "frontier_points": st.session_state.frontier_points
        }
        
        if st.button("Run Summarization"):
            # Save parameters
            filepath = save_parameters(parameters)
            st.write(f"Parameters saved to: {filepath}")
            
            # Update status for all points to processing
            for key in st.session_state.run_status:
                st.session_state.run_status[key] = "processing"
            
            # Run summarization
            success = summarize_parameters()
            
            # Update status based on result
            for key in st.session_state.run_status:
                st.session_state.run_status[key] = "completed" if success else "failed"
        
        # Display status for each point
        st.subheader("Processing Status")
        for i, point in enumerate(st.session_state.frontier_points):
            status_key = f"frontier_point_{i}"
            status = st.session_state.run_status.get(status_key, "pending")
            
            # Status colors
            status_colors = {
                "pending": "🟧",  # Orange
                "processing": "🟧",  # Orange
                "completed": "🟩",  # Green
                "failed": "🟥"  # Red
            }
            
            st.write(f"{status_colors[status]} Point {i+1}: {point['key']} - {status}")

if __name__ == "__main__":
    main()

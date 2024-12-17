import streamlit as st
import pickle
import os
from itertools import product
import time

# Constants
UNIVERSE_OPTIONS = ["US", "UK", "EU", "GLOBAL", "APAC", "LATAM", "EMEA"]
ENVIRONMENT_OPTIONS = ["PROD", "UAT", "DEV", "TEST"]
MODEL_IMPLEMENTATIONS = ["RC", "LS", "BLS", "CLS"]
MODEL_LEVERAGES = ["EDI", "AE", "AEP", "AEPP", "AEPPP"]

def generate_model_keys(implementations, leverages):
    """Generate all combinations of implementations and leverages"""
    return [f"{impl}_{lev}" for impl, lev in product(implementations, leverages)]

def check_existing_config(db_table):
    """Check if configuration already exists for the given table"""
    filename = f"{db_table}_config.pkl"
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            existing_config = pickle.load(f)
        return True, existing_config
    return False, None

def save_parameters(params, db_table):
    """Save parameters to pickle file"""
    filename = f"{db_table}_config.pkl"
    with open(filename, 'wb') as f:
        pickle.dump(params, f)
    return os.path.abspath(filename)

def summarize_parameters(on_cluster=False):
    """Simulate parameter summarization"""
    time.sleep(2)
    return True

def generate_example_strings(template, universes, years, model_keys, frontier_points):
    """Generate example strings for each configuration"""
    examples = []
    if not universes or not model_keys:
        return examples
    
    # Take first instance of each parameter for example
    universe = universes[0]
    start_year, end_year = map(int, years.split('-'))
    year = str(start_year)
    model_key = list(model_keys)[0]
    
    # Base variables
    variables = {
        "UNIVERSE": universe,
        "YEAR": year,
        "MODEL_KEY": model_key
    }
    
    # Add frontier points
    for point in frontier_points:
        if point["key"] and "points" in point:
            variables[f"FRONTIER_{point['key']}"] = ", ".join(point["points"])
    
    try:
        example = template.format(**variables)
        examples.append(example)
        
        # Add one more example with different values if available
        if len(universes) > 1 or len(model_keys) > 1 or start_year != end_year:
            variables["UNIVERSE"] = universes[-1] if len(universes) > 1 else universe
            variables["YEAR"] = str(end_year) if start_year != end_year else year
            variables["MODEL_KEY"] = list(model_keys)[-1] if len(model_keys) > 1 else model_key
            examples.append(template.format(**variables))
    except KeyError as e:
        st.error(f"Error in template: Missing variable {e}")
    
    return examples

def main():
    st.set_page_config(layout="wide")
    st.title("Model Configuration Tool")
    
    # Initialize session states
    if 'run_status' not in st.session_state:
        st.session_state.run_status = {}
    if 'frontier_points' not in st.session_state:
        st.session_state.frontier_points = []
    if 'selected_model_keys' not in st.session_state:
        st.session_state.selected_model_keys = set()
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Column 1: Basic Configuration
    with col1:
        st.header("1. Basic Configuration")
        
        universe = st.multiselect("UNIVERSE", options=UNIVERSE_OPTIONS, default=None)
        db_table = st.text_input("DB TABLE")
        
        # Check for existing configuration
        if db_table:
            exists, existing_config = check_existing_config(db_table)
            if exists:
                st.warning(
                    f"{db_table} already exists in Omnitron with the following "
                    f"frontier points, leverage levels, and models:\n\n"
                    f"{existing_config}\n\n"
                    "Click 'Proceed' to add additional data."
                )
                if not st.button("Proceed"):
                    st.stop()
        
        environment = st.selectbox("ENVIRONMENT", options=ENVIRONMENT_OPTIONS)
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
        
        # Generate and display model keys with removal option
        model_keys = generate_model_keys(selected_implementations, selected_leverages)
        if model_keys:
            st.write("**Generated Keys:**")
            for key in model_keys:
                key_col1, key_col2 = st.columns([3, 1])
                with key_col1:
                    if st.checkbox(key, value=key in st.session_state.selected_model_keys, 
                                 key=f"select_{key}"):
                        st.session_state.selected_model_keys.add(key)
                    else:
                        st.session_state.selected_model_keys.discard(key)

    # Column 2: Frontier Points
    with col2:
        st.header("2. Frontier Points")
        
        # Add new frontier point section
        st.subheader("Add New Frontier Point")
        new_frontier_name = st.text_input("FRONTIER NAME")
        new_frontier_point = st.text_input("FRONTIER POINTS")
        
        if st.button("Add Point") and new_frontier_name and new_frontier_point:
            # Find existing frontier point or create new one
            found = False
            for point in st.session_state.frontier_points:
                if point["key"] == new_frontier_name:
                    if new_frontier_point not in point["points"]:
                        point["points"].append(new_frontier_point)
                    found = True
                    break
            
            if not found:
                st.session_state.frontier_points.append({
                    "key": new_frontier_name,
                    "points": [new_frontier_point]
                })
            st.rerun()
        
        # Display existing frontier points
        for i, point in enumerate(st.session_state.frontier_points):
            st.write(f"**{point['key']}**")
            point_cols = st.columns(4)
            for j, frontier_point in enumerate(point["points"]):
                col_idx = j % 4
                with point_cols[col_idx]:
                    bubble_cols = st.columns([3, 1])
                    with bubble_cols[0]:
                        st.info(frontier_point)
                    with bubble_cols[1]:
                        if st.button("×", key=f"remove_{point['key']}_{j}"):
                            point["points"].remove(frontier_point)
                            if not point["points"]:
                                st.session_state.frontier_points.remove(point)
                            st.rerun()

    # Column 3: String Format Builder
    with col3:
        st.header("3. String Format Builder")
        
        template = st.text_area(
            "Template string",
            "Example: {MODEL_KEY} for {UNIVERSE} in {YEAR}"
        )
        
        st.subheader("Example Configurations")
        examples = generate_example_strings(
            template, 
            universe, 
            start_years, 
            st.session_state.selected_model_keys,
            st.session_state.frontier_points
        )
        
        for i, example in enumerate(examples, 1):
            st.write(f"Example {i}:")
            st.success(example)

    # Column 4: Run Summarization
    with col4:
        st.header("4. Run Summarization")
        
        # Add cluster option
        run_on_cluster = st.checkbox("Summarize on cluster", value=False)
        
        # Collect all parameters
        parameters = {
            "universe": universe,
            "db_table": db_table,
            "environment": environment,
            "backtest_user": backtest_user,
            "start_years": start_years,
            "model_keys": list(st.session_state.selected_model_keys),
            "frontier_points": st.session_state.frontier_points,
            "run_on_cluster": run_on_cluster
        }
        
        if st.button("Run Summarization"):
            # Save parameters
            if db_table:
                filepath = save_parameters(parameters, db_table)
                st.write(f"Parameters saved to: {filepath}")
                
                # Update status for all points to processing
                for point in st.session_state.frontier_points:
                    for _ in point["points"]:
                        status_key = f"frontier_{point['key']}"
                        st.session_state.run_status[status_key] = "processing"
                
                # Run summarization
                success = summarize_parameters(run_on_cluster)
                
                # Update status based on result
                for key in st.session_state.run_status:
                    st.session_state.run_status[key] = "completed" if success else "failed"
            else:
                st.error("Please enter a DB TABLE name")
        
        # Display status for each point
        st.subheader("Processing Status")
        for point in st.session_state.frontier_points:
            status_key = f"frontier_{point['key']}"
            status = st.session_state.run_status.get(status_key, "pending")
            
            status_colors = {
                "pending": "🟧",
                "processing": "🟧",
                "completed": "🟩",
                "failed": "🟥"
            }
            
            st.write(f"{status_colors[status]} {point['key']}: {status}")

if __name__ == "__main__":
    main()

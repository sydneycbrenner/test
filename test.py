import streamlit as st
from itertools import product

def generate_model_keys(implementations, leverages):
    """Generate all combinations of implementations and leverages"""
    return [f"{impl}_{lev}" for impl, lev in product(implementations, leverages)]

def main():
    st.title("Model Configuration Tool")
    
    # Predefined options
    universe_options = ["US", "UK", "EU", "GLOBAL", "APAC", "LATAM", "EMEA"]
    environment_options = ["PROD", "UAT", "DEV", "TEST"]
    
    # Model implementation and leverage options
    MODEL_IMPLEMENTATIONS = ["RC", "LS", "BLS", "CLS"]
    MODEL_LEVERAGES = ["EDI", "AE", "AEP", "AEPP", "AEPPP"]
    
    # Basic Configuration
    st.header("1. Basic Configuration")
    
    # First row of basic config
    col1, col2 = st.columns(2)
    with col1:
        universe = st.multiselect(
            "UNIVERSE",
            options=universe_options,
            default=None,
            help="Select one or more universes"
        )
        db_table = st.text_input("DB TABLE")
        environment = st.selectbox(
            "ENVIRONMENT",
            options=environment_options,
            help="Select the environment"
        )
    
    with col2:
        backtest_user = st.text_input("BACKTEST USER")
        
        # Start Years
        st.subheader("START YEARS")
        year_col1, year_col2 = st.columns(2)
        with year_col1:
            start_year_begin = st.number_input(
                "Begin Year",
                min_value=1900,
                max_value=2100,
                value=2020,
                step=1
            )
        with year_col2:
            start_year_end = st.number_input(
                "End Year",
                min_value=1900,
                max_value=2100,
                value=2024,
                step=1
            )
        start_years = f"{start_year_begin}-{start_year_end}"
    
    # Model Keys Section
    st.subheader("MODEL KEYS")
    
    # Initialize session state
    if 'custom_implementations' not in st.session_state:
        st.session_state.custom_implementations = [""]
    if 'custom_leverages' not in st.session_state:
        st.session_state.custom_leverages = [""]
    
    # Two columns for implementations and leverages
    imp_col, lev_col = st.columns(2)
    
    # Implementations column
    with imp_col:
        st.write("**Model Implementations**")
        selected_implementations = []
        
        # Predefined implementations
        for impl in MODEL_IMPLEMENTATIONS:
            if st.checkbox(impl, key=f"impl_{impl}"):
                selected_implementations.append(impl)
        
        # Custom implementations
        st.write("**Custom Implementations:**")
        
        # Handle custom implementations
        for i in range(len(st.session_state.custom_implementations)):
            value = st.text_input(f"Custom Impl {i+1}", key=f"custom_impl_{i}")
            if value:
                selected_implementations.append(value)
            
            if i > 0:  # Only show remove button if not the first input
                if st.button(f"Remove Implementation {i+1}", key=f"remove_impl_{i}"):
                    st.session_state.custom_implementations.pop(i)
                    st.experimental_rerun()
        
        if st.button("Add Custom Implementation"):
            st.session_state.custom_implementations.append("")
            st.experimental_rerun()
    
    # Leverages column
    with lev_col:
        st.write("**Model Leverages**")
        selected_leverages = []
        
        # Predefined leverages
        for lev in MODEL_LEVERAGES:
            if st.checkbox(lev, key=f"lev_{lev}"):
                selected_leverages.append(lev)
        
        # Custom leverages
        st.write("**Custom Leverages:**")
        
        # Handle custom leverages
        for i in range(len(st.session_state.custom_leverages)):
            value = st.text_input(f"Custom Lev {i+1}", key=f"custom_lev_{i}")
            if value:
                selected_leverages.append(value)
            
            if i > 0:  # Only show remove button if not the first input
                if st.button(f"Remove Leverage {i+1}", key=f"remove_lev_{i}"):
                    st.session_state.custom_leverages.pop(i)
                    st.experimental_rerun()
        
        if st.button("Add Custom Leverage"):
            st.session_state.custom_leverages.append("")
            st.experimental_rerun()
    
    # Generate and display model keys
    model_keys = generate_model_keys(selected_implementations, selected_leverages)
    if model_keys:
        st.write("**Generated Model Keys:**")
        st.write(", ".join(model_keys))
    
    # Frontier Points Section
    st.header("2. Frontier Points")
    
    # Initialize frontier points
    if 'frontier_points' not in st.session_state:
        st.session_state.frontier_points = [{"key": "", "value": ""}]
    
    # Handle frontier points
    for i in range(len(st.session_state.frontier_points)):
        cols = st.columns([2, 2, 1])
        with cols[0]:
            st.session_state.frontier_points[i]["key"] = st.text_input("Key", key=f"frontier_key_{i}")
        with cols[1]:
            st.session_state.frontier_points[i]["value"] = st.text_input("Value", key=f"frontier_value_{i}")
        with cols[2]:
            if i > 0:  # Only show remove button if not the first point
                if st.button(f"Remove Point {i+1}", key=f"remove_point_{i}"):
                    st.session_state.frontier_points.pop(i)
                    st.experimental_rerun()
    
    if st.button("Add Frontier Point"):
        st.session_state.frontier_points.append({"key": "", "value": ""})
        st.experimental_rerun()
    
    # String Formatting Section
    st.header("3. String Format Builder")
    
    # Create variables dictionary
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
    
    # Template input
    template = st.text_area(
        "Enter your template string using {variable_name} for placeholders",
        "Example: Model for {UNIVERSE} in {ENVIRONMENT} from {START_YEARS} using {MODEL_KEYS}"
    )
    
    # Variable selection
    selected_vars = st.multiselect(
        "Choose variables to include in formatting",
        list(variables.keys())
    )
    
    # Preview formatted string
    if st.button("Preview Formatted String"):
        try:
            format_dict = {k: variables[k] for k in selected_vars if k in variables}
            formatted_string = template.format(**format_dict)
            st.success("Formatted String:")
            st.write(formatted_string)
        except KeyError as e:
            st.error(f"Error: Missing variable {e} in template")
        except Exception as e:
            st.error(f"Error formatting string: {str(e)}")
    
    # Debug view
    if st.checkbox("Show current values"):
        st.json(variables)

if __name__ == "__main__":
    main()

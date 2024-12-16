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
    
    # Section 1: Basic Variables
    st.header("1. Basic Configuration")
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
        
        # Model Keys Section
        st.subheader("MODEL KEYS")
        
        # Initialize session state for custom entries if not exists
        if 'custom_implementations' not in st.session_state:
            st.session_state.custom_implementations = [""]
        if 'custom_leverages' not in st.session_state:
            st.session_state.custom_leverages = [""]
            
        # Create two columns for implementations and leverages
        impl_col, lev_col = st.columns(2)
        
        with impl_col:
            st.write("**Model Implementations**")
            # Checkboxes for predefined implementations
            selected_implementations = []
            for impl in MODEL_IMPLEMENTATIONS:
                if st.checkbox(impl, key=f"impl_{impl}"):
                    selected_implementations.append(impl)
            
            # Custom implementation inputs
            st.write("Custom Implementations:")
            
            def add_custom_impl():
                st.session_state.custom_implementations.append("")
                
            def remove_custom_impl(index):
                st.session_state.custom_implementations.pop(index)
            
            # Display custom implementation inputs
            for i, custom_impl in enumerate(st.session_state.custom_implementations):
                col1, col2 = st.columns([4, 1])
                with col1:
                    value = st.text_input(
                        f"Custom Impl {i+1}",
                        value=custom_impl,
                        key=f"custom_impl_{i}"
                    )
                    if value:  # Only add non-empty values
                        selected_implementations.append(value)
                with col2:
                    if len(st.session_state.custom_implementations) > 1 and st.button("×", key=f"remove_impl_{i}"):
                        remove_custom_impl(i)
                        st.experimental_rerun()
            
            if st.button("Add Custom Implementation"):
                add_custom_impl()
                st.experimental_rerun()
                
        with lev_col:
            st.write("**Model Leverages**")
            # Checkboxes for predefined leverages
            selected_leverages = []
            for lev in MODEL_LEVERAGES:
                if st.checkbox(lev, key=f"lev_{lev}"):
                    selected_leverages.append(lev)
            
            # Custom leverage inputs
            st.write("Custom Leverages:")
            
            def add_custom_lev():
                st.session_state.custom_leverages.append("")
                
            def remove_custom_lev(index):
                st.session_state.custom_leverages.pop(index)
            
            # Display custom leverage inputs
            for i, custom_lev in enumerate(st.session_state.custom_leverages):
                col1, col2 = st.columns([4, 1])
                with col1:
                    value = st.text_input(
                        f"Custom Lev {i+1}",
                        value=custom_lev,
                        key=f"custom_lev_{i}"
                    )
                    if value:  # Only add non-empty values
                        selected_leverages.append(value)
                with col2:
                    if len(st.session_state.custom_leverages) > 1 and st.button("×", key=f"remove_lev_{i}"):
                        remove_custom_lev(i)
                        st.experimental_rerun()
            
            if st.button("Add Custom Leverage"):
                add_custom_lev()
                st.experimental_rerun()
        
        # Generate all model key combinations
        model_keys = generate_model_keys(selected_implementations, selected_leverages)
        
        # Display preview of generated keys
        if model_keys:
            st.write("**Generated Model Keys:**")
            st.write(", ".join(model_keys))
        
        # Start Years as two integers
        st.subheader("START YEARS")
        start_year_col1, start_year_col2 = st.columns(2)
        with start_year_col1:
            start_year_begin = st.number_input(
                "Begin Year",
                min_value=1900,
                max_value=2100,
                value=2020,
                step=1,
                help="Enter the beginning year"
            )
        with start_year_col2:
            start_year_end = st.number_input(
                "End Year",
                min_value=1900,
                max_value=2100,
                value=2024,
                step=1,
                help="Enter the ending year"
            )
        start_years = f"{start_year_begin}-{start_year_end}"
    
    # Section 2: Dynamic Frontier Points
    st.header("2. Frontier Points")
    
    # Initialize frontier points in session state if not exists
    if 'frontier_points' not in st.session_state:
        st.session_state.frontier_points = [{"key": "", "value": ""}]
    
    # Function to add new frontier point
    def add_frontier_point():
        st.session_state.frontier_points.append({"key": "", "value": ""})
    
    # Function to remove frontier point
    def remove_frontier_point(index):
        st.session_state.frontier_points.pop(index)
    
    # Display all frontier points
    for i, point in enumerate(st.session_state.frontier_points):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            point["key"] = st.text_input(f"Key {i+1}", value=point["key"], key=f"key_{i}")
        with col2:
            point["value"] = st.text_input(f"Value {i+1}", value=point["value"], key=f"value_{i}")
        with col3:
            if st.button("Remove", key=f"remove_{i}"):
                remove_frontier_point(i)
                st.experimental_rerun()
    
    if st.button("Add Frontier Point"):
        add_frontier_point()
        st.experimental_rerun()
    
    # Section 3: String Formatting
    st.header("3. String Format Builder")
    
    # Create dictionary of all available variables
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
    
    # String format template input
    st.subheader("Create your string template")
    template = st.text_area(
        "Enter your template string using {variable_name} for placeholders",
        "Example: Model for {UNIVERSE} in {ENVIRONMENT} from {START_YEARS} using {MODEL_KEYS}"
    )
    
    # Variable selection
    st.subheader("Select variables to include")
    available_vars = list(variables.keys())
    selected_vars = st.multiselect(
        "Choose variables to include in formatting",
        available_vars
    )
    
    # Preview formatted string
    if st.button("Preview Formatted String"):
        try:
            # Create a dictionary with only selected variables
            format_dict = {k: variables[k] for k in selected_vars if k in variables}
            formatted_string = template.format(**format_dict)
            st.success("Formatted String:")
            st.write(formatted_string)
        except KeyError as e:
            st.error(f"Error: Missing variable {e} in template")
        except Exception as e:
            st.error(f"Error formatting string: {str(e)}")

    # Display current values
    if st.checkbox("Show current values"):
        st.json(variables)

if __name__ == "__main__":
    main()

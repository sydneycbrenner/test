import streamlit as st
import pickle
import os
from itertools import product
import time
from constants import *
from helper_functions import *

def main():
    st.set_page_config(layout="wide")
    st.title("Omnitron Summarization Tool")

    # Initialize session states
    if 'run_status' not in st.session_state:
        st.session_state.run_status = {}
    if 'frontier_points' not in st.session_state:
        st.session_state.frontier_points = []
    if 'model_selections' not in st.session_state:
        st.session_state.model_selections = []
    if 'combination_status' not in st.session_state:
        st.session_state.combination_status = {}
    if 'universe' not in st.session_state:
        st.session_state.universe = []
    # Create main columns
    col1, col2, col3, col4 = st.columns(4)

    # Column 1: Basic Configuration
    with col1:
        st.header("Initial Setup")
        environment = st.selectbox("Environment", options=ENVIRONMENT_OPTIONS)
        db_table = st.text_input("Omnitron DB Table Name")

        universe = st.multiselect("Universe", options=UNIVERSE_OPTIONS, default=None)
        st.session_state.universe = universe

        backtest_user = st.text_input("Backtest User",
                                      help="If summarizing a table that has backtests"
                                           "across several users, go through this process"
                                           "once for each user.")

        st.subheader("Start Years")
        year_col1, year_col2 = st.columns(2)
        with year_col1:
            start_year_begin = st.number_input("Begin", min_value=1985, max_value=2024, value=1999)
        with year_col2:
            start_year_end = st.number_input("End", min_value=1985, max_value=2024, value=2024)
        start_years = f"{start_year_begin}-{start_year_end}"

        st.subheader("MODEL KEYS")

        # Add new implementation section
        st.write("**Select Model Implementation:**")
        new_implementation = st.selectbox(
            "Implementation",
            ["Select..."] + MODEL_IMPLEMENTATIONS + ["Custom"],
            key="new_impl"
        )

        # Handle custom implementation
        if new_implementation == "Custom":
            new_implementation = st.text_input("Enter custom implementation:")

        # Select leverages for the implementation
        if new_implementation and new_implementation != "Select...":
            st.write("**Select Leverages:**")
            selected_leverages = []
            leverage_fees = {}

            # Display leverage options
            for leverage in MODEL_LEVERAGES:
                subcol1, subcol2 = st.columns([3,2])
                with subcol1:
                    if st.checkbox(leverage, key=f"{new_implementation}_{leverage}"):
                        with subcol2:
                            default_fee = DEFAULT_FEES.get(leverage, 0.00)
                            fee = st.number_input(
                                f"Fee",
                                value=default_fee,
                                min_value=-0.05,
                                max_value=0.0,
                                step=0.001,
                                format="%.3f",
                                key=f"{new_implementation}_{leverage}_fee"
                            )
                            selected_leverages.append(leverage)
                            leverage_fees[leverage] = fee

            # Custom leverage option
            if st.checkbox("Add Custom Leverage", key=f"{new_implementation}_custom"):
                custom_col1, custom_col2 = st.columns([3, 2])
                with custom_col1:
                    custom_leverage = st.text_input("Enter custom leverage:", key=f"{new_implementation}_custom_input")
                if custom_leverage:
                    with custom_col2:
                        custom_fee = st.number_input(
                            "Fee",
                            value=0.0,
                            min_value=-0.05,
                            max_value=0.0,
                            step=0.001,
                            format="%.3f",
                            key=f"{new_implementation}_custom_fee"
                        )
                        selected_leverages.append(custom_leverage)
                        leverage_fees[custom_leverage] = custom_fee

            # Add implementation with its leverages
            if st.button("Add Model Configuration"):
                new_config = {
                    "implementation": new_implementation,
                    "leverages": selected_leverages,
                    "fees": leverage_fees
                }
                st.session_state.model_selections.append(new_config)
                st.rerun()

        # Display current model configurations
        if st.session_state.model_selections:
            st.write("**Current Model Configurations:**")
            for i, config in enumerate(st.session_state.model_selections):
                st.write(f"Implementation: {config['implementation']}")
                st.write("Leverages and Fees:")
                for leverage in config['leverages']:
                    fee = config['fees'].get(leverage, 'Missing!')
                    st.write(f"- {leverage} (Fee: {fee:.3f})")
                if st.button("Remove", key=f"remove_config_{i}"):
                    st.session_state.model_selections.pop(i)
                    st.rerun()
                st.write("---")

        # Generate model keys from selections
        model_keys = []
        for config in st.session_state.model_selections:
            impl = config['implementation']
            for lev in config['leverages']:
                model_keys.append(f"{impl}_{lev}")

        if model_keys:
            st.write("**Generated Keys:**")
            st.write(", ".join(model_keys))
            display_summary_sidebar()

    # Column 2: Frontier Points
    with col2:
        st.header("2. Frontier Points")

        # Add new frontier point section
        st.subheader("Add New Frontier Point")
        new_frontier_name = st.text_input("Frontier Name")
        new_frontier_point = [st.text_input("Frontier Points",
                                            help="Enter multiple points as comma-separated list. Use underscores for spaces.")]

        # If user passes in a comma-separated list of values, split these out
        if ',' in new_frontier_point[0]:
            assert len(new_frontier_point) == 1
            new_frontier_point = [x.strip() for x in new_frontier_point[0].split(',')]

        # Add button in its own container
        if st.button("Add Point") and new_frontier_name and new_frontier_point:
            found = False
            for point in st.session_state.frontier_points:
                if point["key"] == new_frontier_name:
                    for new_val in new_frontier_point:
                        if new_val not in point["points"]:
                            point["points"].append(new_val)
                    found = True
                    break

            if not found:
                st.session_state.frontier_points.append({
                    "key": new_frontier_name,
                    "points": new_frontier_point
                })
            st.rerun()

        # Display existing frontier points
        for point in st.session_state.frontier_points:
            st.write(f"**{point['key']}**")
            points_container = st.container()

            with points_container:
                for i, frontier_point in enumerate(point["points"]):
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.info(frontier_point)
                    with cols[1]:
                        if st.button("×", key=f"remove_{point['key']}_{i}"):
                            point["points"].remove(frontier_point)
                            if not point["points"]:
                                st.session_state.frontier_points.remove(point)
                            st.rerun()
            st.write("---")

    # Column 3: String Format Builder
    with col3:
        st.header("3. String Format Builder")

        template = st.text_area(
            "Template string",
            "SSF2_{MODEL_KEY}_{UNIVERSE}_{YEAR}"
        )

        st.subheader("Example Configurations")
        examples = generate_example_strings(
            template,
            universe,
            start_years,
            model_keys,
            st.session_state.frontier_points
        )

        for i, example in enumerate(examples, 1):
            st.write(f"Example {i}:")
            st.success(example)

    # Column 4: Run Summarization
    with col4:
        st.header("4. Run Summarization")

        # Add version selector
        version = st.radio(
            "Summarizer Version",
            ["2023", "2024"],
            horizontal=True,
            help="Select the version of the summarizer to run."
        )

        # Add cluster option
        run_on_cluster = st.checkbox("Summarize on cluster", value=False)

        # Generate all combinations for status tracking
        all_combinations = []
        for config in st.session_state.model_selections:
            impl = config['implementation']
            for lev in config['leverages']:
                if st.session_state.frontier_points:
                    for point in st.session_state.frontier_points:
                        combo_key = generate_combination_key(impl, lev, point)
                        all_combinations.append({
                            'key': combo_key,
                            'impl': impl,
                            'lev': lev,
                            'frontier': point.get('key', ''),
                            'status': st.session_state.combination_status.get(combo_key, 'pending')
                        })
                else:
                    # Handle case with no frontier points
                    combo_key = generate_combination_key(impl, lev, None)
                    all_combinations.append({
                        'key': combo_key,
                        'impl': impl,
                        'lev': lev,
                        'frontier': None,
                        'status': st.session_state.combination_status.get(combo_key, 'pending')
                    })


        # Collect all parameters
        parameters = {
            "universe": universe,
            "db_table": db_table,
            "environment": environment,
            "backtest_user": backtest_user,
            "start_years": start_years,
            "model_keys": model_keys,
            "model_configs": st.session_state.model_selections,
            "frontier_points": st.session_state.frontier_points,
            "run_on_cluster": run_on_cluster,
            "version": version,
        }

        if st.button("Run Summarization"):
            # if db_table:
            #     exists, existing_config = check_existing_config(db_table, environment)
            #     if exists:
            #         st.warning(
            #             f"{db_table} already exists in Omnitron with the following "
            #             f"parameters:\n\n"
            #             f"{existing_config}\n\n"
            #             "Click 'Proceed' to add additional data."
            #         )
            #         if not st.button("Proceed"):
            #             st.stop()

                # Save parameters
                filepath = save_parameters(parameters, db_table, environment)
                st.write(f"Parameters saved to: {filepath}")

                # Initialize/update status for all combinations
                for combo in all_combinations:
                    st.session_state.combination_status[combo['key']] = 'processing'

                # Run summarization and get results
                results = summarize_parameters(run_on_cluster, version)

                # Update status based on results
                for combo_key, success in results.items():
                    st.session_state.combination_status[combo_key] = "completed" if success else "failed"

        # Display status for all combinations
        st.subheader("Processing Status")

        # Group combinations by implementation for cleaner display
        current_impl = None
        for combo in all_combinations:
            if combo['impl'] != current_impl:
                current_impl = combo['impl']
                st.write(f"\n**{current_impl}**")

            status = st.session_state.combination_status.get(combo['key'], 'pending')
            status_colors = {
                "pending": "🟧",
                "processing": "🟧",
                "completed": "🟩",
                "failed": "🟥"
            }

            # Create status display string
            display_text = f"{combo['lev']}"
            if combo['frontier']:
                display_text += f" - {combo['frontier']}"

            st.write(f"{status_colors[status]} {display_text}: {status}")

if __name__ == "__main__":
    main()
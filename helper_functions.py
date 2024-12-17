import streamlit as st
import pickle
import os
from itertools import product
import time
from constants import *
import json
import random

def format_config(config):
    """Format configuration for display"""
    formatted = {
        "universe": config["universe"],
        "db_table": config["db_table"],
        "environment": config["environment"],
        "backtest_user": config["backtest_user"],
        "start_years": config["start_years"],
        "model_keys": config["model_keys"],
        "frontier_points": config["frontier_points"],
        "run_on_cluster": config["run_on_cluster"]
    }
    return json.dumps(formatted, indent=2)

def generate_model_keys(implementations, leverages):
    """Generate all combinations of implementations and leverages"""
    return [f"{impl}_{lev}" for impl, lev in product(implementations, leverages)]

def check_existing_config(db_table, environment):
    """Check if configuration already exists for the given table"""
    filename = os.path.join(SUMMARIZER_CONFIG_ARCHIVE, f"{environment}_{db_table}_config.pkl")
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            existing_config = pickle.load(f)
        return True, existing_config
    return False, None

def save_parameters(params, db_table, environment):
    """Save parameters to pickle file"""
    filename = os.path.join(SUMMARIZER_CONFIG_ARCHIVE, f"{environment}_{db_table}_config.pkl")
    with open(filename, 'wb') as f:
        pickle.dump(params, f)
    return os.path.abspath(filename)


def summarize_parameters(run_on_cluster=False, version="2024"):
    """Simulate parameter summarization with individual combination results"""
    # In practice, this would communicate with your actual summarization system
    # Here we'll simulate async completion of different combinations
    time.sleep(2)  # Simulate initial processing

    # Return a dictionary of results for each combination
    # In practice, this would be populated by your actual system
    results = {}
    for key in st.session_state.combination_status:
        # Simulate some failures for demonstration
        results[key] = random.choice([True, True, True, False])

    return results

def generate_combination_key(impl, lev, point):
    """Generate a unique key for each combination"""
    if point and point.get("key"):
        return f"{impl}_{lev}_{point['key']}"
    return f"{impl}_{lev}"

def generate_example_strings(template, universes, years, model_keys, frontier_points):
    """Generate example strings for each configuration"""
    examples = []
    if not universes or not model_keys:
        return examples

    # Take first instance of each parameter for example
    universe = universes[0]
    start_year, end_year = map(int, years.split('-'))
    year = str(start_year)
    model_key = model_keys[0] if isinstance(model_keys, list) else list(model_keys)[0]

    # Base variables
    variables = {
        "UNIVERSE": universe,
        "YEAR": year,
        "MODEL_KEY": model_key
    }

    # Add in first value from each frontier point
    for point in frontier_points:
        if point["key"] and "points" in point:
            variables[point["key"]] = point["points"][0]

    try:
        example = template.format(**variables)
        examples.append(example)

        # Add one more example with different values if available
        if len(universes) > 1 or len(model_keys) > 1 or len(frontier_points) > 1:
            variables["UNIVERSE"] = universes[-1] if len(universes) > 1 else universe
            variables["MODEL_KEY"] = model_keys[-1] if isinstance(model_keys, list) and len(
                model_keys) > 1 else model_key
            for point in frontier_points:
                if point["key"] and "points" in point:
                    variables[point["key"]] = point["points"][-1]
            examples.append(template.format(**variables))
    except KeyError as e:
        st.error(f"Error in template: Missing variable {e}")

    return examples


def merge_configurations(existing_config, new_config):
    """Merge existing and new configurations"""
    merged = existing_config.copy()

    # Merge lists
    merged["universe"] = list(set(existing_config["universe"] + new_config["universe"]))
    merged["model_keys"] = list(set(existing_config["model_keys"] + new_config["model_keys"]))

    # Merge model configurations
    merged["model_configs"] = existing_config["model_configs"] + new_config["model_configs"]

    # Merge frontier points
    existing_points = {p["key"]: p for p in existing_config["frontier_points"]}
    for new_point in new_config["frontier_points"]:
        key = new_point["key"]
        if key in existing_points:
            # Combine points for existing frontier names
            existing_points[key]["points"] = list(set(
                existing_points[key]["points"] + new_point["points"]
            ))
        else:
            existing_points[key] = new_point

    merged["frontier_points"] = list(existing_points.values())

    return merged

def display_summary_sidebar():
    """Display summary of configurations in sidebar"""
    with st.sidebar:
        st.header("Summary of Configurations")

        st.subheader("Universes")
        for univ in st.session_state.get("universe", []):
            st.write(f"• {univ}")

        st.subheader("Model Configurations")
        for config in st.session_state.get("model_selections", []):
            st.write(f"**{config['implementation']}**")
            for lev in config['leverages']:
                fee = config['fees'].get(lev, 0.01)
                st.write(f"└─ {lev} (Fee: {fee * 100:.2f}%)")

        if st.session_state.get("frontier_points"):
            st.subheader("Frontier Points")
            for point in st.session_state.frontier_points:
                st.write(f"**{point['key']}**")
                for p in point['points']:
                    st.write(f"└─ {p}")

        total_combinations = len(st.session_state.get("universe", [])) * \
                             sum(len(config['leverages']) for config in st.session_state.get("model_selections", [])) * \
                             sum(len(point['points']) for point in st.session_state.get("frontier_points", []))

        st.metric("Total Combinations", total_combinations)
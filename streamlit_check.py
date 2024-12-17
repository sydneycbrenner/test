import sqlite3
from datetime import datetime
import json


def check_job_status(job_id):
    """Check status of a specific job"""
    with sqlite3.connect('job_status.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status, start_time, end_time, results
            FROM jobs
            WHERE job_id = ?
        ''', (job_id,))
        result = cursor.fetchone()

        if result:
            status, start_time, end_time, results = result
            return {
                'status': status,
                'start_time': start_time,
                'end_time': end_time,
                'results': json.loads(results) if results else None
            }
        return None


# Add this to your Streamlit app's Run Summarization section:
def run_summarization(parameters):
    """Save configuration and initiate processing"""
    # Save configuration to watched directory
    config_path = os.path.join(
        "C:/path/to/config/directory",
        f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
    )

    with open(config_path, 'wb') as f:
        pickle.dump(parameters, f)

    # Store the config path in session state
    st.session_state.current_job = {
        'config_path': config_path,
        'start_time': datetime.now()
    }

    return config_path


# In your Streamlit app's main loop:
def update_status_display():
    """Update status display in Streamlit"""
    if 'current_job' in st.session_state:
        status = check_job_status(st.session_state.current_job['config_path'])

        if status:
            st.write(f"Job Status: {status['status']}")

            if status['status'] == 'RUNNING':
                # Show progress for each combination
                progress_placeholder = st.empty()
                with progress_placeholder.container():
                    for combination in status['results']['combinations']:
                        status_color = {
                            'pending': '🟧',
                            'processing': '🟨',
                            'completed': '🟩',
                            'failed': '🟥'
                        }.get(combination['status'], '⬜')
                        st.write(f"{status_color} {combination['name']}")

            elif status['status'] in ['COMPLETED', 'FAILED']:
                if status['results']:
                    st.json(status['results'])
                if status['status'] == 'FAILED':
                    st.error("Job failed. Check logs for details.")
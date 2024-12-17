import time
import os
import pickle
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sqlite3
from datetime import datetime


class ConfigHandler(FileSystemEventHandler):
    def __init__(self, network_script_path):
        self.network_script_path = network_script_path
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database for job status tracking"""
        with sqlite3.connect('job_status.db') as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    config_file TEXT,
                    status TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    combinations JSON,
                    results JSON
                )
            ''')

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.pkl'):
            self.process_config(event.src_path)

    def process_config(self, config_path):
        """Process new configuration file"""
        try:
            # Load configuration
            with open(config_path, 'rb') as f:
                config = pickle.load(f)

            # Generate unique job ID
            job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Initialize job status in database
            with sqlite3.connect('job_status.db') as conn:
                conn.execute('''
                    INSERT INTO jobs (job_id, config_file, status, start_time)
                    VALUES (?, ?, ?, ?)
                ''', (job_id, config_path, 'STARTING', datetime.now()))

            # Execute network script with configuration
            self.run_network_script(job_id, config)

        except Exception as e:
            logging.error(f"Error processing config {config_path}: {str(e)}")
            self.update_job_status(job_id, 'FAILED', str(e))

    def run_network_script(self, job_id, config):
        """Execute the script on network drive"""
        try:
            # Update status to running
            self.update_job_status(job_id, 'RUNNING')

            # Import and run network script
            import sys
            sys.path.append(os.path.dirname(self.network_script_path))

            # This assumes your network script has a run_summary function
            network_module = __import__(os.path.basename(self.network_script_path).replace('.py', ''))
            results = network_module.run_summary(config)

            # Update status based on results
            self.update_job_status(job_id, 'COMPLETED', results=results)

        except Exception as e:
            logging.error(f"Error running network script for job {job_id}: {str(e)}")
            self.update_job_status(job_id, 'FAILED', error=str(e))

    def update_job_status(self, job_id, status, error=None, results=None):
        """Update job status in database"""
        with sqlite3.connect('job_status.db') as conn:
            if status in ['COMPLETED', 'FAILED']:
                conn.execute('''
                    UPDATE jobs 
                    SET status = ?, end_time = ?, results = ?
                    WHERE job_id = ?
                ''', (status, datetime.now(), results, job_id))
            else:
                conn.execute('''
                    UPDATE jobs 
                    SET status = ?
                    WHERE job_id = ?
                ''', (status, job_id))


def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        filename='watcher.log'
    )

    # Path to watched directory and network script
    watch_dir = r"C:\path\to\config\directory"  # Where Streamlit saves configs
    network_script = r"\\networkdrive\folder\summary_script.py"

    # Create observer
    event_handler = ConfigHandler(network_script)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
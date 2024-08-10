from airflow import DAG, settings
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.models import Connection
import json
import os

KEY_FILE_PATH = "./key.json"

def add_gcp_connection(**kwargs):
    new_conn = Connection(
        conn_id="google_cloud_default",  # Change this to your desired connection ID
        conn_type='google_cloud_platform',
    )

    # Read the GCP key JSON content from an environment variable
    key_content = os.getenv('GOOGLE_CREDENTIALS')
    project_id = os.getenv('PROJECT_ID')

    print(key_content)
    print(project_id)

    if not key_content:
        raise ValueError("Environment variable GCP_KEY_JSON not set")

    with open("key.json", 'w') as f:
        f.write(key_content)
    

    extra_field = {
        "extra__google_cloud_platform__scope": "https://www.googleapis.com/auth/cloud-platform",
        "extra__google_cloud_platform__project": project_id,  # Change this to your GCP project ID
        "extra__google_cloud_platform__key_path": './key.json'
    }

    session = settings.Session()

    # Checking if connection exists
    existing_conn = session.query(Connection).filter(Connection.conn_id == new_conn.conn_id).first()
    if existing_conn:
        existing_conn.set_extra(json.dumps(extra_field))
        session.add(existing_conn)
    else:
        new_conn.set_extra(json.dumps(extra_field))
        session.add(new_conn)
        
    session.commit()
    session.close()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2020, 5, 9),  # Change this to your desired start date
    "email": ["airflow@airflow.com"],  # Change this to your email address
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5)
}

dag = DAG("AddGCPConnection", default_args=default_args, schedule_interval="@once")  # Change DAG ID if needed

with dag:
    activateGCP = PythonOperator(
        task_id='add_gcp_connection_python',
        python_callable=add_gcp_connection,
    )

    set_credentials_task = BashOperator(
        task_id="set_google_credentials",
        bash_command=f"export GOOGLE_APPLICATION_CREDENTIALS={KEY_FILE_PATH} && echo 'Credentials set'"
    )

    activateGCP >> set_credentials_task

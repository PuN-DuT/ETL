from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

import sources as f

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(seconds=15)
}


@dag(dag_id='ETL',
     start_date=datetime(2024, 8, 14),
     schedule_interval='@daily',
     default_args=default_args,
     on_failure_callback=f.send_message
     )
def etl_dag():

    @task(multiple_outputs=True)
    def api_to_s3():
        context = get_current_context()
        execution_date = context['ds']
        return {'path': f.download_to_s3(execution_date),
                'exec_date': execution_date}

    @task
    def s3_to_postgres(path, exec_date):
        f.download_s3_to_pg(path, exec_date)
        return exec_date

    @task
    def postgres_to_s3(exec_date):
        f.download_pg_to_s3(exec_date)

    args = api_to_s3()
    load_pg = s3_to_postgres(args['path'], args['exec_date'])
    load_s3 = postgres_to_s3(load_pg)


main_dag = etl_dag()

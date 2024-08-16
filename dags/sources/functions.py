from tempfile import NamedTemporaryFile
import requests
from random import randint

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook


def download_to_s3(execution_date):
    import pandas as pd

    count = randint(1, 100)
    url = (f'https://api.randomdatatools.ru?count={count}&'
           f'params=FirstName,LastName,DateOfBirth,Gender,'
           f'Phone,Login,Password,Email,Country,Region')

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data)
    df['FirstName'] = df.FirstName + ' ' + df.LastName
    df['DateOfBirth'] = pd.to_datetime(df['DateOfBirth'], format='%d.%m.%Y')
    df['date_of_registration'] = execution_date
    df['date_of_registration'] = df['date_of_registration'].astype('datetime64[ns]')
    df = (
        df.drop(columns='LastName')
        .rename(columns={'FirstName': 'user_name',
                         'DateOfBirth': 'date_of_birth'})
        .rename(columns={col: col.lower() for col in df.columns})
    )
    df = df[['user_name', 'date_of_birth', 'date_of_registration', 'phone',
             'login', 'password', 'email', 'gender', 'country', 'region']]

    with NamedTemporaryFile(mode='w',
                            suffix='csv',
                            delete=False) as temp_file:
        df.to_csv(temp_file.name, index=False)

    s3_hook = S3Hook(aws_conn_id='minio_default')
    s3_path = f's3://users/row_data/users_{execution_date}.csv'
    bucket, key = s3_hook.parse_s3_url(s3_path)
    s3_hook.load_file(
        filename=temp_file.name,
        bucket_name=bucket,
        key=key,
        replace=True
    )

    return s3_path


def download_s3_to_pg(s3_path: str, execution_date):
    s3_hook = S3Hook(aws_conn_id='minio_default')
    bucket, key = s3_hook.parse_s3_url(s3_path)
    file_path = s3_hook.download_file(bucket_name=bucket, key=key)

    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS users
        (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(50),        
            date_of_birth DATE,
            date_of_registration DATE,
            phone VARCHAR(50),
            login VARCHAR(50),
            password VARCHAR(30),
            email VARCHAR(100),
            gender VARCHAR(20),
            country VARCHAR(50),
            region VARCHAR(100)       
        );
        '''
    copy_query = ''' 
    COPY users(user_name, date_of_birth, date_of_registration, phone, login,
               password, email, gender, country, region)
    FROM STDIN WITH CSV HEADER DELIMITER ',';
    '''

    pg_hook.run(sql=create_table_query)

    with open(file_path) as file:
        pg_hook.copy_expert(sql=copy_query, filename=file.name)


def download_pg_to_s3(execution_date):
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    copy_query = """ 
        COPY (SELECT region,
                     to_char(date_of_registration, 'month') AS month_name, 
                     COUNT(*) AS count_user,
                     SUM(COUNT(*)) OVER (PARTITION BY region) AS total_by_region
                FROM users 
               GROUP BY 1, 2
               ORDER BY 1, 3 DESC) TO STDOUT WITH CSV HEADER;                  
        """

    with NamedTemporaryFile(mode='w',
                            suffix='csv',
                            delete=False) as temp_file:
        pg_hook.copy_expert(sql=copy_query, filename=temp_file.name)

    s3_hook = S3Hook(aws_conn_id='minio_default')
    s3_path = f's3://users/aggregated_data/users_agg_by_region_{execution_date[:4]}.csv'
    bucket, key = s3_hook.parse_s3_url(s3_path)
    s3_hook.load_file(
        filename=temp_file.name,
        bucket_name=bucket,
        key=key,
        replace=True
    )


def send_message(context):
    from telebot import TeleBot
    from .config.config import load_config

    config = load_config('/opt/airflow/dags/sources/.env')
    token = config.tg_bot.token
    chat_id = config.tg_bot.admin

    bot = TeleBot(token)
    path = '/opt/airflow/dags/pic/alert.jpg'
    task_instance = context['task_instance']
    dag_date = context['ds']

    with open(path, 'rb') as photo:
        bot.send_photo(
            chat_id=chat_id,
            photo=photo
        )

    bot.send_message(
        chat_id=chat_id,
        text=f'Task failed: <b><u>{task_instance.task_id.replace("_", " ")}</u></b> on dag'
             f' <b><u>{task_instance.dag_id}</u></b>  <b>{dag_date}</b>',
        parse_mode='Html'
    )

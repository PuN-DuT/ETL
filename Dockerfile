FROM apache/airflow:2.9.3-python3.11
COPY docker_requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/docker_requirements.txt
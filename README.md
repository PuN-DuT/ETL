# ETL Pipeline with Apache Airflow and Docker

This project demonstrates an ETL (Extract, Transform, Load) pipeline using Apache Airflow, containerized with Docker. The pipeline consists of tasks to extract data, load it into an S3-compatible storage provided by MinIO, transfer it to a PostgreSQL database, and return aggregated data back to the S3 storage.## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Services](#services)
- [Storage](#storage)
- [License](#license)

## Overview

The ETL pipeline is defined in the `etl_dag.py` file using Airflow's DAG (Directed Acyclic Graph) and task decorators. The pipeline includes tasks to extract random user data from the https://randomdatatools.ru API, load it into an S3-compatible storage provided by MinIO, and transfer it to a PostgreSQL database. After the data is transferred to PostgreSQL, an aggregation step is performed to summarize the data by date and region. The aggregated data is then returned to the S3 storage for further analysis or reporting.
## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/PuN-DuT/ETL.git
    cd ETL
    ```
2. **Install necessary packages**:

    ```sh
    pip install -r requirements.txt
    ```   
3. **Build and start the Docker containers**:

    ```sh
    docker-compose up
    ```

## Usage

1. **Access MinIO UI**: Open your browser and navigate to `http://localhost:9001`.

    - **Login**: `minio_admin`
    - **Password**: `minio_password`

2. **Create a new bucket**:

    - In the MinIO UI, create a new bucket named `users`.

3. **Access Airflow UI**: Open your browser and navigate to `http://localhost:8080`.

    - **Login**: `airflow`
    - **Password**: `airflow`

4. **Set up connections**:

    - Go to the Airflow UI and navigate to **Admin** -> **Connections**.
    - Add a new connection with the following details:
        - **Connection Id**: `minio_default`
        - **Connection Type**: `Amazon Web Service`
        - **Extra**:
            ```json
            {
                "aws_access_key_id": "minio_admin",
                "aws_secret_access_key": "minio_password",
                "endpoint_url": "http://minio:9000"
            }
            ```
    - Add another new connection with the following details:
        - **Connection Id**: `postgres_default`
        - **Host**: `host.docker.internal`
        - **Database**: `minio`
        - **Login**: `minio`
        - **Password**: `minio`
        - **Port**: `5433`

5. **Trigger the DAG**: Find the `ETL` DAG in the Airflow UI and trigger it manually or wait for the scheduled run.

## Alerts

To set up alerts for task failures via a Telegram chatbot, follow these steps:

1. **Create a Telegram Bot**:
    - Open Telegram and search for the "BotFather" bot.
    - Start a chat with BotFather and use the `/newbot` command to create a new bot.
    - Follow the instructions to name your bot and get the bot token.

2. **Get Chat ID**:
    - Start a chat with your new bot and send any message to it.
    - Use a bot like "userinfobot" to get your chat ID.

3. **Configure Environment Variables**:
    - Copy the `.env.example` file to `.env`:
        ```sh
        cp .env.example .env
        ```
    - Edit the `.env` file to include your Telegram bot token and chat ID:
        ```env
        BOT_TOKEN=your_bot_token
        CHAT_ID=your_chat_id
        ```
In case of task failures, alerts are sent via the configured Telegram chatbot. The `alert.jpg` image is used for these notifications.

## Services

- **Airflow**: Used as the workflow orchestration tool to manage and schedule the ETL pipeline.
- **PostgreSQL**: Acts as the database to store transformed data.
- **MinIO**: Serves as an S3-compatible storage solution, providing high-performance, distributed object storage for storing data extracted from the API and transferred between tasks in the ETL pipeline.
- **Random User Data API**: The [https://randomdatatools.ru](https://randomdatatools.ru) API is used to fetch random user data, which is then processed and stored in the pipeline.
## Project Structure

The project has the following structure:

- **📁 dags**  
  - **📄 etl_dag.py**:
  - **🔑 .env.example**: Example environment variables file.
  - **📁 pic**
      - **🖼️  alert.jpg**: Image used for Telegram alerts.
  - **📁 sources**
    - **🔧 __init__.py**
    - **📄 functions.py**: Contains functions used in the DAG.
    - **📁 config**
      - **🔧__init__.py**
      - **🔧 config.py**: Contains configurations for the bot.
- **🐳 docker-compose.yml**
- **🐳 Dockerfile**
- **📄 README.md**
- **🔧 docker_requirements.txt**
- **🔧 requirements.txt**


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
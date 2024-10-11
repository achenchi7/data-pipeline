# Data Pipeline Documentation
This project sets up a real-time data pipeline using Apache Kafka, Apache Spark, Cassandra, and Apache NiFi to process and store streaming data. The pipeline ingests data, processes it using Spark and apache, and then stores the processed data in a Cassandra database for future analysis.

### Tech stack
- **Kafka:** A distributed event streaming platform that ingests and publishes streaming data.
- **Spark Streaming:** Real-time data processing engine that processes data ingested from Kafka.
- **Cassandra:** A NoSQL database that stores the processed data.
- **NiFi:** Manages data flow and integrates different systems.
- **Apache airflow:**

### Docker compose configuration
The `docker-compose.yml` file orchestrates the setup of the various services required by the data pipeline. It spins up `Kafka`, `Zookeeper`, `Spark`, `Cassandra`, and `Airflow` in separate Docker containers, allowing each service to run in isolation while being able to communicate with each other over the defined network.

#### Key components
- **Kafka Broker:** Set up to handle data ingestion. Kafka receives messages that will be processed by Spark.
- **Zookeeper:** Coordinates and manages Kafka brokers.
- **Schema Registry:** Provides a centralized repository for storing Avro schemas that Kafka will use.
- **Spark Master and Worker:** Spark's master node manages worker nodes that process data in parallel.
- **Cassandra:** Stores the processed data.
- **NiFi:** Enables data flow management for complex data routing between components.

#### The architecture
Below is a visualization of the data pipeline architecture
![data pipeline architecture](https://github.com/achenchi7/data-pipeline/blob/main/pipeline-architecture.png)


### Code Breakdown
**Cassandra Keyspace and Table Creation**
**Purpose:**
This chunk of code defines the creation of a keyspace and table in Cassandra to store processed data.

Key Functions:
create_keyspace(session):
This function creates the `spark_streams keyspace` with a replication factor of 1, ensuring the data is distributed across one replica.
This keyspace will act as the namespace for storing tables that contain user data.
`create_table(session)`:
Creates the `created_users` table within the `spark_streams` keyspace.
The table stores user information such as first_name, last_name, gender, email, etc., with a unique identifier (id) as the primary key.

```python
def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)

def create_table(session):
    session.execute("""
    CREATE TABLE IF NOT EXISTS spark_streams.created_users (
        id UUID PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        address TEXT,
        post_code TEXT,
        email TEXT,
        username TEXT,
        registered_date TEXT,
        phone TEXT,
        picture TEXT);
    """)
```
**How It Meets Requirements:**
This segment ensures that Cassandra has the proper structure to store user data, allowing the pipeline to store structured information for further use or analysis.

### Data Insertion into Cassandra
**Purpose:**
This part of the code handles inserting streaming data into Cassandra once it's processed.

Key Function:
`insert_data(session, **kwargs)`:
This function inserts records into the `created_users` table.
It accepts keyword arguments containing user information (e.g., first_name, last_name, etc.) and executes the insertion using Cassandra's `session.execute()` method.

```python
def insert_data(session, **kwargs):
    session.execute("""
        INSERT INTO spark_streams.created_users(id, first_name, last_name, gender, address, 
            post_code, email, username, registered_date, phone, picture)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, first_name, last_name, gender, address, postcode, email, username, dob, registered_date, phone, picture))
```

**How It Meets Requirements:**
The insertion function ensures that processed data is stored persistently in Cassandra, fulfilling the requirement for data storage in the pipeline.

### Spark Streaming Setup
**Purpose:**
This section establishes a connection to Apache Spark for processing the streaming data from Kafka.

Key Function:
`create_spark_connection()`:
Creates a Spark session configured to use the Kafka and Cassandra connectors.
It loads the required packages for Spark to communicate with Kafka (`spark-sql-kafka`) and Cassandra (`spark-cassandra-connector`).

```python
def create_spark_connection():
    s_conn = SparkSession.builder \
        .appName('SparkDataStreaming') \
        .config('spark.jars.packages', "com.datastax.spark:spark-cassandra-connector_2.13:3.4.1,"
                                       "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1") \
        .config('spark.cassandra.connection.host', 'localhost') \
        .getOrCreate()
```
**How It Meets Requirements:**
This function sets up the Spark environment needed to read Kafka streams and process the data before storing it in Cassandra

### Kafka Data Stream Connection
**Purpose:**
This function connects to the Kafka topic to read real-time streaming data and processes it using Spark.

**Key Function:**
`connect_to_kafka()`:
Connects to the Kafka topic and reads incoming messages.
The data is processed as a Spark DataFrame, making it easier to manipulate and transform using Spark's APIs.

```python
def connect_to_kafka(spark_conn):
    spark_df = spark_conn.readStream \
        .format('kafka') \
        .option('kafka.bootstrap.servers', 'localhost:9092') \
        .option('subscribe', 'user_data_topic') \
        .load()
```
**How It Meets Requirements:**

The function establishes a connection to the Kafka stream, allowing the pipeline to ingest real-time data, a core requirement for this streaming data pipeline.

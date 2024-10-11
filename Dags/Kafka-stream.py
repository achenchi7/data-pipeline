from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'airscholar',
    'start_date': datetime(2023, 9, 3, 10, 00)
}

def get_data():
    import requests

    res = requests.get('https://randomuser.me/api/')
    res = res.json()
    res = res['results'][0]

    return res

def format_data(res):
    data = {}
    location = res['location']
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']}, "\
                      f"{location['city']}, {location['state']}, {location['country']}"
    data['postcode'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']

    return data

def stream_data():
    import json
    from kafka import KafkaProducer
    import time

    
    producer = KafkaProducer(bootstrap_servers=['broker:2902'], max_block_ns=5000)
    
    while True:
        if time.time() > curr_time + 60: #1 minute
            break
        try:
            res = get_data()
            res = format_data(res)

            producer.send('users_created', json.dumps(res).encode('utf-8'))
        except Exception as e:
            logging.error(f'An error occured: {e}')
            continue



with DAG('user_automation',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:
    
    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )


# from datetime import datetime
# from airflow import DAG
# from airflow.operators.python import PythonOperator
# import json
# from kafka import KafkaConsumer
# import logging

# # Define default arguments for the Airflow DAG
# default_args = {
#     'owner': 'airscholar',
#     'start_date': datetime(2023, 9, 3, 10, 00)
# }

# # Function to process the data received from Kafka
# def process_data(data):
#     try:
#         location = data['location']
#         formatted_data = {
#             'first_name': data['name']['first'],
#             'last_name': data['name']['last'],
#             'gender': data['gender'],
#             'address': f"{str(location['street']['number'])} {location['street']['name']}, "
#                        f"{location['city']}, {location['state']}, {location['country']}",
#             'postcode': location['postcode'],
#             'email': data['email'],
#             'username': data['login']['username'],
#             'dob': data['dob']['date'],
#             'registered_date': data['registered']['date'],
#             'phone': data['phone'],
#             'picture': data['picture']['medium']
#         }
#         return formatted_data
#     except KeyError as e:
#         logging.error(f'Missing key in data: {e}')
#         return None

# # Function to consume data from Kafka
# def consume_from_kafka():
#     consumer = KafkaConsumer(
#         'users_created',  # Kafka topic where NiFi publishes the data
#         bootstrap_servers=['broker:2902'],  # Kafka broker
#         auto_offset_reset='earliest',
#         enable_auto_commit=True,
#         group_id='airflow-consumer-group',
#         value_deserializer=lambda x: json.loads(x.decode('utf-8'))
#     )

#     logging.info("Started consuming from Kafka topic 'users_created'")

#     for message in consumer:
#         data = message.value  # Extract the JSON data from Kafka message
#         logging.info(f"Received data from Kafka: {data}")

#         formatted_data = process_data(data)

#         if formatted_data:
#             logging.info(f"Processed data: {json.dumps(formatted_data, indent=2)}")
#             # Here you can add logic to store the data, send it somewhere, etc.
#         else:
#             logging.error("Failed to process data.")

# # Airflow DAG definition
# with DAG('user_data_pipeline',
#          default_args=default_args,
#          schedule_interval='@daily',
#          catchup=False) as dag:

#     # Define the PythonOperator for consuming data from Kafka
#     consume_data_task = PythonOperator(
#         task_id='consume_from_kafka',
#         python_callable=consume_from_kafka
#     )

# # Run the task in Airflow
# consume_data_task.execute(context={})

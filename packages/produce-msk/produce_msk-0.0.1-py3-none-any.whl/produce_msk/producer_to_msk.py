import sys,traceback
import json
import base64
import logging
import boto3
import sys
from confluent_kafka import Producer
from botocore.exceptions import ClientError
from decimal import Decimal

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class KafkaMSKProducer():
    """Kafka producer abstraction to produce Json message to a defined kafka topic.
    In sync or async way, and defining to use callbacks if needed.
    """

    def __init__(self, kafka_config: dict):
        self._producer = Producer(kafka_config)
 
    @staticmethod
    def _callback_acked(err, msg) -> None:
        """"""
        if err:
            print(
                f'Failed to deliver message: {str(msg.value())}. {str(err)}')
        else:
            print(
                f'Message produced in topic: {str(msg.topic())}')

    def produce(self, topic: str, message,
                     sync: bool = False, use_callback: bool = False) -> None:
        """Produce message to the defined Kafka Topic. In sync or async way.

        Args:
            - topic: the topic where the data will be produced.
            - message: the message to produce to the kafka topic.
            - sync: flag make the produce call synchronous or asynchronous
            - use_callback: flag to print a log when a message is produce.

        Returns: None
        """
        logging.info(f'Param topic: {topic}')
        logging.info(f'Param message: {message}')
        
        assert type(sync) == bool and type(use_callback) == bool,\
            'sync and use_callback need to be booleans.'
        callback_f = KafkaMSKProducer._callback_acked if use_callback else None

        self._producer.produce(topic=topic, value=message , callback=callback_f)

        
        if sync:
            self._producer.flush()
        else:
            self._producer.poll(0)
        print('Data produced.')

class receivemessage():

    # HTTP messages 
    SUCCESS_MSG = 'Item saved sucessfully.'
    BACKEND_ERROR_MSG = 'Error, the item from the request could not be saved.'


    # ==================================================================================
    # This function generate the api response, with http status code and body to be return
    # to the client
    # ==================================================================================
    # ----------------------------------------------------------------------------------
    # INPUT:    status_code          (string)       the http status code of the response
    #           body                 (JSON)         the message of the response to be send on the body
    # OUTPUT:   webhook_response     (JSON)         the response on json format sending the
    #                                               status code and the message in the body.
    # ----------------------------------------------------------------------------------   
    def generate_api_response(status_code: int, body: str) -> dict:

        assert (str(status_code).startswith(('1', '2', '3', '4', '5'))
                and len(str(status_code)) == 3), 'Invalid http code'
        webhook_response = {
            'statusCode': status_code,
            'body': json.dumps(body)
        }
        return webhook_response

    # ==================================================================================
    # This function receive tha name of secret and get value 
    # ==================================================================================
    # ----------------------------------------------------------------------------------
    # INPUT:    secret_name      (string)       Name of secret
    # OUTPUT:   secret_value     (JSON)         Secret value
    # ----------------------------------------------------------------------------------    
    def read_secret(secret_name: str) -> str:
        secret = boto3.client('secretsmanager')
        try:
            secret_value_response = secret.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.error(
                    f'SecretId not found, check the path in the env variables. {e}'
                )
                raise e
            else:
                logger.error(f'An error ocurred while retrieving the secret. {e}')
                raise e

        if 'SecretBinary' in secret_value_response:
            # in case the secret is defined in binary
            secret_value = base64.b64decode(secret_value_response['SecretBinary'])
        else:
            secret_value = secret_value_response['SecretString']
        return secret_value

    # ==================================================================================
    # This function receive name of topic and message. the call read_sercret and send
    # mesaage and topic to create 
    # ==================================================================================
    # ----------------------------------------------------------------------------------
    # INPUT:    resource_path      (string)      Name of topic
    #           body               (JSON)        All meesage
    # OUTPUT:                      (string)      Success/fail produce message
    # ----------------------------------------------------------------------------------    
    def api_call_handler(resource_path: str, body: str, kafka_secret) -> dict:
        """Handle the API call. Identifying the resource (path) from where the
        API Call has been made, based on the resource header of the call. And
        parser the body of the call and write the result in the desired format.
        It could be to a dynamodb table or to a kafka topic.

        Args:
            - resource_path: the resource from where the API has been called.
            - body: the json payload receive from the API.

        Returns: the HTTP response to be send by API Gateway.
        """
        try:
            kafkasecret = json.loads(receivemessage.read_secret(kafka_secret))
            kafka_handler = KafkaMSKProducer(kafkasecret)
            kafka_handler.produce(
                topic=resource_path, message=body, sync=True, use_callback=True)
            succ_msg = 'The message was send succesfully'
            return {
                'result': succ_msg
            }
        except Exception as e:
            error_code = 500
            error_msg = f'An error ocurred while saving the item. {e}'
            logger.error(error_msg, exc_info=1)
            # add other exception to saend 400 erros for example if needed
            return {
                    'result': error_msg
            }


import asyncio
from json import load
import os

from azure.identity.aio import DefaultAzureCredential
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
import socket


from azure.servicebus.aio._servicebus_sender_async import ServiceBusSender
from dotenv import load_dotenv

load_dotenv()

FULLY_QUALIFIED_NAMESPACE = os.environ["AZURE_NAMESPACE_NAME"]
QUEUE_NAME = os.environ["AZURE_QUEUE_NAME"]

credential = DefaultAzureCredential()

async def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    await sender.send_messages(message)

class ServiceBussClientCreator():
   async def __init__(
            self,
            fully_qualified_namespace:str,
            credential:DefaultAzureCredential,
            logging_enable:bool):
        
        async with ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            logging_enable=logging_enable) as service_buss_client:
            yield service_buss_client
        

async def run():
    # create a Service Bus client using the credential
    async with ServiceBusClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        credential=credential,
        logging_enable=True) as servicebus_client:
        # get a Queue Sender object to send messages to the queue
        sender: ServiceBusSender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            # send one message
            await send_single_message(sender)

        # Close credential when no longer needed.
        await credential.close()

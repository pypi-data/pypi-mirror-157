import datetime
import boto3
import traceback
from copy import deepcopy

from util.ptLogger import PTLogger
from util.ptMetric import PTMetric

client = boto3.client('events')
logger = PTLogger(__name__).get_logger()
global_parameters = {
    "EnableNotification": False,
    "Annotation": {
        "Application": "undefined",
        "Module": "undefined",
        "Creator": "undefined",
        "Owner": "undefined",
        "Reviser": "undefined"
    }
}


def processRequest(messageList, event, context):
    raise NotImplementedError("processRequest not implemented")


def _extract_message(record):
    eventSourceArn = record["eventSourceARN"]
    queueName = eventSourceArn.split(":")[-1]
    messageBodyText = record.get("body")
    message = {
        "receiptHandle": record.get("receiptHandle"),
        "messageBodyText": messageBodyText,
        "metadata": {
            "eventSource": record.get("eventSource"),
            "eventSourceARN": record.get("eventSourceARN"),
            "queueName": queueName,
            "senderId": record.get("attributes").get("SenderId"),
            "approximateFirstReceiveTimestamp": record.get("attributes").get("ApproximateFirstReceiveTimestamp"),
            "approximateReceiveCount": record.get("attributes").get("ApproximateReceiveCount"),
            "sentTimestamp": record.get("attributes").get("SentTimestamp"),
        }
    }
    return message


def handler(event, context):
    tick_start = datetime.datetime.now()
    logger.info("triggered by QueueHandler...")
    logger.info(f"Lambda function_name: {context.function_name}")
    logger.info(f"Lambda function_version: {context.function_version}")
    logger.info(f"Lambda invoked_function_arn: {context.invoked_function_arn}")
    logger.info(f"message is: {event}")
    logger.info("initializing ptMetric...")

    dimensions = deepcopy(global_parameters["Annotation"])
    dimensions.update({"FunctionName": context.function_name})
    dimensions.update({"TriggerHandlerType": "QueueTrigger"})

    metric_wrapper = PTMetric(namespace="PT/Lambda", dimensions=dimensions)
    metric_wrapper.put_metric_data(name="Entry", value=1, unit="Count")

    try:
        messageList = [_extract_message(r) for r in event["Records"]]

        respDict = processRequest(messageList, event, context)
        if respDict and not isinstance(respDict, dict):
            raise Exception("resp type must be dict, now is %s" % type(respDict))

        metric_wrapper.put_metric_data(name="Invocation", value=1, unit="Count")
        tick_end = datetime.datetime.now()
        tick_delta = (tick_end - tick_start).total_seconds() * 1000
        metric_wrapper.put_metric_data(name="Duration", value=tick_delta, unit="Milliseconds")

        if global_parameters["EnableNotification"]:
            logger.warn("notification is not implemented")

    except Exception as ex:
        metric_wrapper.put_metric_data(name="Error", value=1, unit="Count")
        traceback.print_exc()
        if global_parameters["EnableNotification"]:
            logger.warn("notification is not implemented")

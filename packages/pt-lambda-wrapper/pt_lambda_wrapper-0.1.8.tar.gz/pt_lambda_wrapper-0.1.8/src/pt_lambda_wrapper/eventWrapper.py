import datetime
import boto3
import traceback
import json

from copy import deepcopy

from util.ptLogger import PTLogger
from util.ptMetric import PTMetric
from util.ptTrace import PTTrace

client = boto3.client('events')
logger = PTLogger(__name__).get_logger()
global_parameters = {
    "EnableNotification": False,
    "EnableMetric": True,
    "EnableTrace": True,  # JimmyMo: must add pt-infra-xray layer
    "Annotation": {
        "Application": "undefined",
        "Module": "undefined",
        "Creator": "undefined",
        "Owner": "undefined",
        "Reviser": "undefined"
    }
}


def processRequest(req, event=None, context=None):
    raise NotImplementedError("processRequest not implemented")


def handler(event, context):
    tick_start = datetime.datetime.now()
    logger.info("triggered by EventHandler...")
    logger.info(f"Lambda function_name: {context.function_name}")
    logger.info(f"Lambda function_version: {context.function_version}")
    logger.info(f"Lambda invoked_function_arn: {context.invoked_function_arn}")
    logger.info(f"event is: {event}")

    if global_parameters["EnableMetric"]:
        logger.info("metric enabled! initializing ptMetric...")
        dimensions = deepcopy(global_parameters["Annotation"])
        dimensions.update({"FunctionName": context.function_name})
        dimensions.update({"TriggerHandlerType": "EventTrigger"})

        context.metric_wrapper = PTMetric(namespace="PT/Lambda", dimensions=dimensions)
        context.metric_wrapper.put_metric_data(name="Entry", value=1, unit="Count")

    if global_parameters["EnableTrace"]:
        logger.info("trace enabled!")
        context.trace_wrapper = PTTrace()
        context.trace_wrapper.enable_all_trace()

    if isinstance(event["detail"], str):
        eventDetail = json.loads(event["detail"])
    else:
        eventDetail = event["detail"]

    try:
        req = {
            "source": event["source"],
            "detailType": event["detail-type"],
            "metadata": eventDetail.get("metadata", {}),
            "payload": eventDetail.get("payload", {}),
        }
        with context.trace_wrapper.record("ProcessRequest") as recorder:
            recorder.put_metadata("very_important_inforamtion", {"message": "Hello I am metadata"}, "information")
            recorder.put_annotation("very_important_annotation", "Very very important information")
            respDict = processRequest(req, event, context)
            if respDict and not isinstance(respDict, dict):
                raise Exception("resp type must be dict, now is %s" % type(respDict))

        if global_parameters["EnableMetric"]:
            context.metric_wrapper.put_metric_data(name="Invocation", value=1, unit="Count")
            tick_end = datetime.datetime.now()
            tick_delta = (tick_end - tick_start).total_seconds() * 1000
            context.metric_wrapper.put_metric_data(name="Duration", value=tick_delta, unit="Milliseconds")

        if global_parameters["EnableNotification"]:
            logger.warn("notification is not implemented")
    except Exception as ex:
        context.metric_wrapper.put_metric_data(name="Error", value=1, unit="Count") if global_parameters["EnableMetric"] else None
        traceback.print_exc()
        if global_parameters["EnableNotification"]:
            logger.warn("notification is not implemented")
        raise ex


if __name__ == "__main__":
    print("Done")
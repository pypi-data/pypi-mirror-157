import base64


def processRequest(req):
    raise NotImplementedError("processRequest not implemented")


def handler(event, context):
    print("triggered by HttpHandler...")
    print("event is %s" % event)

    if event["httpMethod"] == "OPTIONS":
        print(
            "NOTICE!, received options preflight request, may consider use api-gateway mock options method instead...")
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
                "Content-Type": "application/json"
            },
            "body": None,
            "isBase64Encoded": False
        }

    try:
        if event["body"]:
            requestBody = base64.b64encode(bytearray.fromhex(event["body"])) if event["isBase64Encoded"] else event["body"]

        req = {
            "headers": event["headers"] or {},
            "queryStringParameters": event["queryStringParameters"] or {},
            "pathParameters": event["pathParameters"] or {},
            "body": requestBody if "requestBody" in locals() else {}
        }

        resp = processRequest(req)
        if not isinstance(resp, dict):
            raise Exception("resp type must be dict, now is %s" % type(resp))

        if resp and "contentType" in resp:
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
                    "Content-Type": resp["contentType"]
                },
                "body": resp["body"],
                "isBase64Encoded": resp["isBase64Encoded"]
            }
        else:
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
                    "Content-Type": "application/json"
                },
                "body": resp,
                "isBase64Encoded": False
            }
    except Exception as ex:
        print(ex)
        return {
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
                "Content-Type": "application/json"
            },
            "statusCode": 200,
            "body": ex,
            "isBase64Encoded": False
        }


if __name__ == "__main__":
    handler(None, None)

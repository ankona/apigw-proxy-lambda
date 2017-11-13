"""
Definition for an api-passthrough-proxy lambda function. This lambda handler
takes in the default event definition for a {proxy+} api gateway endpoint
and routes that traffic to upstream services defined in environment variables.
"""
import os
import json
import logging
import requests as req

class JsonableObject(object):
    """
    An object that can easily be serialized to json.
    """
    def to_json(self):
        """
        Convert self to a json representation.
        """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, separators=(',', ':'))

class TargetRequest(JsonableObject):
    """
    Contains all information necessary to pass the request to an upstream endpoint.
    """
    def __init__(self, method, uri, query_string, body=""):
        """
        Initialize the object with all required properties.
        """
        self.method = method.lower()
        self.uri = uri.lower()
        self.query_string = query_string
        # self.headers = headers if headers else {}
        self.body = body

def is_proxy_api(event):
    """
    Return a boolean indicating if the service call is a HTTP proxy
    endpoint or a HTTP custom endpoint.
    """
    return True if event["pathParameters"] and "proxy" in event["pathParameters"] else False

def build_target_upstream(logger, event):
    """
    Given the incoming proxy+ api request & upstream list, define the
    upstream request to perform.
    """
    proxy_resource = event["resource"]
    http_method = event["httpMethod"]
    # headers = event["headers"]
    query_params = event["queryStringParameters"]
    proxy_path = event["pathParameters"]["proxy"] if is_proxy_api(event) else event["resource"]
    body = event["body"]

    # apigw will send a proxy resource like /foo/bar/{proxy+}.
    # remove the proxy part so we can look up the mapping.
    base_node = proxy_resource.replace("/{proxy+}", "")

    target_upstream = ""

    try:
        env_key = base_node.replace("/", "_")
        if env_key.startswith("_"):
            env_key = env_key[1:] # get rid of leading / replaced with _
        target_upstream = os.environ[env_key]
        logger.debug("target_upstream: %s", target_upstream)
    except KeyError as kex:
        logger.exception(kex)
        logger.error("No target upstream found. Add ENV var for supplied base node: %s", base_node)

    if target_upstream:
        if not target_upstream.endswith("/"):
            target_upstream += "/"

        target_uri = target_upstream + proxy_path if is_proxy_api(event) else target_upstream
        target = TargetRequest(method=http_method,
                               uri=target_uri,
                               query_string=query_params,
                               body=body)

        logger.info("target: %s", target.to_json())

    return target

def execute_upstream(target_request):
    """
    Use target_request to call an upstream service and return the response.
    """
    result = None
    if target_request.method == "get":
        result = req.get(target_request.uri)
    elif target_request.method == "head":
        result = req.head(target_request.uri)
    elif target_request.method == "post":
        headers = {'content-type': 'application/json'}
        result = req.post(target_request.uri,
                          headers=headers,
                          data=target_request.body)
    elif target_request.method == "put":
        headers = {'content-type': 'application/json'}
        result = req.put(target_request.uri,
                         headers=headers,
                         data=target_request.body)
    elif target_request.method == "patch":
        headers = {'content-type': 'application/json'}
        result = req.patch(target_request.uri,
                           headers=headers,
                           data=target_request.body)
    elif target_request.method == "delete":
        result = req.delete(target_request.uri)
    elif target_request.method == "options":
        result = req.options(target_request.uri)
    return result

def lambda_handler(event, context):
    """
    Handle all incoming requests. Pass request details on to target API.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("Received event: %s", json.dumps(event, separators=(',', ':')))

    target = build_target_upstream(logger, event)
    result = None
    if target:
        try:
            result = execute_upstream(target)
        except Exception as ex:
            logger.exception(ex)
            return {
                "statusCode": "500",
                "body": "An error occurred."
            }
        logger.info("result.content: %s", result.json())
        return {
            "statusCode": result.status_code,
            "headers": {
                "x-custom-header": "my val",
                "content-type": "application/json"
            },
            "body": json.dumps(result.json(), separators=(',', ':'))
        }
    else:
        logger.error("No target built! Does Not Compute!")

if __name__ == "__main__":
    pass

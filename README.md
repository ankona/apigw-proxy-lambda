# apigw-proxy-lambda
A lambda function used to map incoming requests from a {proxy+} AWS API Gateway endpoint to a target upstream API.

Note: If you are hitting a public upstream API, this is unnecessary. It's only use for me is to overcome the APIGW limitation that resources inside our corporate VPC cannot be hit without a lambda tied to the VPC (that is, there is no APIGW VPC integration.)

This function is a minimum-viable-product for proxy APIs and may serve as a base. However, there are some large problems with proxy+ api integrations in API Gateway:

    - Fixed cache lifetime across all proxy+ endpoints.
    - Fixed authorization across all proxy+ endpoints.

# How does it work?

The simplest implementation possible is to map "keys" in the API to named environment variables on the lambda function. This avoids creating any database or modifications of code to add new endpoints. Just add items to APIGW & modify your lambda environment variables.

E.g. 

    - Create an env var SERVICE_ONE with a value of http://my.api.com/serviceone
    - Create an API in apigw with a proxy+ endpoint with the resource named SERVICE_ONE.
    - Check env vars for matching value. 

See [here](https://github.com/thehighlander/apigw-proxy-lambda/blob/master/apigw-proxy-lambda/lambda_function.py#L47)
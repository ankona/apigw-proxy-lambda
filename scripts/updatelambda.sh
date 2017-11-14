#!/bin/bash
rm apigw_proxy_lambda.zip
zip -ru apigw_proxy_lambda.zip . -x "*.pyc" "*.dist-info/*" ".git/*" ".DS_Store"
zip apigw_proxy_lambda.zip lambda_function.py
aws lambda update-function-code --function-name apigw-proxy-lambda --zip-file fileb://apigw_proxy_lambda.zip --publish

#!/bin/bash
env=${1}
function_base_name='apigw-proxy-lambda'
package_dir='deployment-package'

# move all my lambda code into a new directory where we'll deploy from.
mkdir "$package_dir"
cp ./*.py "./$package_dir"

# update the environment file to have the proper env to run under.
echo "current_environment = '$env'" > "./$package_dir/environment.py"

# install necessary libs for lambda to run remotely.
pip install -r requirements.txt -t "./$package_dir"

# move into my deployment directory.
cd "$package_dir"

# zip up the lambda function & all it's dependencies. update code in AWS
rm "$function_base_name.zip"
zip -ru "$function_base_name.zip" . -x "*.pyc" "*.dist-info/*" ".git/*" ".DS_Store"
aws lambda update-function-code --function-name "$function_base_name" --zip-file "fileb://$function_base_name.zip" --publish
#rm "$function_base_name.zip"

# clean up all files from the packaging operation
cd ..
rm -r "$package_dir"

### USAGE ####
# cd /Users/chris/github/apigw-proxy-lambda/apigw-proxy-lambda
# ../scripts/updatelambda.sh dev

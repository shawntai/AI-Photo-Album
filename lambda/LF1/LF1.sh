pip3 install --target ./package requests-aws4auth opensearch-py
cd package
zip -r ../LF1.zip .
cd ../
zip LF1.zip LF1.py
aws lambda update-function-code --function-name LF1 --zip-file fileb://LF1.zip
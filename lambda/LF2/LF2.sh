pip3 install --target ./package requests-aws4auth opensearch-py inflection
cd package
zip -r ../LF2.zip .
cd ../
zip LF2.zip LF2.py
aws lambda update-function-code --function-name LF2 --zip-file fileb://LF2.zip
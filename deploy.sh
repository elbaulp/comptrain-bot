#!/bin/bash

sls deploy
cd .venv/lib/python3.7/site-packages
zip -r9 ${OLDPWD}/function.zip .
cd $OLDPWD
zip -g function.zip handler.py
aws lambda update-function-code --function-name comptrain-bot-dev-comptrain --zip-file fileb://function.zip
rm function.zip

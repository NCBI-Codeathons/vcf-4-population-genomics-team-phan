# API

```bash
export FLASK_ENV=development
export FLASK_APP=app.py

pushd src/app && flask run --host=0.0.0.0 && popd
```

```bash
npm config set prefix '~/.local/'
# npm install -g serverless
npm install -g serverless@1.55.1

export PATH=~/.local/bin/:$PATH

npm install -g serverless
serverless config credentials --provider aws --key $AWS_ACCESS_KEY --secret $AWS_SECRET_KEY

pushd src/app
serverless plugin install -n serverless-wsgi
serverless plugin install -n serverless-python-requirements
serverless plugin install -n serverless-deployment-bucket

# currently fails
serverless deploy
```

# API

## Set up local server

```bash
export FLASK_ENV=development
export FLASK_APP=app.py

pushd src/app && flask run --host=0.0.0.0 && popd
```

## Use serverless.com tools to deploy service

### Set up serverless.com

You can tweak some steps (paths, command line parameters, etc.) to suit your
needs.

```bash
# add custom values
export AWS_ACCESS_KEY=
export AWS_SECRET_KEY=
export AWS_REGION=us-east-1
```

```bash
npm config set prefix '~/.local/'
npm install -g serverless

export PATH=~/.local/bin/:$PATH

serverless config credentials --provider aws --key $AWS_ACCESS_KEY --secret $AWS_SECRET_KEY

serverless plugin install -n serverless-wsgi
serverless plugin install -n serverless-python-requirements
serverless plugin install -n serverless-deployment-bucket
```

### Deploy app using CloudFormation

```bash
# You need to be in the Flask app directory
pushd "$(git rev-parse --abbrev-ref HEAD)/api/src/app"

# Currently fails
serverless deploy --verbose
```

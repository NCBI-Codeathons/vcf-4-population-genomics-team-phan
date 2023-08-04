# API

## Configure required environment variables

```bash
# add custom values
export AWS_ACCESS_KEY=
export AWS_SECRET_KEY=
export AWS_REGION=us-east-1
```

## Run a local server

You need to have a virtual environment created to run the app.

```bash
source "$(git rev-parse --show-toplevel)/api/dev_env.sh"
```

Once the v.e. is created, you can start the server:

```bash
export FLASK_ENV=development
export FLASK_APP=app.py

pushd "$(git rev-parse --show-toplevel)/api/src/app"
flask run --host=0.0.0.0
popd
```

## Use `serverless.com` tools to deploy the server

### Set up `serverless.com` tools

You can tweak some steps (paths, command line parameters, etc.) to suit your
needs.

```bash
npm config set prefix '~/.local/'
npm install -g serverless

export PATH=~/.local/bin/:$PATH

serverless config credentials --provider aws --key $AWS_ACCESS_KEY --secret $AWS_SECRET_KEY

serverless plugin install -n serverless-wsgi
serverless plugin install -n serverless-python-requirements
serverless plugin install -n serverless-deployment-bucket
```

### Deploy the app using CloudFormation through `serverless`

```bash
# You need to be in the Flask app directory
pushd "$(git rev-parse --show-toplevel)/api/src/app"

# If this fails, you may lack the necessary permissions (see below)
serverless deploy --verbose
```

The `deploy` command will fail if you lack the necessary permissions. You would
need to attach the policy in file
[`serverless_policies.json`](./serverless_policies.json) to the user account
you are using to deploy.

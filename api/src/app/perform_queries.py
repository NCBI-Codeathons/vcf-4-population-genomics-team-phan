import boto3
from botocore.exceptions import ClientError
from io import StringIO
import json
from pathlib import Path
from os import environ
import time
import tempfile


# TODO improve the quality of this code. It was hastily created
#      It works, but quality is not at the desired level

# NOTE We have not yet integrated querying the model
#      from this app. Only two queries in natural language (NL) are supported.
#      Converting NL to SQL is simulated.


class VarAIException(Exception):
    def __init__(self, message, error_code=500):
        self.error_code = error_code
        super().__init__(message)


def _get_region_name() -> str:
    """Dynamically find out the current region."""
    return boto3.DEFAULT_SESSION.region_name \
        if boto3.DEFAULT_SESSION \
        else boto3.Session().region_name


def _get_secret(region_name, secret_name):
    """Securely retrieve the access and secret keys needed"""
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    return get_secret_value_response['SecretString']


AWS_REGION = environ.get('AWS_REGION', _get_region_name())
AWS_ACCESS_KEY = environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = environ.get('AWS_SECRET_KEY')

if not AWS_ACCESS_KEY or not AWS_ACCESS_KEY:
    secret = json.loads(_get_secret(AWS_REGION, "teamphan-svc-account"))
    AWS_ACCESS_KEY = secret["AWS_ACCESS_KEY"]
    AWS_SECRET_KEY = secret["AWS_SECRET_KEY"]

S3_BUCKET_NAME = "teamphan-athena-results"
S3_OUTPUT_DIRECTORY = "output"
S3_STAGING_DIR = f"s3://{S3_BUCKET_NAME}/{S3_OUTPUT_DIRECTORY}"


def _query_athena(athena_client, db_name: str, query_str: str, staging_dir: str):
    """Perform a query against an Athena backend."""
    query_response = athena_client.start_query_execution(
        QueryString=query_str,
        QueryExecutionContext={"Database": db_name},
        ResultConfiguration={
            "OutputLocation": staging_dir,
            "EncryptionConfiguration": {"EncryptionOption": "SSE_S3"},
        },
    )

    execution_id = query_response['QueryExecutionId']
    query_status = {}
    # TODO improve the following code that waits for the query to complete.
    while True:
        queryExecution = athena_client.get_query_execution(
            QueryExecutionId=execution_id)
        query_status = queryExecution["QueryExecution"]["Status"]
        if query_status["State"] in ['QUEUED', 'RUNNING']:
            time.sleep(0.001)
        else:
            break

    if "State" in query_status:
        if query_status["State"] == "SUCCEEDED":
            output_file = f"{execution_id}.csv"
            return output_file, output_file + ".metadata"

        print(query_status["State"], "\n")

    if "StateChangeReason" in query_status:
        print("StateChangeReason", query_status["StateChangeReason"], "\n")

    if 'AthenaError' in query_status:
        raise VarAIException(
            "An error occurred: " + query_status['AthenaError'])

    raise VarAIException("An unknown error occurred")


athena_client = boto3.client(
    "athena",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)


# NOTE we are using a look up table while the actual model is being worked on
_NL_TO_SQL = {
    "Retrieve Run and variation columns for variation E484K":
        "SELECT distinct Run, variation FROM annotated_variations WHERE variation = 'E484K'",
    "variant at position 27513":
        "SELECT * FROM annotated_variations WHERE POS = 27513"
}


def _nl_to_sql(nl_query: str) -> str:
    """Convert natural language queries to SQL."""
    sql = _NL_TO_SQL.get(nl_query)
    if sql:
        return sql

    raise VarAIException(
        "Sorry, we could not understand your request: " + nl_query, 422)


def _perform_query(nl_query: str, athena_client, s3_client):
    query_str = _nl_to_sql(nl_query) + " LIMIT 1000"  # TODO replace this
    db_name = "ncbi-vcf-codeathon-rc-db1"
    output_filename, _ = _query_athena(
        athena_client, db_name, query_str, S3_STAGING_DIR)

    with tempfile.NamedTemporaryFile() as tmp:
        temp_file_location: str = tmp.name

        s3_client.download_file(
            S3_BUCKET_NAME,
            f"{S3_OUTPUT_DIRECTORY}/{output_filename}",
            temp_file_location,
        )

        # If we get to create the REST API, it will return a stream, not a file location
        data = Path(temp_file_location).read_text()
        if data:
            return StringIO(data)

        raise VarAIException("No results found", 404)


def perform_query(nl_query: str):
    return _perform_query(nl_query, athena_client, s3_client)

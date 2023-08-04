import boto3
import json
from botocore.exceptions import ClientError
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.schema import Table, MetaData
from sqlalchemy import func, select

from langchain.llms import LlamaCpp
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_experimental.sql import SQLDatabaseChain


def get_secret(region_name):
    secret_name = "teamphan-svc-account"

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


AWS_REGION = 'us-east-1'
secret = json.loads(get_secret(AWS_REGION))
AWS_ACCESS_KEY = secret["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = secret["AWS_SECRET_KEY"]

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
model_path_llama_7b = "/home/ec2-user/llama.cpp/models/7B/ggml-model-q4_0.bin"
model_path_llama2_7b = "/home/ec2-user/llama.cpp/models/llama-2-7b/ggml-model-q4_0.bin"
llm = LlamaCpp(model_path=model_path_llama2_7b,
               n_ctx=4096,
               callback_manager=callback_manager, verbose=True)

schema_name = 'default'
s3_staging_dir = 's3://teamphan-athena-results/output'
conn_str = "awsathena+rest://" + AWS_ACCESS_KEY + ':' + AWS_SECRET_KEY \
    + "@athena.us-east-1.amazonaws.com:443" \
    "/" + schema_name + "?s3_staging_dir=" + s3_staging_dir
engine = create_engine(conn_str)
db = SQLDatabase(engine)
db = SQLDatabase.from_uri(
    "sqlite:///../../chinook-database/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite")
db_chain = SQLDatabaseChain.from_llm(
    llm, db, verbose=True, use_query_checker=True)
db_chain.run("How many albums are there?")
# toolkit=SQLDatabaseToolkit(db=db, llm=llm)
# agent_executor=create_sql_agent(
#     llm=llm,
#     toolkit=toolkit,
#     verbose=True,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
# agent_executor.run("Describe the Album table")

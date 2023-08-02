# import libraries
import openai
import numpy as np
import pandas as pd
import streamlit as st
import boto3
import time

# required functions

def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index = False)

def generate_sql(query):
    model_engine = "text-davinci-003"
    prompt = (
        f"Translate the following natural language query to SQL:\n"
        f"{query}\n"
        f"SQL:"
    )
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        temperature=0,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["#", ";"]
    )
    return response.choices[0].text.strip()

def create_table_definition():
    prompt="""### SQL table, with its properties:
    #
    # annotated_variations({})
    #
    """.format(['run', 'CHR', 'POS', 'REF', 'ALT', 'DP', 'G_AD_2', 'EFFECT', 'FUNCLASS',
       'CODON', 'variation', 'AA_LEN', 'protein_name', 'ref_aa', 'alt_aa',
       'protein_position', 'ver', 'updated'])
    return prompt

def adjust_query(qstring):
    if '?' in qstring:
        query.replace('?', '')
    return qstring

def combine_prompts(schema, query_prompt):
    definition=create_table_definition()
    query_init_string=f"### A query to answer: {query_prompt}"
    return schema+query_init_string

def run_athena_query(client, query_string, athena_db, outdir):
    query_response = client.start_query_execution(
    QueryString = query_string,
    QueryExecutionContext={"Database": athena_db},
    ResultConfiguration={
        "OutputLocation": outdir,
        "EncryptionConfiguration": {"EncryptionOption": "SSE_S3"},
    },
)
    query_status={}
    while True:
        queryExecution = client.get_query_execution(QueryExecutionId=query_response['QueryExecutionId'])
        query_status = queryExecution["QueryExecution"]["Status"]
        if query_status["State"] in ['QUEUED', 'RUNNING']:
            time.sleep(0.001)
        else:
            break

    if "State" in query_status:
        print(query_status["State"], "\n")
    if "StateChangeReason" in query_status:
        print("StateChangeReason", query_status["StateChangeReason"], "\n")
    if 'AthenaError' in query_status:
        print("An error occurred: ", query_status['AthenaError'])
    
    query_execution_id = query_response['QueryExecutionId']
    
    return query_execution_id

def results_to_dataframe(results):
    columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = []
    for row in results['ResultSet']['Rows'][1:]:
        rows.append([field['VarCharValue'] for field in row['Data']])
    df = pd.DataFrame(rows, columns=columns)
    return df

#------------------------------------------------------------------------------------------------------------
# session_state vars
if 'sql_query' not in st.session_state: # create session state variable for client auth 
        st.session_state['sql_query'] = None

# Load OpenAI API key from secrets file
openai.api_key=st.secrets["openai_key"]
aws_access = st.secrets["aws_access"]
aws_secret = st.secrets["aws_secret"]

# Adding some texts to explain the purpose of the app
st.sidebar.header('Var.ai')

st.sidebar.write("""
         ######  This app uses streamlit and OpenAI APIs to allow users to retrieve data on VCF data
         """)

# Create table property string
table_schema = create_table_definition()
# Text input where the user enter the text to be translated to SQL query
query = st.text_input('Enter your search question/query', '')
sql_query = st.text_input('Enter SQL search', '')
#if the Generate SQL query if clicked 
if st.button('Run search'):
  #if text input is not empty
  if len(query) > 0:
    
    # process user search 
    query_proc = adjust_query(query) # remove ?
    query_final = combine_prompts(table_schema, query_proc)
    #st.write(query_final)
    #Generate sql query
    Respo=generate_sql(query_final)
    
    st.session_state['sql_query'] =  Respo
    
    #print sql query
    st.write('SQL query being used')
    st.write(st.session_state['sql_query'])
    
    # run user search
    region = 'us-east-1'
    schema_name = 'ncbi-vcf-codeathon-rc-db1'
    S3_STAGING_DIR = "s3://teamphan-output/streamlit_out/"

    # establish client
    athena_client = boto3.client(
        "athena",
        aws_access_key_id=aws_access,
        aws_secret_access_key=aws_secret,
        region_name=region,
    )

    # run query
    search_id= run_athena_query(athena_client, st.session_state['sql_query'], schema_name, S3_STAGING_DIR)

    results = athena_client.get_query_results(QueryExecutionId=search_id)

    # conver results to df
    results_df = results_to_dataframe(results)

    st.dataframe(results_df)
    
    st.download_button(label="Download data as CSV", data=convert_df(results_df),file_name=output_name, mime='text/csv')

if st.button('Run SQL query'):
    st.session_state['sql_query'] = sql_query

    # run user search
    region = 'us-east-1'
    schema_name = 'ncbi-vcf-codeathon-rc-db1'
    S3_STAGING_DIR = "s3://teamphan-output/streamlit_out/"

    # establish client
    athena_client = boto3.client(
        "athena",
        aws_access_key_id=aws_access,
        aws_secret_access_key=aws_secret,
        region_name=region,
    )

    # run query
    search_id= run_athena_query(athena_client, st.session_state['sql_query'], schema_name, S3_STAGING_DIR)

    results = athena_client.get_query_results(QueryExecutionId=search_id)

    # conver results to df
    results_df = results_to_dataframe(results)

    st.dataframe(results_df)
    
    st.download_button(label="Download data as CSV", data=convert_df(results_df),file_name=output_name, mime='text/csv')
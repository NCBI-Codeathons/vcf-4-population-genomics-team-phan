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
    prompt="""### SQL table, with the schema: CREATE TABLE annotated_variations (
    run VARCHAR(255), -- SRA accession, run accession
    chr VARCHAR(50),  -- chromosome
    pos BIGINT,       -- DNA or RNA base position
    ref VARCHAR(255), -- reference allele
    alt VARCHAR(255), -- alternate or variant allele
    dp BIGINT,
    g_ad_2 BIGINT,
    effect VARCHAR(255), -- effect values are CODON_CHANGE_PLUS_CODON_DELETION, CODON_CHANGE_PLUS_CODON_INSERTION, CODON_DELETION, CODON_INSERTION, FRAME_SHIFT, FRAME_SHIFT+START_LOST, INTERGENIC, NON_SYNONYMOUS_CODING, STOP_GAINED, SYNONYMOUS_CODING
    funclass VARCHAR(255), -- function class(funclass) or consequence values are MISSENSE, NONE, NONSENSE, SILENT 
    codon VARCHAR(255), -- codon encoding amino acid https://en.wikipedia.org/wiki/DNA_and_RNA_codon_tables
    variation VARCHAR(255), -- variation allele
    aa_len BIGINT,  -- variation amino acid length
    protein_name VARCHAR(255), -- protein_name's aliases are "gene" and "gene name".  For demo until gene info is loaded.
    ref_aa VARCHAR(255), -- reference amino acid, wild-type amino acid
    alt_aa VARCHAR(255), -- alternate or variant amino acid
    protein_position BIGINT, -- protein position of ref_aa and alt_aa
    ver VARCHAR(50),
    updated TIMESTAMP
);
    """
    return prompt

def adjust_query(qstring):
    if '?' in qstring:
        query.replace('?', '')
    return qstring

def combine_prompts(schema, query_prompt):
    schema=create_table_definition()
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
        rows.append([field['VarCharValue'] for field in row['Data'] if len(field) != 0])
    df = pd.DataFrame(rows, columns=columns)
    return df

def escape_markdown(text): # print out SQL query with correct formatting
    MD_SPECIAL_CHARS = "\`*_{}[]()#+-.!"
    for char in MD_SPECIAL_CHARS:
        text = text.replace(char, "\\"+char)
    return text

def contains_str_from_list(input_str, elements_list): # check if a string contains any words from list
    concerns = any(element in input_str for element in elements_list)

    if concerns:
        return True
    else:
        return False
    

def check_string(input_str): # check for any invalid words and raise correct exception
    # check if str conatins any security concern commands
    sec_check = contains_str_from_list(input_str, st.session_state['security_catch'])
    if 'CREATE' in input_str:
        raise ExecutionFailure("SQL error - Can't execute CREATE command")
    elif sec_check:
        raise InvalidSecurityQuery(f"""Query can't be executed due to security.\n
Your query contains one or more of the following invalid SQL commands:
'INSERT', 'UPDATE', 'DELETE', 'ALTER TABLE', 'CREATE TABLE',
'DROP TABLE', 'TRUNCATE TABLE', 'MERGE', 'RENAME TABLE', 'RENAME'""")

# custom exceptions
class ExecutionFailure(Exception):
   def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidSecurityQuery(Exception):
   def __init__(self, message):
        self.message = message
        super().__init__(self.message)
                                  
#------------------------------------------------------------------------------------------------------------
# session_state vars
if 'sql_query' not in st.session_state: # create session state variable for client auth 
        st.session_state['sql_query'] = None

if 'security_catch' not in st.session_state:
    st.session_state['security_catch'] = ['INSERT', 'UPDATE', 'DELETE', 'ALTER TABLE',
                                          'CREATE TABLE', 'DROP TABLE', 'TRUNCATE TABLE',
                                          'MERGE', 'RENAME TABLE', 'RENAME']
#------------------------------------------------------------------------------------------------------------
## Main script
# Load OpenAI API key from secrets file
openai.api_key=st.secrets["openai_key"]
aws_access = st.secrets["aws_access"]
aws_secret = st.secrets["aws_secret"]

# Adding some texts to explain the purpose of the app
st.sidebar.write('# Var.ai')

st.sidebar.write("""
         This app uses streamlit and OpenAI APIs to allow users to retrieve data on VCF data using natural language text
         """)
st.sidebar.write("##### Proof of Concept for NCBI VCF for Population Genomics Codeathon - Team Phan")

# Create table property string
table_schema = create_table_definition()

with st.container():
    st.subheader('Natural Text Search')
    # Text input where the user enter the text to be translated to SQL query
    st.text('''Enter a question to obtain results''')
    query = st.text_area('Enter your search question', '')
    #if the Generate SQL query if clicked 
    if st.button('Run search'):
        # check user input 
        try:
            check_string(query)
     
             #if text input is not empty
            if len(query) > 0:
     
                # process user search 
                query_proc = adjust_query(query) # remove '?' if present
                query_final = combine_prompts(table_schema, query_proc)
                #Generate sql query
                Respo=generate_sql(query_final)
                clean_response = escape_markdown(Respo)
                
                st.session_state['sql_query'] =  Respo
                
                #print sql query
                st.write('SQL query being used:')
                st.markdown(clean_response)
                
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
                    
                # allow user to download their filtered output
                st.download_button(label="Download data as CSV", data=convert_df(results_df), mime='text/csv')
     
        except ExecutionFailure as e:
            st.text(f"{e}")
        except InvalidSecurityQuery as i:
            st.text(f"{i}")

     
#with st.container():
 #   st.subheader('SQL Query')
  #  st.text('''Only use this if you know the exact SQL query you want to use.
#Will not create a SQL query for you.''')
 #   sql_query = st.text_area('Enter SQL query', '')
  #  if st.button('Run SQL query'):
   #     try:
    #        check_string(query)
     #       st.session_state['sql_query'] = sql_query

            # run user search
      #      region = 'us-east-1'
       #     schema_name = 'ncbi-vcf-codeathon-rc-db1'
        #    S3_STAGING_DIR = "s3://teamphan-output/streamlit_out/"

            # establish client
         #   athena_client = boto3.client(
          #      "athena",
           #     aws_access_key_id=aws_access,
            #    aws_secret_access_key=aws_secret,
             #   region_name=region,
            #)

            # run query
            #search_id= run_athena_query(athena_client, st.session_state['sql_query'], schema_name, S3_STAGING_DIR)

            #results = athena_client.get_query_results(QueryExecutionId=search_id)

            # conver results to df
            #results_df = results_to_dataframe(results)

            #st.dataframe(results_df)
            # allow user to download their filtered output
            #st.download_button(label="Download data as CSV", data=convert_df(results_df), mime='text/csv')

       # except ExecutionFailure as e:
        #    st.text(f"{e}")
        #except InvalidSecurityQuery as i:
         #   st.text(f"{i}")


 

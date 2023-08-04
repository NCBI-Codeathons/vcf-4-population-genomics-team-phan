# Langchain using Llama

## Project Goals

This is to evaluate and demonstrate using `langchain` with Open Source Llama model(s), so
that users do not need to use paid GPT models.

## How to run

```sh
git clone https://github.com/NCBI-Codeathons/vcf-4-population-genomics-team-phan.git
cd langchain
python3 -m virtualenv env_langchain
source env_langchain/bin/activate
pip install -r requirements.txt
python langchain.py
```

More information about evaluating and demonstrating using `langchain` is in [`doc/llama_ec2_provision.md`](../doc/llama_ec2_provision.md).
# Evaluate and demonstrate using `langchain` with Open Source Llama model(s)

```none
EC2 t2.xlarge, 1T
```

```bash
sudo yum install emacs
sudo yum install git -y
sudo yum install virtualenv
sudo yum groupinstall "Development Tools"
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make
cd models

# Following download takes a lot of time.  Better do it first
# download original 7B, 13B, 30B, 65B model weights (219 GB)
# Note: not sure if this violates copyright, because the weights belongs to Meta,
# but this download is not from Meta.
curl -o- https://raw.githubusercontent.com/shawwn/llama-dl/56f50b96072f42fb2520b1ad5a1d6ef30351f23c/llama.sh | bash

# prepare python virtual environment for conversion
python3 -m virtualenv env_model_conversion
source env_model_conversion/bin/activate
pip install -r requirements.txt

# convert the 7B model to ggml FP16 format
python3 convert.py models/7B/

# quantize the model to 4-bits using model 7B as an example (using q4_0 method)
./quantize models/7B/ggml-model-f16.bin models/7B/ggml-model-q4_0.bin q4_0

# exit python virtual environment
deactivate

# run the inference use model 7B as an example
# models 30B and 65B are extremely slow to run on AWS EC2 t2.xlarge
# e.g., 34s for 7B, 1m 45s for 13B, 116m for 30B
./main -m models/7B/ggml-model-q4_0.bin -n 128 -p 'who is the first man on the moon'

# We might not need llama.cpp.  Looks we can run models using python
pip install llama-cpp-python

from llama_cpp import Llama
llm = Llama(model_path="./models/7B/ggml-model.bin")
output = llm("Q: Name the planets in the solar system? A: ", max_tokens=128, stop=["Q:", "\n"], echo=True)
print(output)
```

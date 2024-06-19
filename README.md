Go to the config folder and modify the run.sh:

export OPENAI_API_KEY='sk-xxxxx' -> replace with your OPENAI api-key

nemoguardrails chat --config='your config folder'  


and execute the run.sh to up chat server.

** Create env ***

virtualenv -p  python3.10  ./env 
source ./env/bin/activate

Run in:
python --version
Python 3.10.13



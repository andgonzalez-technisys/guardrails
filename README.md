
1.- ** Create env ***

    virtualenv -p  python3.10  ./env 
    source ./env/bin/activate

2.-  Install requirements.txt  app/requirements.txt

3.-  Modify the run.sh:

    export OPENAI_API_KEY='sk-xxxxx' -> replace with your OPENAI api-key
    
    nemoguardrails chat --config='your config folder'  


4.-execute the ./run.sh to up chat server.



    Run in:
    python --version
    Python 3.10.13



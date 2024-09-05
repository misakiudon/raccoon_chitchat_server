# raccoon_chitchat_server
Server for llm-tts chitchat application.

# How to use
Worked in python version 3.9 and 3.10. 

## Install

```sh
git clone https://github.com/misakiudon/raccoon_chitchat_server.git
cd raccoon_chitchat_server
python -m venv venv
source venv/bin/activate #Linux
# venv\Scripts\activate # Windows
pip install -r requirements.txt
```

## Run
```sh
ngrok authtoken {your_ngrok_authtoken}
python server.py
```

## Run with client
```
Models loaded: 1
Ngrok tunnel open at: NgrokTunnel: **"https://server-ngrok-url.ngrok-free.app"** -> "http://localhost:5000"
 * Serving Flask app 'server'
 * Debug mode: off
```
Copy the ngrok url and use as argument for client. 

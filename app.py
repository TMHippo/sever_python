import argparse
import uuid
from google.cloud.dialogflowcx_v3beta1.services.agents import AgentsClient
from google.cloud.dialogflowcx_v3beta1.services.sessions import SessionsClient
from google.cloud.dialogflowcx_v3beta1.types import session


from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
import uvicorn

from constants import *
import os
        
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="app.json"

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Set up
project_id = Project_id
location_id = Location_id
agent_id = Agent_id
agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"
language_code = "vi"

def get_session():
    session_id = uuid.uuid4()
    session_path = f"{agent}/sessions/{session_id}"
    client_options = None
    agent_components = AgentsClient.parse_agent_path(agent)
    location_id = agent_components["location"]
    if location_id != "global":
        api_endpoint = f"{location_id}-dialogflow.googleapis.com:443"
        client_options = {"api_endpoint": api_endpoint}
    session_client = SessionsClient(client_options=client_options)
    return session_path, session_client

session_path, session_client = get_session()

@app.get('/')
async def introduce():
    return {"Datascient Challenge: KHDLGang"}

@app.get('/reload')
async def reload():
    global session_path, session_client
    session_path, session_client = get_session()
    return JSONResponse({"Status": "Sucessful"})

@app.get('/detect_intent_text')
async def detect_intent_texts(text: str):
    text_input = session.TextInput(text=text)
    query_input = session.QueryInput(text=text_input, language_code=language_code)
    request = session.DetectIntentRequest(
        session=session_path, query_input=query_input
    )
    response = session_client.detect_intent(request=request)

    response_messages = [
        " ".join(msg.text.text) for msg in response.query_result.response_messages
    ]
    results = ' '.join(response_messages)
    return JSONResponse({'response': results})

# if __name__ == '__main__':
#     uvicorn.run("app:app", host=host_api, port=Port, reload=True)
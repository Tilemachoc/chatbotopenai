import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from main import generate_response
from typing import Optional
from pydantic import BaseModel
import json

app = FastAPI()

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class messageParam(BaseModel):
   message: str
   assist_id: str
   thread_id: Optional[str]
   intent_thread_id: Optional[str] 
   instructions_bool: Optional[bool] = False


@app.post("/get_response")
def get_response(message_param: messageParam):
   client = openai.OpenAI()
   try:
      response_dict = generate_response(
         client=client,
         message=message_param.message,
         assist_id=message_param.assist_id,
         thread_id=message_param.thread_id,
         intent_thread_id=message_param.intent_thread_id,
         instructions_bool=message_param.instructions_bool
         )
      response_content = json.dumps(response_dict)
      response = Response(content=response_content)
      return response
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))


    
app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://127.0.0.1:5500"],
   allow_credentials=True,
   allow_methods=["POST"],
   allow_headers=["Content-Type"],
)


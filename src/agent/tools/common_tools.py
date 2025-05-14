

import base64
from datetime import datetime, UTC
import hashlib
import hmac
import os

from dotenv import load_dotenv
from src.core.interfaces.tool import Tool
from datetime import timezone as tz

from src.services.llm_service import get_llm_service
from cryptography.fernet import Fernet

load_dotenv()

class GetDateTool(Tool):
    def name(self) -> str:
        return "generate_date"
    
    def description(self) -> str:
        return (
            "Convert a natural-language date/time expression into an exact ISO-8601 date or datetime. "
        )
    
    def run(self, args):
        ref_ts = datetime.now().isoformat()
        expression = args["expression"]
        timezone = args["timezone"] or tz.utc

        system_prompt = (
            "You are a precise date/time parser."
            "Given a natural-language expression and a reference timestamp + timezone"
            "always output ONLY valid JSON with format {\"datetime\": \"YYYY-MM-DDTHH:MM:SS±HH:MM\"}."
            "don't output anything else."
        )
        user_prompt = (
            f"Expression: \"{expression}\"\n"
            f"Reference Current Timestamp: \"{ref_ts}\"\n"
            f"Timezone: \"{timezone}\"\n"
            "Return the exact ISO-8601 date/time in the following format: {format}"
        )

        # 2) Call the LLM
        llm_service = get_llm_service()
        resp = llm_service.query_execute(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            max_token=200
        )

        return resp
    def get_args_schema(self):
        return [
            {"name": "expression", "type": "str", "description": "Natural-language date/time expression", "status": "required"},
            {"name": "timezone", "type": "str", "description": "Timezone of the output date/time, Optional IANA timezone (e.g. 'Asia/Jakarta').", "status": "required"},
        ]
    
    def output_schema(self):
        return "str"
    

class GetUserIdTool(Tool):
    def __init__(self, user_id) -> None:
        self.id = user_id
    def name(self) -> str:
        return "get_user_id"
    
    def description(self) -> str:
        return "Get user ID from the encrypted user ID"
    
    def run(self, args): 
        return self.create_encrypted_user_id(self.id)

    def output_schema(self):
        return "str"
    def create_encrypted_user_id(self, user_id):
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise RuntimeError("Set MY_SECRET_KEY to your Fernet key!")
        digest = hmac.new(secret_key.encode(), user_id.encode(), digestmod=hashlib.sha256).hexdigest()
        return digest
    
    # def create_encrypted_user_id(self, user_id):
    #     # encrypt user_id with a key from env SECRET_KEY
    #     secret_key = os.getenv("SECRET_KEY")
    #     if not secret_key:
    #         raise RuntimeError("Set MY_SECRET_KEY to your Fernet key!")
        
    #     fernet = Fernet(secret_key.encode())
    #     encrypted_user_id = fernet.encrypt(user_id.encode()).decode()
    #     return encrypted_user_id
       
        
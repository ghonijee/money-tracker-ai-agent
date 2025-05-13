

from datetime import datetime
from src.core.interfaces.tool import Tool
from datetime import timezone as tz

from src.services.llm_service import get_llm_service

class GetDateTool(Tool):
    def name(self) -> str:
        return "generate_date"
    
    def description(self) -> str:
        return (
            "Convert a natural-language date/time expression into an exact ISO-8601 date or datetime. "
            "If no reference is provided, it will assume “now”."
        )
    
    def run(self, args):
        # 1) Build context
        ref_ts = args["reference"] or datetime.now ().isoformat()
        expression = args["expression"]
        timezone = args["timezone"] or tz.utc
        format = args["format"] or "%Y-%m-%dT%H:%M:%S%z"

        system_prompt = (
            "You are a precise date/time parser. "
            "Given a natural-language expression and a reference timestamp + timezone, "
            "output ONLY valid JSON like {\"datetime\": \"YYYY-MM-DDTHH:MM:SS±HH:MM\"}."
        )
        user_prompt = (
            f"Expression: \"{expression}\"\n"
            f"Reference Timestamp: \"{ref_ts}\"\n"
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
        )

        return resp
    def get_args_schema(self):
        return [
            {"name": "expression", "type": "str", "description": "Natural-language date/time expression"},
            {"name": "reference", "type": "str", "description": "Reference date/time, Defaults to now in local timezone."},
            {"name": "timezone", "type": "str", "description": "Timezone of the output date/time, Optional IANA timezone (e.g. 'Asia/Jakarta')."},
            {"name": "format", "type": "str", "description": "Format of the output date/time"}
        ]
    
    def output_schema(self):
        return "str"
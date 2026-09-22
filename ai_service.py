import json
from openai import OpenAI
from config import OPENAI_API_KEY
from ai_tool_schemas import TOOLS
from ai_tools import (
    get_pitch_info,
    get_pricing_info,
    check_pitch_availability,
    get_booking_by_reference,
)
from booking_logic import now_in_nigeria
from datetime import datetime  
import logging
logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

AVAILABLE_FUNCTIONS = {
    "get_pitch_info": get_pitch_info,
    "get_pricing_info": get_pricing_info,
    "check_pitch_availability": check_pitch_availability,
    "get_booking_by_reference": get_booking_by_reference,
}

def build_system_prompt():
    now = now_in_nigeria()
    today_str = now.strftime("%A, %B %d, %Y")
    current_time_str = now.strftime("%I:%M %p")
    return (
        f"You are a helpful assistant for Elite Football Pitch, a football "
        f"pitch booking service in Nigeria. The current date and time in "
        f"Nigeria (West Africa Time) is {today_str}, {current_time_str}. "
        f"Use this to correctly resolve relative dates and times like "
        f"'tomorrow', 'this weekend', or 'in an hour' into exact values "
        f"before calling any tool. "
        f"When calling tools, pass times in 24-hour HH:MM format as the "
        f"tools require. However, when speaking to the user, ALWAYS "
        f"present times in 12-hour format with AM/PM (e.g. '3:00 PM', "
        f"never '15:00'). "
        f"Answer questions about pricing, availability, facilities, opening "
        f"hours, and booking status ONLY by using the tools provided to you. "
        f"Never guess, assume, or make up any pricing, availability, date, "
        f"time, or policy information. If a tool doesn't give you enough "
        f"information to answer, say so honestly rather than guessing. "
        f"You cannot create, modify, or cancel bookings through this chat — "
        f"if asked, direct the user to the normal booking form on the website."
    )

MAX_HISTORY_MESSAGES = 10

def get_ai_response(user_message, conversation_history=None):
    messages = [{"role": "system", "content": build_system_prompt()}]

    if conversation_history:
        trimmed_history = conversation_history[-MAX_HISTORY_MESSAGES:]
        messages.extend(trimmed_history)

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )

    reply = response.choices[0].message

    if not reply.tool_calls:
        return reply.content

    messages.append(reply)

    for tool_call in reply.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

        if not function_to_call:
            result = {"error": f"Unknown tool: {function_name}"}
        else:
            try:
                result = function_to_call(**function_args)
            except Exception as e:
                logger.error(f"Tool '{function_name}' failed with args {function_args}: {e}")
                result = {"error": f"Something went wrong while checking that. Please rephrase your question."}

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })

    second_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    return second_response.choices[0].message.content
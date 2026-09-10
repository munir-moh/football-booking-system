# ai_service.py
#
# This is the core "AI brain" of the assistant. It:
# 1. Sends the conversation + available tools to OpenAI
# 2. If OpenAI wants to call a tool, runs the real Python function
# 3. Sends the tool's result back to OpenAI
# 4. Returns OpenAI's final, natural-language answer
#
# Flask (app.py) will call get_ai_response() from this file.
# Nothing here talks to React directly.

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

client = OpenAI(api_key=OPENAI_API_KEY)

# Maps a tool's name (as OpenAI will refer to it) to the real Python
# function that should run when that tool is requested.
AVAILABLE_FUNCTIONS = {
    "get_pitch_info": get_pitch_info,
    "get_pricing_info": get_pricing_info,
    "check_pitch_availability": check_pitch_availability,
    "get_booking_by_reference": get_booking_by_reference,
}

SYSTEM_PROMPT = (
    "You are a helpful assistant for Elite Football Pitch, a football "
    "pitch booking service. Answer questions about pricing, availability, "
    "facilities, opening hours, and booking status ONLY by using the "
    "tools provided to you. Never guess, assume, or make up any pricing, "
    "availability, or policy information. If a tool doesn't give you "
    "enough information to answer, say so honestly rather than guessing. "
    "If the user gives a vague date like 'tomorrow', ask them to confirm "
    "the exact date before calling a tool that needs one. "
    "You cannot create, modify, or cancel bookings through this chat — "
    "if asked, direct the user to the normal booking form on the website."
)


def get_ai_response(user_message, conversation_history=None):
    """
    Takes the user's new message and the prior conversation (if any),
    and returns the AI's final text reply.

    conversation_history: a list of {"role": "user"/"assistant", "content": "..."}
    from earlier turns in this chat, or None for a fresh conversation.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": user_message})

    # First call: let OpenAI see the message and decide if it needs a tool
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )

    reply = response.choices[0].message

    # If OpenAI did NOT ask for a tool, we already have the final answer
    if not reply.tool_calls:
        return reply.content

    # Otherwise, OpenAI wants one or more tools run. Add its request to
    # the conversation, then run each tool and add the result too.
    messages.append(reply)

    for tool_call in reply.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
        if function_to_call:
            result = function_to_call(**function_args)
        else:
            result = {"error": f"Unknown tool: {function_name}"}

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })

    # Second call: give OpenAI the tool results so it can write the
    # final, natural-language answer
    second_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    return second_response.choices[0].message.content
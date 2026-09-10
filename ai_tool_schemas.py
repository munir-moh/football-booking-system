# ai_tool_schemas.py
#
# These describe our Python functions (from ai_tools.py) in the exact
# format OpenAI's API expects for "tool use" / function calling.
# Each entry tells the AI: the tool's name, what it does, and what
# arguments (if any) it needs to call it.
#
# IMPORTANT: this file only describes the tools. It does not run them.
# The actual running happens in the AI service (Step 5), which reads
# the AI's request and calls the matching real function from ai_tools.py.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_pitch_info",
            "description": (
                "Get general information about the football pitch: "
                "opening and closing hours, available facilities, "
                "discounts, and the booking policy. Use this for "
                "questions like 'what time does it open', "
                "'what facilities are there', or 'what's the policy'."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pricing_info",
            "description": (
                "Get the pitch's pricing: price per hour, currency, "
                "and the minimum number of hours that can be booked. "
                "Use this for questions like 'how much does it cost' "
                "or 'what's the minimum booking duration'."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_pitch_availability",
            "description": (
                "Check whether the pitch is available for a specific "
                "date, start time, and duration. Use this for questions "
                "like 'is it free tomorrow at 5pm' or 'can I book 2 hours "
                "on Friday morning'. Always confirm the exact date and "
                "time with the user before calling this if they were vague."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format, e.g. 2026-01-25"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in 24-hour HH:MM format, e.g. 17:00"
                    },
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours requested, e.g. 2"
                    }
                },
                "required": ["date", "start_time", "hours"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_booking_by_reference",
            "description": (
                "Look up the status of an existing booking using its "
                "reference code (format like FP-20260112-2239-DYXU). "
                "Use this only when the user provides a specific "
                "reference code and asks about its status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reference": {
                        "type": "string",
                        "description": "The booking reference code, e.g. FP-20260112-2239-DYXU"
                    }
                },
                "required": ["reference"]
            }
        }
    }
]
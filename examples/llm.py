import json
from groq import Groq
from chatbox.config import settings
from pydantic import BaseModel

client = Groq(api_key=settings.groq_api_key)


def get_weather(city: str) -> str:
  """Get the weather of a city"""
  return "22 degrees Celsius"

available_functions = {
    "get_weather": get_weather,
}

def execute_tool_call(tool_call):
    """Parse and execute a single tool call"""
    function_name = tool_call.function.name
    function_to_call = available_functions[function_name]
    function_args = json.loads(tool_call.function.arguments)
    
    # Call the function with unpacked arguments
    return function_to_call(**function_args)

# Schema for get_weather tool
weather_schema = {
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Get the weather of a city",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "Name of the city"
        }
      },
      "required": ["city"]
    }
  }
}

class TeacherInfo(BaseModel):
  name: str
  age: int

system_prompt = """
You are a helpful tutor for a programming language called Python.
You know about Alexandru Ghiura who is the teacher of the course, has 20y and is veryyyyyy smart
"""

messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]


def add_message( text: str):
  messages.append({"role": "user", "content": text})

def add_ai_message(text: str):
  messages.append({"role": "assistant", "content": text})

def run_completion(messages):
  completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=messages,
    tools=[weather_schema],
    tool_choice="auto",
    # stream=False,
    # response_format={
    #     "type": "json_schema",
    #     "json_schema": {
    #         "name": "my_output",
    #         "schema": TeacherInfo.model_json_schema()
    #     }
    # }
  )

  return completion.choices[0].message

#print(TeacherInfo.model_json_schema())


add_message("What is the weather in Bucharest?")
response = run_completion(messages)

if response.tool_calls:
  for tool_call in response.tool_calls:
    tool_result = execute_tool_call(tool_call)
    
    messages.append({
      "role": "tool",
      "tool_call_id": tool_call.id,
      "name": tool_call.function.name,
      "content": str(tool_result)
    })

  response = run_completion(messages)
  add_ai_message(response.content)
  print(response.content)

  for message in messages:
    print(message)



# while True:
#   try:
#     # 1. add user message
#     user_input = input("> ")
#     add_message(user_input)

#     # 2. run messages and add ai meesage
#     response = run_completion(messages)
#     add_ai_message(response)
    
#     print(messages)

#     # 3. print response
#     print("-" * 100)
#     print(response)
#     print("-" * 100)
#     print("\n")

#   except (EOFError, KeyboardInterrupt):
#     # Handles cell interruption or graceful stop
#     #print(messages)
#     break
#   except Exception as e:
#     # Catch other unexpected errors
#     print(f"An error occurred: {e}")
#     break

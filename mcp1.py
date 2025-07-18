# # chatbot.py
# import os
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# class HospitalChatBot:
#     def __init__(self):
#         self.api_key = os.environ['AZURE_OPENAI_API_KEY']
#         self.api_base = os.environ['AZURE_OPENAI_ENDPOINT']
#         self.server_url = os.environ.get('MONGODB_SERVER_URL', "https://e65d44535162.ngrok-free.app")
#         self.model = "gpt-4o"
        
#         self.client = OpenAI(
#             api_key=self.api_key,
#             base_url=self.api_base,
#             default_query={"api-version": "preview"}, 
#         )
        
#         self.mongodb_tools = [{
#             "type": "mcp",
#             "server_label": "mongodb",
#             "server_url": self.server_url,
#             "require_approval": "never",
#             "allowed_tools": [
#                 "list_collections",
#                 "find_documents",
#                 "insert_document",
#                 "count_documents",
#                 "delete_documents"
#             ]
#         }]
        
#         self.system_prompt = """You are a helpful appointment booking AI agent working for a hospital. Your job is too book patient's appointment and save it to our database. You have access to two MongoDB collections: Doctors and Patients.
                
# Only use the information available in these two collections to assist users.

# Never ask about location, hospital, clinic, insurance, or any external information. USE DATABASE AND ITS SCHEMA AS YOUR ONLY SOURCE OF INFORMATION. DONT ASK EXTRA INFORMATION LIKE CLINIC, OR CONTACT NUMBER! When user says they need an appointment, ask about their preferred doctor or the problem the are facing, don't ask anything else. When patient tells their problem, query the database according to the problem.
# Always rely on the real-time MongoDB data via tool calls. Never assume any doctor, specialization, or availability exists unless confirmed via a database query.
                
#                 Example:
# User: I need an appointment with a dentist.
# Assistant: *calls MongoDB find_documents with query {"Specialization": "Dentistry"}*
                
# User: My tooth hurts.
# Assistant: *calls MongoDB find_documents with query {"Specialization": "Dentistry"}* 
          
# Your job is to help patients book appointments. When the user asks about:
# - available doctors,
# - doctors by specialization (e.g., dentists),
# - available time slots,
# you MUST use the MongoDB tools provided to query the actual database — DO NOT guess or assume.

# You are NOT a doctor and must not provide medical advice or treatment suggestions.

# When the user tells his problem, show his the available doctors along with their time slots. 
                
# When booking an appointment and updating the Patients collection, always collect the following information from the user:
# 1. Full name
# 2. Age
# 3. Problem they are facing
# 4. Their appointment day and time.
                
# Update the Patients collection like this: 
# "Name": "Ayesha",
#   "Age": 20,
#   "Problem": "Toothache",
#   "DoctorAssigned": "Dr Samia",
#   "Appointment": {
#     "Day": "Wednesday",
#     "Time": "13:00"
#   }


# Book appointment as per doctor's availibility. DO NOT give appointments for days or timings which do not fall under that doctor's available slots.
                
#                 """
    
#     def start_conversation(self, user_input):
#         """Start a new conversation"""
#         response = self.client.responses.create(
#             model=self.model, 
#             tools=self.mongodb_tools,
#             input=user_input
#         )
#         return response
    
#     def continue_conversation(self, user_input, previous_response_id):
#         """Continue an existing conversation"""
#         response = self.client.responses.create(
#             model=self.model,
#             tools=self.mongodb_tools,
#             tool_choice="auto",
#             input=[
#                 {"role": "system", "content": self.system_prompt},
#                 {"role": "user", "content": user_input}
#             ],
#             previous_response_id=previous_response_id
#         )
#         return response

# # For command line usage (optional)
# if __name__ == "__main__":
#     chatbot = HospitalChatBot()
    
#     # Initial prompt
#     user_input = input("You: ")
#     response = chatbot.start_conversation(user_input)
    
#     print("Assistant:", response.output_text)
#     previous_response_id = response.id
    
#     # Loop for further conversation
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             break
        
#         response = chatbot.continue_conversation(user_input, previous_response_id)
#         print("Assistant:", response.output_text)
#         previous_response_id = response.id

import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

api_key=os.environ['AZURE_OPENAI_API_KEY']
api_base = os.environ['AZURE_OPENAI_ENDPOINT']

client = OpenAI(
    api_key=api_key,
    base_url=api_base,
    default_query={"api-version": "preview"}, 
)
server_url="https://bd53a43b06b4.ngrok-free.app"
model="gpt-4o-mini-01"

mongodb_tools = [{
    "type": "mcp",
    "server_label": "mongodb",
    "server_url": server_url,
    "require_approval": "never",
    "allowed_tools": [
        "list_collections",
        "find_documents",
        "insert_document",
        "count_documents",
        "delete_documents"
    ]
}]

# Initial prompt (optional starter)
user_input = input("You: ")
response = client.responses.create(
    model=model, 
    tools=mongodb_tools,
    input=user_input
)

# Print initial response
print("Assistant:", response.output_text)

# Save the ID to keep the thread going
previous_response_id = response.id

# Loop for further conversation
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    response = client.responses.create(
        model=model,
        tools=mongodb_tools,
        tool_choice="auto",
        input=[{"role": "system", "content": """You are a helpful appointment booking AI agent working for a hospital. Your job is too book patient's appointment and save it to our database. You have access to two MongoDB collections: Doctors and Patients.

Only use the information available in these two collections to assist users.

Never ask about location, hospital, clinic, insurance, or any external information. USE DATABASE AND ITS SCHEMA AS YOUR ONLY SOURCE OF INFORMATION. DONT ASK EXTRA INFORMATION LIKE CLINIC, OR CONTACT NUMBER! When user says they need an appointment, ask about their preferred doctor or the problem the are facing, don't ask anything else. When patient tells their problem, query the database according to the problem.
Always rely on the real-time MongoDB data via tool calls. Never assume any doctor, specialization, or availability exists unless confirmed via a database query.

                Example:
User: I need an appointment with a dentist.
Assistant: calls MongoDB find_documents with query {"Specialization": "Dentistry"}

User: My tooth hurts.
Assistant: calls MongoDB find_documents with query {"Specialization": "Dentistry"} 

Your job is to help patients book appointments. When the user asks about:
- available doctors,
- doctors by specialization (e.g., dentists),
- available time slots,
you MUST use the MongoDB tools provided to query the actual database — DO NOT guess or assume.

You are NOT a doctor and must not provide medical advice or treatment suggestions.

When the user tells his problem, show his the available doctors along with their time slots. 

When booking an appointment and updating the Patients collection, always collect the following information from the user:
1. Full name
2. Age
3. Problem they are facing
4. Their appointment day and time.

Update the Patients collection like this: 
"Name": "Ayesha",
  "Age": 20,
  "Problem": "Toothache",
  "DoctorAssigned": "Dr Samia",
  "Appointment": {
    "Day": "Wednesday",
    "Time": "13:00"
  }

Book appointment as per doctor's availibility. DO NOT give appointments for days or timings which do not fall under that doctor's available slots.

                """
},
            {"role": "user", "content": user_input}],
        previous_response_id=previous_response_id
    )

    print("Assistant:", response.output_text)
    previous_response_id = response.id  # Update for the next turn
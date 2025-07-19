
# from fastapi import FastAPI, Request, HTTPException
# from typing import Dict, Any, Optional, List
# from mongodb_client import MongoDBClient  # Your class from earlier
# import asyncio
# import os
# from dotenv import load_dotenv
# import json
# from datetime import datetime

# load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://saverarizwan11906:savera999@testingmcp.waghnod.mongodb.net/")
# #DB_NAME = os.getenv("DB_NAME", "mcpdatabase")
# DB_NAME = os.getenv("DB_NAME", "MedicalRecords")

# mongo_client = MongoDBClient(connection_string=MONGO_URI, database_name=DB_NAME)

# app = FastAPI()

# # Add request logging
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     start_time = datetime.now()
    
#     # Log the request
#     body = await request.body()
#     print(f"\n{'='*50}")
#     print(f"🔥 INCOMING REQUEST at {start_time}")
#     print(f"Method: {request.method}")
#     print(f"URL: {request.url}")
#     print(f"Headers: {dict(request.headers)}")
#     if body:
#         try:
#             json_body = json.loads(body.decode())
#             print(f"Body: {json.dumps(json_body, indent=2)}")
#         except:
#             print(f"Body (raw): {body}")
    
#     # Create new request with the body
#     from fastapi import Request
#     from starlette.datastructures import Headers
    
#     async def receive():
#         return {"type": "http.request", "body": body}
    
#     request = Request(scope=request.scope, receive=receive)
    
#     response = await call_next(request)
    
#     duration = (datetime.now() - start_time).total_seconds()
#     print(f"✅ Response completed in {duration:.3f}s")
#     print(f"{'='*50}\n")
    
#     return response

# @app.on_event("startup")
# async def startup():
#     print("🚀 Starting MCP MongoDB Server...")
#     await mongo_client.connect()
#     print("✅ MCP MongoDB Server started successfully!")

# @app.on_event("shutdown")
# async def shutdown():
#     print("🛑 Shutting down MCP MongoDB Server...")
#     if mongo_client.client:
#         mongo_client.client.close()
#     print("✅ MCP MongoDB Server shutdown complete!")

# @app.post("/")
# async def handle_rpc(request: Request):
#     try:
#         body = await request.json()
#         print(f"\n🧩 MCP REQUEST RECEIVED:")
#         print(f"📝 Raw body: {json.dumps(body, indent=2)}")
        
#         method = body.get("method")
#         request_id = body.get("id")
#         params = body.get("params", {})
        
#         print(f"🎯 Method: {method}")
#         print(f"🆔 Request ID: {request_id}")
#         print(f"📋 Params: {json.dumps(params, indent=2)}")
        
#         # Base response structure
#         def make_response(result: Any):
#             response = {"jsonrpc": "2.0", "id": request_id, "result": result}
#             print(f"📤 SENDING RESPONSE: {json.dumps(response, indent=2)}")
#             return response
        
#         def make_error(message: str, code: int = -32000):
#             error_response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
#             print(f"❌ SENDING ERROR: {json.dumps(error_response, indent=2)}")
#             return error_response
        
#         if method == "initialize":
#             print("🔧 Handling initialize request")
#             result = {
#                 "protocolVersion": "2025-03-26",
#                 "capabilities": {
#                     "tools": {}
#                 },
#                 "serverInfo": {
#                     "name": "mongodb-mcp-server",
#                     "version": "1.0.0"
#                 }
#             }
#             return make_response(result)
        
#         elif method == "tools/list":
#             print("🔧 Handling tools/list request")
#             # Return tools in the correct MCP format
#             tools_dict = mongo_client.get_available_tools()
#             tools = []
            
#             for tool_name, tool_info in tools_dict.items():
#                 schema = tool_info["schema"]["function"]
#                 tool_def = {
#                     "name": schema["name"],
#                     "description": schema["description"],
#                     "inputSchema": {
#                         "type": "object",
#                         "properties": schema["parameters"]["properties"],
#                         "required": schema["parameters"]["required"]
#                     }
#                 }
#                 tools.append(tool_def)
#                 print(f"📋 Added tool: {tool_name}")
            
#             print(f"🛠️  Total tools available: {len(tools)}")
#             return make_response({"tools": tools})
        
#         elif method == "tools/call":
#             print("🔧 Handling tools/call request")
#             # Handle tool calls
#             tool_name = params.get("name")
#             arguments = params.get("arguments", {})
            
#             print(f"🎯 Tool to call: {tool_name}")
#             print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
            
#             tools_dict = mongo_client.get_available_tools()
#             if tool_name not in tools_dict:
#                 print(f"❌ Tool '{tool_name}' not found")
#                 print(f"📋 Available tools: {list(tools_dict.keys())}")
#                 return make_error(f"Tool '{tool_name}' not found", code=-32601)
            
#             try:
#                 print(f"🔄 Executing tool: {tool_name}")
#                 func = tools_dict[tool_name]["callable"]
#                 result = await func(**arguments)
#                 print(f"✅ Tool execution result: {result}")
                
#                 # Return the result in MCP format
#                 response_result = {
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": result
#                         }
#                     ]
#                 }
#                 return make_response(response_result)
#             except Exception as e:
#                 print(f"❌ Tool execution failed: {str(e)}")
#                 import traceback
#                 traceback.print_exc()
#                 return make_error(f"Tool execution failed: {str(e)}", code=-32001)
        
#         else:
#             print(f"❌ Unknown method: {method}")
#             return make_error(f"Unknown method: {method}", code=-32601)
    
#     except Exception as e:
#         print(f"❌ Error processing request: {e}")
#         import traceback
#         traceback.print_exc()
#         return {
#             "jsonrpc": "2.0",
#             "id": body.get("id") if 'body' in locals() else None,
#             "error": {
#                 "code": -32000,
#                 "message": f"Internal server error: {str(e)}"
#             }
#         }

# # Add CORS middleware
# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# if __name__ == "__main__":
#     import uvicorn
#     print("🚀 Starting MCP MongoDB Server on port 5000...")
#     uvicorn.run(app, host="0.0.0.0", port=5000)


from fastapi import FastAPI, Request, HTTPException
from typing import Dict, Any, Optional, List
from mongodb_client import MongoDBClient  # Your class from earlier
import asyncio
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
#DB_NAME = os.getenv("DB_NAME", "mcpdatabase")
DB_NAME = os.getenv("MONGODB_DATABASE")

mongo_client = MongoDBClient(connection_string=MONGO_URI, database_name=DB_NAME)

app = FastAPI()

# Add request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # Log the request
    body = await request.body()
    print(f"\n{'='*50}")
    print(f"🔥 INCOMING REQUEST at {start_time}")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {dict(request.headers)}")
    if body:
        try:
            json_body = json.loads(body.decode())
            print(f"Body: {json.dumps(json_body, indent=2)}")
        except:
            print(f"Body (raw): {body}")
    
    # Create new request with the body
    from fastapi import Request
    from starlette.datastructures import Headers
    
    async def receive():
        return {"type": "http.request", "body": body}
    
    request = Request(scope=request.scope, receive=receive)
    
    response = await call_next(request)
    
    duration = (datetime.now() - start_time).total_seconds()
    print(f"✅ Response completed in {duration:.3f}s")
    print(f"{'='*50}\n")
    
    return response

@app.on_event("startup")
async def startup():
    print("🚀 Starting MCP MongoDB Server...")
    await mongo_client.connect()
    print("✅ MCP MongoDB Server started successfully!")

@app.on_event("shutdown")
async def shutdown():
    print("🛑 Shutting down MCP MongoDB Server...")
    if mongo_client.client:
        mongo_client.client.close()
    print("✅ MCP MongoDB Server shutdown complete!")

@app.post("/")
async def handle_rpc(request: Request):
    try:
        body = await request.json()
        print(f"\n🧩 MCP REQUEST RECEIVED:")
        print(f"📝 Raw body: {json.dumps(body, indent=2)}")
        
        method = body.get("method")
        request_id = body.get("id")
        params = body.get("params", {})
        
        print(f"🎯 Method: {method}")
        print(f"🆔 Request ID: {request_id}")
        print(f"📋 Params: {json.dumps(params, indent=2)}")
        
        # Base response structure
        def make_response(result: Any):
            response = {"jsonrpc": "2.0", "id": request_id, "result": result}
            print(f"📤 SENDING RESPONSE: {json.dumps(response, indent=2)}")
            return response
        
        def make_error(message: str, code: int = -32000):
            error_response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
            print(f"❌ SENDING ERROR: {json.dumps(error_response, indent=2)}")
            return error_response
        
        if method == "initialize":
            print("🔧 Handling initialize request")
            result = {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mongodb-mcp-server",
                    "version": "1.0.0"
                }
            }
            return make_response(result)
        
        elif method == "tools/list":
            print("🔧 Handling tools/list request")
            # Return tools in the correct MCP format
            tools_dict = mongo_client.get_available_tools()
            tools = []
            
            for tool_name, tool_info in tools_dict.items():
                schema = tool_info["schema"]["function"]
                tool_def = {
                    "name": schema["name"],
                    "description": schema["description"],
                    "inputSchema": {
                        "type": "object",
                        "properties": schema["parameters"]["properties"],
                        "required": schema["parameters"]["required"]
                    }
                }
                tools.append(tool_def)
                print(f"📋 Added tool: {tool_name}")
            
            print(f"🛠️  Total tools available: {len(tools)}")
            return make_response({"tools": tools})
        
        elif method == "tools/call":
            print("🔧 Handling tools/call request")
            # Handle tool calls
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            print(f"🎯 Tool to call: {tool_name}")
            print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
            
            tools_dict = mongo_client.get_available_tools()
            if tool_name not in tools_dict:
                print(f"❌ Tool '{tool_name}' not found")
                print(f"📋 Available tools: {list(tools_dict.keys())}")
                return make_error(f"Tool '{tool_name}' not found", code=-32601)
            
            try:
                print(f"🔄 Executing tool: {tool_name}")
                func = tools_dict[tool_name]["callable"]
                result = await func(**arguments)
                print(f"✅ Tool execution result: {result}")
                
                # Return the result in MCP format
                response_result = {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
                return make_response(response_result)
            except Exception as e:
                print(f"❌ Tool execution failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return make_error(f"Tool execution failed: {str(e)}", code=-32001)
        
        else:
            print(f"❌ Unknown method: {method}")
            return make_error(f"Unknown method: {method}", code=-32601)
    
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32000,
                "message": f"Internal server error: {str(e)}"
            }
        }

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MCP MongoDB Server on port 5000...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
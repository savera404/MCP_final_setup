import json
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
import bson
from datetime import datetime

class MongoDBClient:
    """
    A client class for interacting with MongoDB database.
    This class manages the connection and provides database operation tools.
    """

    def __init__(self, connection_string: str, database_name: str):
        """Initialize the MongoDB client with connection parameters"""
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            self.client.close()

    async def connect(self):
        """Establishes connection to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test the connection
            await self.client.admin.command('ping')
            print(f"Successfully connected to MongoDB database: {self.database_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MongoDB: {e}")

    async def list_collections(self) -> str:
        """List all collections in the database"""
        try:
            collections = await self.db.list_collection_names()
            return json.dumps({"collections": collections})
        except PyMongoError as e:
            return json.dumps({"error": f"Failed to list collections: {e}"})

    async def find_documents(self, collection_name: str, query: str = "{}", limit: int = 10) -> str:
        """
        Find documents in a collection based on a query.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query as JSON string (default: "{}")
            limit: Maximum number of documents to return (default: 10)
        """
        try:
            collection = self.db[collection_name]
            query_dict = json.loads(query) if query else {}
            
            # Handle ObjectId in queries
            if '_id' in query_dict and isinstance(query_dict['_id'], str):
                try:
                    query_dict['_id'] = bson.ObjectId(query_dict['_id'])
                except bson.errors.InvalidId:
                    return json.dumps({"error": "Invalid ObjectId format"})
            
            cursor = collection.find(query_dict).limit(limit)
            documents = []
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                # Convert datetime objects to ISO format
                for key, value in doc.items():
                    if isinstance(value, datetime):
                        doc[key] = value.isoformat()
                documents.append(doc)
            
            return json.dumps({"documents": documents, "count": len(documents)})
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON query format"})
        except PyMongoError as e:
            return json.dumps({"error": f"Database error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})

    async def insert_document(self, collection_name: str, document: str) -> str:
        """
        Insert a document into a collection.
        
        Args:
            collection_name: Name of the collection
            document: Document to insert as JSON string
        """
        try:
            collection = self.db[collection_name]
            doc_dict = json.loads(document)
            
            # Handle datetime fields
            for key, value in doc_dict.items():
                if isinstance(value, str) and value.endswith('Z'):
                    try:
                        doc_dict[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        pass  # Keep as string if not a valid datetime
            
            result = await collection.insert_one(doc_dict)
            return json.dumps({
                "success": True,
                "inserted_id": str(result.inserted_id),
                "message": "Document inserted successfully"
            })
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON document format"})
        except PyMongoError as e:
            return json.dumps({"error": f"Database error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})

    async def update_documents(self, collection_name: str, query: str, update: str) -> str:
        """
        Update documents in a collection.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query to match documents as JSON string
            update: Update operations as JSON string (use MongoDB update operators)
        """
        try:
            collection = self.db[collection_name]
            query_dict = json.loads(query)
            update_dict = json.loads(update)
            
            # Handle ObjectId in queries
            if '_id' in query_dict and isinstance(query_dict['_id'], str):
                try:
                    query_dict['_id'] = bson.ObjectId(query_dict['_id'])
                except bson.errors.InvalidId:
                    return json.dumps({"error": "Invalid ObjectId format"})
            
            result = await collection.update_many(query_dict, update_dict)
            return json.dumps({
                "success": True,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "message": f"Updated {result.modified_count} documents"
            })
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON format in query or update"})
        except PyMongoError as e:
            return json.dumps({"error": f"Database error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})

    async def delete_documents(self, collection_name: str, query: str) -> str:
        """
        Delete documents from a collection.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query to match documents to delete as JSON string
        """
        try:
            collection = self.db[collection_name]
            query_dict = json.loads(query)
            
            # Handle ObjectId in queries
            if '_id' in query_dict and isinstance(query_dict['_id'], str):
                try:
                    query_dict['_id'] = bson.ObjectId(query_dict['_id'])
                except bson.errors.InvalidId:
                    return json.dumps({"error": "Invalid ObjectId format"})
            
            result = await collection.delete_many(query_dict)
            return json.dumps({
                "success": True,
                "deleted_count": result.deleted_count,
                "message": f"Deleted {result.deleted_count} documents"
            })
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON query format"})
        except PyMongoError as e:
            return json.dumps({"error": f"Database error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})

    async def count_documents(self, collection_name: str, query: str = "{}") -> str:
        """
        Count documents in a collection based on a query.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query as JSON string (default: "{}")
        """
        try:
            collection = self.db[collection_name]
            query_dict = json.loads(query) if query else {}
            
            # Handle ObjectId in queries
            if '_id' in query_dict and isinstance(query_dict['_id'], str):
                try:
                    query_dict['_id'] = bson.ObjectId(query_dict['_id'])
                except bson.errors.InvalidId:
                    return json.dumps({"error": "Invalid ObjectId format"})
            
            count = await collection.count_documents(query_dict)
            return json.dumps({"count": count})
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON query format"})
        except PyMongoError as e:
            return json.dumps({"error": f"Database error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})

    async def aggregate(self, collection_name: str, pipeline: str) -> str:
        """
        Perform aggregation operations on a collection.
        
        Args:
            collection_name: Name of the collection
            pipeline: Aggregation pipeline as JSON string
        """
        try:
            collection = self.db[collection_name]
            pipeline_list = json.loads(pipeline)
            
            if not isinstance(pipeline_list, list):
                return json.dumps({"error": "Pipeline must be a list of aggregation stages"})
            
            cursor = collection.aggregate(pipeline_list)
            results = []
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                # Convert datetime objects to ISO format
                for key, value in doc.items():
                    if isinstance(value, datetime):
                        doc[key] = value.isoformat()
                results.append(doc)
            
            return json.dumps({"results": results, "count": len(results)})
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON pipeline format"})
        except PyMongoError as e:
            return json.dumps({"error": f"Database error: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})

    def get_available_tools(self) -> Dict[str, Any]:
        """Return available MongoDB operations as tool definitions"""
        return {
            "list_collections": {
                "name": "list_collections",
                "callable": self.list_collections,
                "schema": {
                    "type": "function",
                    "function": {
                        "name": "list_collections",
                        "description": "List all collections in the MongoDB database",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {},
                            "required": []
                        }
                    }
                }
            },
            "find_documents": {
    "name": "find_documents",
    "callable": self.find_documents,
    "schema": {
        "type": "function",
        "function": {
            "name": "find_documents",
            "description": "Find documents in a MongoDB collection based on a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection to search in"
                    },
                    "query": {
                        "type": "string",
                        "description": "MongoDB query as a JSON string"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of documents to return"
                    }
                },
                "required": ["collection_name"]
            }
        }
    }
},

            "insert_document": {
                "name": "insert_document",
                "callable": self.insert_document,
                "schema": {
                    "type": "function",
                    "function": {
                        "name": "insert_document",
                        "description": "Insert a document into a MongoDB collection",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "collection_name": {
                                    "type": "string",
                                    "description": "Name of the collection to insert into"
                                },
                                "document": {
                                    "type": "string",
                                    "description": "Document to insert as JSON string"
                                }
                            },
                            "required": ["collection_name", "document"]
                        }
                    }
                }
            },
            "update_documents": {
    "name": "update_documents",
    "callable": self.update_documents,
    "schema": {
        "type": "function",
        "function": {
            "name": "update_documents",
            "description": "Update documents in a MongoDB collection",
            "parameters": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection to update"
                    },
                    "query": {
                        "type": "string",
                        "description": "MongoDB query to match documents as a JSON string"
                    },
                    "update": {
                        "type": "string",
                        "description": "Update operations as a JSON string (use MongoDB update operators like $set, $inc, etc.)"
                    }
                },
                "required": ["collection_name", "query", "update"]
            }
        }
    }
},

            "delete_documents": {
    "name": "delete_documents",
    "callable": self.delete_documents,
    "schema": {
        "type": "function",
        "function": {
            "name": "delete_documents",
            "description": "Delete documents from a MongoDB collection",
            "parameters": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection to delete from"
                    },
                    "query": {
                        "type": "string",
                        "description": "MongoDB query to match documents to delete as a JSON string"
                    }
                },
                "required": ["collection_name", "query"]
            }
        }
    }
},

            "count_documents": {
    "name": "count_documents",
    "callable": self.count_documents,
    "schema": {
        "type": "function",
        "function": {
            "name": "count_documents",
            "description": "Count documents in a MongoDB collection based on a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection to count documents in"
                    },
                    "query": {
                        "type": "string",
                        "description": "MongoDB query as a JSON string"
                    }
                },
                "required": ["collection_name"]
            }
        }
    }
},

            "aggregate": {
                "name": "aggregate",
                "callable": self.aggregate,
                "schema": {
                    "type": "function",
                    "function": {
                        "name": "aggregate",
                        "description": "Perform aggregation operations on a MongoDB collection",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "collection_name": {
                                    "type": "STRING",
                                    "description": "Name of the collection to perform aggregation on"
                                },
                                "pipeline": {
                                    "type": "STRING",
                                    "description": "Aggregation pipeline as JSON string (list of aggregation stages)"
                                }
                            },
                            "required": ["collection_name", "pipeline"]
                        }
                    }
                }
            }
        }




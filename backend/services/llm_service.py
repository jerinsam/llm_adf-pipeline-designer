from unittest import result
import requests
import json
from config.config import Config 
import re 

class LLMService:
    def __init__(self):
        self.use_perplexity = Config.USE_PERPLEXITY
        self.perplexity_url = Config.PERPLEXITY_URL
        self.api_key = Config.PERPLEXITY_API_KEY
        self.model = Config.PERPLEXITY_MODEL

        # self.use_ollama = Config.USE_OLLAMA
        # self.ollama_url = Config.OLLAMA_URL
        # self.model = Config.OLLAMA_MODEL

        if not self.api_key:
            raise Exception("PERPLEXITY_API_KEY environment variable not set")
        
        self.system_prompt = """You are an Azure Data Factory pipeline expert. Your task is to:
1. Interpret user requests for data pipelines
2. Generate valid JSON configurations for:
   - Linked Services with proper naming (ls_source_target)
   - Datasets with proper naming (ds_source_target)  
   - Pipelines with proper naming (pl_source_target)
   - Activities like Copy, Lookup, etc.
3. Create visual pipeline flow with nodes and connections
4. Follow Azure best practices and naming conventions
5. Use proper ADF component names and structure

ADF Naming Conventions:
- Linked Services: ls_[source]_[target] (e.g., ls_sql_mysql)
- Datasets: ds_[source]_[target] (e.g., ds_sql_mysql)
- Pipelines: pl_[source]_to_[target] (e.g., pl_sql_to_mysql)
- Activities: CopyData, LookupConfig, etc.

Response format:
{
  "pipeline_flow": {
    "nodes": [
      {
        "id": "ls_sql_server",
        "type": "linked_service",
        "name": "ls_sql_server",
        "label": "SQL Server Linked Service"
      },
      {
        "id": "ds_sql_server",
        "type": "dataset", 
        "name": "ds_sql_server",
        "label": "SQL Server Dataset"
      },
      {
        "id": "copy_activity",
        "type": "activity",
        "name": "CopyData",
        "label": "Copy Data Activity"
      }
    ],
    "edges": [
      {
        "id": "edge_1",
        "source": "ls_sql_server",
        "target": "ds_sql_server",
        "label": "provides connection"
      }
    ]
  },
  "json_configs": {
    "linked_services": [
      {
        "name": "ls_sql_server",
        "type": "Microsoft.DataFactory/factories/linkedservices",
        "properties": {
          "type": "SqlServer",
          "typeProperties": {
            "connectionString": "connection string here"
          }
        }
      }
    ],
    "datasets": [
      {
        "name": "ds_sql_server", 
        "type": "Microsoft.DataFactory/factories/datasets",
        "properties": {
          "type": "SqlServerTable",
          "linkedServiceName": {
            "referenceName": "ls_sql_server",
            "type": "LinkedServiceReference"
          },
          "typeProperties": {
            "tableName": "table_name"
          }
        }
      }
    ],
    "pipeline": {
      "name": "pl_sql_to_databricks",
      "type": "Microsoft.DataFactory/factories/pipelines",
      "properties": {
        "activities": [
          {
            "name": "CopyData",
            "type": "Copy",
            "inputs": [
              {
                "referenceName": "ds_sql_server",
                "type": "DatasetReference"
              }
            ],
            "outputs": [
              {
                "referenceName": "ds_databricks",
                "type": "DatasetReference"
              }
            ],
            "typeProperties": {
              "source": {
                "type": "SqlSource"
              },
              "sink": {
                "type": "AzureDatabricksDeltaSink"
              }
            }
          }
        ]
      }
    }
  },
  "explanation": "Pipeline to copy data from SQL Server to Databricks with proper ADF components"
}

Always respond with valid JSON in the exact format above. Never include markdown code blocks. Just return the JSON object."""

    def generate_pipeline_config(self, conversation_history):
        try:
            # Prepare conversation history
            recent_messages = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            messages = self._format_conversation(recent_messages)
            with open('prompt.txt', 'w') as log_file:
                log_file.write(f"{messages}\n")
            return self._call_perplexity_api(messages)
                
        except Exception as e:
            raise Exception(f"Error generating pipeline config: {str(e)}")
    
    def _format_conversation(self, messages):
        # Format conversation for Perplexity API
        formatted_messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Convert messages to Perplexity format
        for msg in messages:
            if msg['role'] == 'user':
                formatted_messages.append({"role": "user", "content": msg['content']})
            elif msg['role'] == 'assistant':
                formatted_messages.append({"role": "assistant", "content": msg['content']})
        
        return formatted_messages
    
    def _call_perplexity_api(self, messages):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages
            }
            
            print(f"Sending request to Perplexity: {self.perplexity_url}")
            print(f"Model: {self.model}")
            print(f"Messages count: {len(messages)}")
            
            response = requests.post(
                self.perplexity_url, 
                headers=headers, 
                json=payload, 
                timeout=12000
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"Raw response received")
                    
                    # Extract content from Perplexity response
                    response_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    if not response_content:
                        raise Exception("Empty response from Perplexity")
                    
                    print(f"Response content: {response_content[:200]}...")
                    
                    # Try to parse the JSON response
                    try:
                        # Look for JSON object in the response
                        start = response_content.find('{')
                        end = response_content.rfind('}') + 1
                        if start != -1 and end > start:
                            json_str = response_content[start:end]
                            parsed_json = json.loads(json_str)
                            print("Successfully parsed JSON response")
                            return self._validate_and_clean_response(parsed_json)
                        else:
                            raise Exception("No valid JSON structure found in response")
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                        # Try to clean and parse
                        cleaned_response = self._clean_json_response(response_content)
                        if cleaned_response:
                            return self._validate_and_clean_response(cleaned_response)
                        else:
                            raise Exception(f"Failed to parse JSON response: {response_content[:200]}")
                            
                except json.JSONDecodeError as e:
                    raise Exception(f"Invalid JSON response from Perplexity: {e}")
                except (KeyError, IndexError) as e:
                    raise Exception(f"Unexpected response format from Perplexity: {e}")
            else:
                error_text = response.text
                raise Exception(f"Perplexity API error {response.status_code}: {error_text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Perplexity API. Check your internet connection.")
        except requests.exceptions.Timeout:
            raise Exception("Perplexity request timed out. Try simplifying your request.")
        except Exception as e:
            raise Exception(f"Perplexity API error: {str(e)}")
    
    def _clean_json_response(self, response_text):
        """Attempt to clean and parse JSON response"""
        try:
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            
            # Strip whitespace
            response_text = response_text.strip()
            
            # Try to find and extract JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        return None
    
    def _validate_and_clean_response(self, response_data):
        """Validate and clean the response data"""
        # Ensure required structure exists
        if 'pipeline_flow' not in response_data:
            response_data['pipeline_flow'] = {'nodes': [], 'edges': []}
        
        if 'json_configs' not in response_data:
            response_data['json_configs'] = {'linked_services': [], 'datasets': [], 'pipeline': {}}
        
        # Ensure pipeline_flow has nodes and edges
        if 'nodes' not in response_data['pipeline_flow']:
            response_data['pipeline_flow']['nodes'] = []
        if 'edges' not in response_data['pipeline_flow']:
            response_data['pipeline_flow']['edges'] = []
            
        # Ensure json_configs has required keys
        required_keys = ['linked_services', 'datasets', 'pipeline']
        for key in required_keys:
            if key not in response_data['json_configs']:
                response_data['json_configs'][key] = [] if key != 'pipeline' else {}
        
        return response_data
import json
from jsonschema import validate, ValidationError

class JSONValidator:
    @staticmethod
    def validate_linked_service(linked_service_json):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "properties": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "typeProperties": {"type": "object"}
                    },
                    "required": ["type", "typeProperties"]
                }
            },
            "required": ["name", "type", "properties"]
        }
        
        try:
            validate(instance=linked_service_json, schema=schema)
            return True, None
        except ValidationError as e:
            return False, str(e)
    
    @staticmethod
    def validate_dataset(dataset_json):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "properties": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "linkedServiceName": {"type": "object"},
                        "typeProperties": {"type": "object"}
                    },
                    "required": ["type", "linkedServiceName", "typeProperties"]
                }
            },
            "required": ["name", "type", "properties"]
        }
        
        try:
            validate(instance=dataset_json, schema=schema)
            return True, None
        except ValidationError as e:
            return False, str(e)
    
    @staticmethod
    def validate_pipeline(pipeline_json):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "properties": {
                    "type": "object",
                    "properties": {
                        "activities": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    },
                    "required": ["activities"]
                }
            },
            "required": ["name", "type", "properties"]
        }
        
        try:
            validate(instance=pipeline_json, schema=schema)
            return True, None
        except ValidationError as e:
            return False, str(e)
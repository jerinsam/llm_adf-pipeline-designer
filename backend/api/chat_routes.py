from flask import Blueprint, request, jsonify
from services.llm_service import LLMService
import traceback

chat_bp = Blueprint('chat', __name__)
llm_service = LLMService()

# Simple in-memory storage for current conversation
current_conversation = []

@chat_bp.route('/chat', methods=['POST'])
def chat():
    global current_conversation
    
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json', 'success': False}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided', 'success': False}), 400
            
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'error': 'Missing message', 'success': False}), 400
        
        # Add user message to conversation
        current_conversation.append({
            'role': 'user',
            'content': user_message
        })
        
        # Generate response using LLM
        result = llm_service.generate_pipeline_config(current_conversation)

        with open('conversation_log.txt', 'w') as log_file:
            log_file.write(f"{result}\n") 

        # Add assistant response to conversation
        explanation = result.get('explanation', 'Pipeline configuration generated')
        current_conversation.append({
            'role': 'assistant',
            'content': explanation
        })
        
        return jsonify({
            'response': result,
            'success': True
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': f'Error: {str(e)}',
            'success': False
        }), 500

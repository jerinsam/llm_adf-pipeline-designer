class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

class ValidationError(APIError):
    """Exception for validation errors"""
    def __init__(self, message):
        super().__init__(message, status_code=400)

class ResourceNotFoundError(APIError):
    """Exception for resource not found errors"""
    def __init__(self, resource_type, resource_id):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, status_code=404)

class AzureError(APIError):
    """Exception for Azure service errors"""
    def __init__(self, message, azure_error=None):
        super().__init__(message, status_code=500)
        self.azure_error = azure_error

class AuthenticationError(APIError):
    """Exception for authentication errors"""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401)

def handle_error(error):
    """Convert exceptions to JSON responses"""
    if isinstance(error, APIError):
        response = {
            'success': False,
            'error': error.message,
            'error_type': error.__class__.__name__
        }
        if hasattr(error, 'azure_error'):
            response['azure_error'] = str(error.azure_error)
        return response, error.status_code
    
    # Handle unexpected errors
    return {
        'success': False,
        'error': str(error),
        'error_type': 'UnexpectedError'
    }, 500

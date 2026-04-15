"""
Standardized error responses for REST API.
All errors follow the format: { "status": "error", "message": "...", "code": "..." }
"""

def api_error(message, status_code=400, error_code=None):
    """
    Return standardized error response.
    
    Args:
        message: Human-readable error message
        status_code: HTTP status code (400, 404, 500, etc.)
        error_code: Optional machine-readable error code
    
    Returns:
        Tuple of (dict, http_status_code)
    """
    return {
        'status': 'error',
        'message': message,
        'code': error_code or status_code,
    }, status_code


def api_success(data=None, message='Success'):
    """
    Return standardized success response.
    
    Args:
        data: Response payload
        message: Success message
    
    Returns:
        Dict with status and data
    """
    response = {
        'status': 'success',
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return response

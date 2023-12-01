from flask import jsonify

def response(
    status: bool,
    code: int,
    message: str,
    error: Exception | None = None,
    data: list[dict] | None = None
) -> jsonify:
    return jsonify({
        'status': 'success' if status else 'error',
        'code': code,
        'message': message,
        'error': error,
        'data': data
    }), code
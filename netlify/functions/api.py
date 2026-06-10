import sys
import os
from io import BytesIO

# Add project root to sys.path so we can import src.app and modules
current_dir = os.path.dirname(os.path.abspath(__file__))
# Netlify structures lambda bundles with the build root as task base
sys.path.append(current_dir)

# Add project root (two levels up from netlify/functions/api.py)
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

# Add src folder
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from app import app
except ImportError:
    # Fallback to local lambda folder paths if bundled differently
    sys.path.append(os.getcwd())
    sys.path.append(os.path.join(os.getcwd(), "src"))
    from app import app

def handler(event, context):
    # Convert Lambda/Netlify event to WSGI environment
    headers = event.get("headers", {})
    body = event.get("body", "")
    
    # Handle base64 encoded bodies
    if event.get("isBase64Encoded", False):
        import base64
        body_bytes = base64.b64decode(body)
    else:
        body_bytes = body.encode("utf-8") if isinstance(body, str) else (body or b"")
        
    # Standard WSGI Environment dictionary
    environ = {
        "REQUEST_METHOD": event.get("httpMethod", "GET"),
        "SCRIPT_NAME": "",
        "PATH_INFO": event.get("path", "").replace("/.netlify/functions/api", ""),
        "QUERY_STRING": "",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "80",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "https",
        "wsgi.input": BytesIO(body_bytes),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    
    # Parse query parameters to query string
    qparams = event.get("queryStringParameters")
    if qparams:
        from urllib.parse import urlencode
        environ["QUERY_STRING"] = urlencode(qparams)
        
    for k, v in headers.items():
        environ[f"HTTP_{k.upper().replace('-', '_')}"] = v
        
    if "content-type" in headers:
        environ["CONTENT_TYPE"] = headers["content-type"]
    if "content-length" in headers:
        environ["CONTENT_LENGTH"] = headers["content-length"]
        
    response_status = []
    response_headers = []
    
    def start_response(status, headers, exc_info=None):
        response_status.append(status)
        response_headers.extend(headers)
        return lambda d: None
        
    # Invoke Flask application
    response_body = b"".join(app(environ, start_response))
    
    # Parse status code
    status_code = 200
    if response_status:
        try:
            status_code = int(response_status[0].split()[0])
        except Exception:
            pass
            
    # Format response headers
    resp_headers = {k: v for k, v in response_headers}
    
    # Enable CORS headers for safety
    resp_headers["Access-Control-Allow-Origin"] = "*"
    resp_headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    resp_headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
    
    return {
        "statusCode": status_code,
        "headers": resp_headers,
        "body": response_body.decode("utf-8", errors="ignore"),
        "isBase64Encoded": False
    }

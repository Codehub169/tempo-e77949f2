import requests
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure basic logging if no handlers are configured.
# This is a common practice for libraries/modules.
# The application (app.py) might have its own logging configuration.
if not logging.getLogger(__name__).hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # seconds
DEFAULT_RETRY_TOTAL = 3
DEFAULT_RETRY_CONNECT = 3 # Retries for connection errors specifically
DEFAULT_RETRY_BACKOFF_FACTOR = 1 # seconds (e.g., 1s, 2s, 4s for subsequent retries)

def fetch_data_from_external_service():
    """
    Fetches data from an external service, with robust error handling
    and a retry mechanism for connection issues and transient server errors.
    Uses logging for detailed error information and returns structured
    responses including user-friendly error messages.
    Requires EXTERNAL_SERVICE_URL environment variable to be set.
    """
    service_url = os.environ.get("EXTERNAL_SERVICE_URL")
    
    if not service_url:
        logger.error("CRITICAL: EXTERNAL_SERVICE_URL environment variable is not set. Cannot fetch data from the external service.")
        return {
            "status": "error", 
            "type": "ConfigurationError", 
            "message": "The application is not configured to connect to the external data service. Please set the EXTERNAL_SERVICE_URL environment variable."
        }
    
    logger.info(f"Attempting to fetch data from external service at URL: {service_url}")

    response_obj = None # Initialize to handle it in JSONDecodeError block if request fails before response_obj is assigned.

    session = requests.Session()
    retry_strategy = Retry(
        total=DEFAULT_RETRY_TOTAL,
        backoff_factor=DEFAULT_RETRY_BACKOFF_FACTOR,
        status_forcelist=[500, 502, 503, 504], # Retry on these server errors
        allowed_methods=frozenset(["GET"]), # Only retry for idempotent methods like GET
        connect=DEFAULT_RETRY_CONNECT
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response_obj = session.get(service_url, timeout=DEFAULT_TIMEOUT)
        response_obj.raise_for_status() # Raise an HTTPError for bad responses (4XX or 5XX)
        data = response_obj.json() # Assumes the response is JSON
        logger.info(f"Successfully fetched and decoded JSON data from {service_url}.")
        return {"status": "success", "data": data}
        
    except requests.exceptions.ConnectionError as e:
        log_message = (
            f"Connection Error for {service_url} (configured with up to {DEFAULT_RETRY_CONNECT} connection retries and "
            f"{DEFAULT_RETRY_TOTAL} total retries): Failed to establish a connection. "
            f"The service might be down, unreachable, or blocked by a firewall. Details: {e}"
        )
        logger.error(log_message)
        returned_message = (
            f"Could not connect to the external service at {service_url}. "
            "The service may be down, unreachable, or blocked by a firewall. "
            "Please verify the URL, check your network connectivity (including DNS resolution), "
            "and ensure that any firewalls (local or network) are not blocking outgoing connections to this service."
        )
        return {"status": "error", "type": "ConnectionError", "message": returned_message}
        
    except requests.exceptions.Timeout as e:
        log_message = f"Timeout Error for {service_url} after retries: The request timed out (timeout set to {DEFAULT_TIMEOUT}s). Details: {e}"
        logger.error(log_message)
        returned_message = f"The request to the external service at {service_url} timed out after {DEFAULT_TIMEOUT} seconds."
        return {"status": "error", "type": "Timeout", "message": returned_message}
        
    except requests.exceptions.HTTPError as e:
        response_text_snippet = ""
        status_code_str = "Unknown"
        status_code_val = None

        if e.response is not None:
            status_code_val = e.response.status_code
            status_code_str = str(status_code_val)
            try:
                # Security note: Logging response text might disclose sensitive info if the error response contains it.
                # Truncation helps, but review if service might return sensitive data in errors.
                response_text_snippet = e.response.text[:500] + ('...' if len(e.response.text) > 500 else '')
            except Exception:
                response_text_snippet = "[Could not decode response text or response was not text]"

        log_message = (
            f"HTTP Error {status_code_str} for {service_url}. "
            f"Response snippet: {response_text_snippet}. Full Details: {e}"
        )
        logger.error(log_message)
        returned_message = f"Received an HTTP {status_code_str} error from the external service at {service_url}."
        return {"status": "error", "type": "HTTPError", "code": status_code_val, "message": returned_message}
        
    except requests.exceptions.JSONDecodeError as e:
        response_text_snippet = "[Response object not available or text attribute missing]"
        if response_obj is not None and hasattr(response_obj, 'text') and isinstance(response_obj.text, str):
             # Security note: Logging response text might disclose sensitive info.
            response_text_snippet = response_obj.text[:500] + ('...' if len(response_obj.text) > 500 else '')
        
        log_message = f"JSON Decode Error for {service_url}: Failed to parse JSON response. Response text snippet: '{response_text_snippet}'. Details: {e}"
        logger.error(log_message)
        returned_message = f"Failed to parse JSON response from {service_url}. The response was not valid JSON."
        return {"status": "error", "type": "JSONDecodeError", "message": returned_message}

    except requests.exceptions.RequestException as e:
        # Catch any other error from the requests library
        log_message = f"Generic Request Exception for {service_url}: An error occurred during the request. Details: {e}"
        logger.error(log_message)
        returned_message = f"An error occurred when requesting data from {service_url}."
        return {"status": "error", "type": "RequestException", "message": returned_message}
    
    except Exception as e:
        # Catch any other unexpected error
        # Use logger.exception to include stack trace for unexpected errors
        logger.exception(f"Unexpected {type(e).__name__} when fetching data from {service_url}")
        returned_message = "An unexpected internal error occurred while trying to fetch external data. Please check server logs."
        return {"status": "error", "type": "UnexpectedError", "message": returned_message}

# Example of how this function might be used (if run as a standalone script for testing):
# if __name__ == "__main__":
#     # For testing, you might temporarily set the environment variable here or in your shell
#     # os.environ["EXTERNAL_SERVICE_URL"] = "https://jsonplaceholder.typicode.com/todos/1" # A working example
#     # os.environ["EXTERNAL_SERVICE_URL"] = "http://nonexistent-domain-for-testing-12345.com" # Example of connection error
#     # os.environ["EXTERNAL_SERVICE_URL"] = "https://httpstat.us/503" # Example of server error for retry
#     # os.environ["EXTERNAL_SERVICE_URL"] = "https://httpstat.us/200?sleep=15000" # Example of timeout (if DEFAULT_TIMEOUT is less than 15s)
#     # os.environ["EXTERNAL_SERVICE_URL"] = "https://www.google.com" # Example of JSONDecodeError (Google homepage is HTML)

#     logger.info("Fetching data from external service (example run)...")
#     result = fetch_data_from_external_service()
#     
#     if result["status"] == "success":
#         logger.info(f"Successfully fetched data: {result['data']}")
#     else:
#         logger.error(f"Failed to fetch data. Error Type: {result.get('type', 'Unknown')}, Message: {result['message']}")

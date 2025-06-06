import requests
import os
import logging

# Configure basic logging for the module.
# This basicConfig is primarily effective if the module is run standalone
# or if no other logging configuration has been set up by an importing application.
# In a Flask app (like the provided app.py context), Flask's own logging setup
# would typically be used and might override or precede this configuration.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_data_from_external_service():
    """
    Fetches data from an external service, with robust error handling
    for connection issues and other request-related exceptions.
    Uses logging for detailed error information and returns structured
    responses including user-friendly error messages.
    """
    service_url = os.environ.get("EXTERNAL_SERVICE_URL", "http://34.28.45.117:5031/")
    
    response_obj = None  # Initialize response_obj to ensure it's available in JSONDecodeError block if needed

    try:
        # Set a timeout for the request to prevent indefinite hanging.
        # Timeout is (connect_timeout, read_timeout). Using a single value for both.
        response_obj = requests.get(service_url, timeout=10)
        
        # Raise an HTTPError for bad responses (4xx or 5xx client/server errors).
        response_obj.raise_for_status()
        
        # Attempt to parse JSON.
        data = response_obj.json()
        return {"status": "success", "data": data}
        
    except requests.exceptions.ConnectionError as e:
        log_message = f"Connection Error for {service_url}: The target machine actively refused connection. Details: {e}"
        logger.error(log_message)
        returned_message = f"Could not connect to the external service at {service_url}. Connection refused."
        return {"status": "error", "type": "ConnectionError", "message": returned_message}
        
    except requests.exceptions.Timeout as e:
        log_message = f"Timeout Error for {service_url}: The request timed out after 10 seconds. Details: {e}"
        logger.error(log_message)
        returned_message = f"The request to the external service at {service_url} timed out."
        return {"status": "error", "type": "Timeout", "message": returned_message}
        
    except requests.exceptions.HTTPError as e:
        response_text_snippet = ""
        if e.response is not None:
            response_text_snippet = e.response.text[:500] + ('...' if len(e.response.text) > 500 else '')
        log_message = (
            f"HTTP Error {e.response.status_code if e.response is not None else 'Unknown'} for {service_url}. "
            f"Response: {response_text_snippet}. Full Details: {e}"
        )
        logger.error(log_message)
        status_code = e.response.status_code if e.response is not None else 'N/A'
        returned_message = f"Received an HTTP {status_code} error from the external service at {service_url}."
        return {"status": "error", "type": "HTTPError", "code": status_code, "message": returned_message}
        
    except requests.exceptions.JSONDecodeError as e:
        response_text_snippet = ""
        if response_obj is not None and hasattr(response_obj, 'text'):
            response_text_snippet = response_obj.text[:500] + ('...' if len(response_obj.text) > 500 else '')
        
        log_message = f"JSON Decode Error for {service_url}: Failed to parse JSON response. Response text snippet: '{response_text_snippet}'. Details: {e}"
        logger.error(log_message)
        returned_message = f"Failed to parse JSON response from the external service at {service_url}. The response was not valid JSON."
        return {"status": "error", "type": "JSONDecodeError", "message": returned_message}

    except requests.exceptions.RequestException as e:
        log_message = f"Request Exception for {service_url}: An unexpected error occurred. Details: {e}"
        logger.error(log_message)
        returned_message = f"An unexpected error occurred when requesting data from the external service at {service_url}."
        return {"status": "error", "type": "RequestException", "message": returned_message}
    
    except Exception as e:
        log_message = f"Unexpected error of type {type(e).__name__} when fetching data from {service_url}."
        logger.exception(log_message) # logger.exception automatically includes exception info and stack trace
        returned_message = f"An unexpected error occurred. Please check logs for details."
        return {"status": "error", "type": "UnexpectedError", "message": returned_message}

# Example of how this function might be used (if run as a standalone script):
# if __name__ == "__main__":
#     # The basicConfig at the top of the file ensures logs are printed to console by default.
#     logger.info("Fetching data from external service (example run)...")
#     result = fetch_data_from_external_service()
#     
#     if result["status"] == "success":
#         logger.info(f"Successfully fetched data: {result['data']}")
#     else:
#         logger.error(f"Failed to fetch data. Error Type: {result.get('type', 'Unknown')}, Message: {result['message']}")
#         # The application can then decide how to proceed: retry, use defaults, exit gracefully, etc.

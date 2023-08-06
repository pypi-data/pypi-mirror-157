# environment variable names
BASE_URL = "CASTOR_QLIK_BASE_URL"
API_KEY = "CASTOR_QLIK_API_KEY"

# API settings
API_BASE_PATH = "api/v1/"

# requests retry settings
RETRY_COUNTS = 3
RETRY_STATUSES = [404, 500, 502, 503, 504]
RETRY_BACKOFF_FACTOR = 0.5

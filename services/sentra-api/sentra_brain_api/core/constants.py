# core/constants.py
APP_NAME = "sentra_brain_api"
TITLE = "Sentra Brain API"
DESCRIPTION = "API for Sentra Brain platform."
VERSION = "0.1.0"
CONTACT = {"name": "Sentra Brain Team", "email": "juan@jgcarmona.com"}
LICENSE_INFO = {"name": "AGPLv3", "url": "https://www.gnu.org/licenses/agpl-3.0.en.html"}

SWAGGER_UI_PARAMETERS = {"defaultModelsExpandDepth": -1}
SWAGGER_FAVICON_URL = "https://sentrabrain.com/favicon.svg"

# vLLM server and conversation engine constants
VLLM_SERVER_URL = "http://vllm:8000"  # Default, override via settings if needed
USER_CONVERSATION_CACHE_SIZE = 5
CONTEXT_WINDOW_SIZE = 20
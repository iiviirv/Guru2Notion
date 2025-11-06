# Configuration Template

# Copy this file and rename to config.py
# DO NOT commit config.py to version control!

# Guru API Credentials
USER_EMAIL = "your.email@company.com"
USER_TOKEN = "your-guru-api-token-here"

# Optional: Override default settings

# Rate limiting (seconds between API calls)
API_DELAY = 0.15

# Maximum retries for failed API calls
MAX_RETRIES = 3

# Progress bar configuration
SHOW_PROGRESS_BARS = True  # Set to False to disable tqdm

# Logging level
# Options: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# Export options
# Warning threshold for large exports
WARN_THRESHOLD = 500

# Default batch size for API requests
BATCH_SIZE = 50

# Notion conversion options
CREATE_STATUS_BANNERS = True
CREATE_METADATA_TABLES = True
ENHANCE_LINK_PREVIEWS = True

# File paths
LOG_DIRECTORY = "guru_export_logs"
TEMP_DIRECTORY = "/tmp"

# How to use this config:
# 1. Copy this file: cp config.template.py config.py
# 2. Edit config.py with your credentials
# 3. Scripts will automatically load from config.py if it exists
# 4. config.py is in .gitignore so it won't be committed

# Example: Load config in your script
# try:
#     from config import USER_EMAIL, USER_TOKEN
# except ImportError:
#     USER_EMAIL = "default@example.com"
#     USER_TOKEN = "your-token-here"

import logging

# Configure logging (only runs once when imported)
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    # handlers=[
    #     logging.FileHandler("app.log"),  # Log to a file
    #     logging.StreamHandler()  # Log to console
    # ]
)

# Get the logger object
log = logging.getLogger(__name__)

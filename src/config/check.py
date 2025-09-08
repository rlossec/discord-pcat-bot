import os
from typing import List

from config.settings import REGISTRATIONS_FILE_PATH, REGISTRATION_LOG_PATH, PAST_REGISTRATIONS_FILE_PATH, BACKUP_FILE_PATH


def initialize_files(file_paths: List[str]):
    for file_path in file_paths:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

def check_mandatory_files_existence(file_paths: List[str]):
    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} file not found")


def check_configuration():
    # Check file existence
    log_data_paths = [REGISTRATIONS_FILE_PATH, REGISTRATION_LOG_PATH, PAST_REGISTRATIONS_FILE_PATH, BACKUP_FILE_PATH]
    initialize_files(log_data_paths)
    # Check mandatory files existence
    mandatory_files = [".env"]
    check_mandatory_files_existence(mandatory_files)

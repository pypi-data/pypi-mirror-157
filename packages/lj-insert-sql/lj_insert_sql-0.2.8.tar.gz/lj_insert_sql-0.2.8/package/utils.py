# 数据清洗链接
import os

DATA_PROCESS_HOST = os.getenv('DATA_PROCESS_HOST', '39.107.36.205')
DATA_PROCESS_PORT = os.getenv('DATA_PROCESS_PORT', 8080)
LICENSE_URL = os.getenv('LICENSE_URL', f'http://{DATA_PROCESS_HOST}:{DATA_PROCESS_PORT}/license/extract')

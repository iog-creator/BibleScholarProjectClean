from sqlalchemy import create_engine
from scripts.db_config import get_db_url
from colorama import Fore, init

init(autoreset=True)

def get_db_connection():
    print(Fore.CYAN + "Connecting to database...")
    try:
        url = get_db_url()
        engine = create_engine(url)
        conn = engine.connect()
        print(Fore.GREEN + "Database connection successful")
        return conn
    except Exception as e:
        print(Fore.RED + f"Connection error: {e}")
        raise
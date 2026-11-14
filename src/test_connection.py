import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:3306/{os.getenv('DB_NAME')}"
)

with create_engine(url).connect() as conn:
    print(conn.execute(text("SELECT VERSION()")).scalar())
    print(conn.execute(text("SELECT DATABASE()")).scalar())

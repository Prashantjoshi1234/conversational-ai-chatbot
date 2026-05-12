import os
import logging
from sqlalchemy import text
from backend.database.connection import SessionLocal
from backend.Authentication.authutils import hash_password
from dotenv import load_dotenv

load_dotenv()

#----logger configuration -----------------
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("admin_insertion.log")
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)

#------------------------------------------



USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")
ROLE = os.getenv("ROLE")



hashed_password = hash_password(PASSWORD)



def admin_insertion():

    db = SessionLocal()

    try:
        check_query = text(
            "SELECT * FROM users WHERE role = :role"
        )

        result = db.execute(
            check_query,
            {"role" : ROLE}
        ).fetchone()

        if result:
            logger.info("Admin already exists")
        else:
            insert_query = text(
                """
                INSERT INTO users (username, password, role)
                VALUES (:username, :password, :role)
                """
            )

            db.execute(
                insert_query,
                {
                    "username" : USERNAME,
                    "password" : hashed_password,
                    "role" : ROLE
                }
            )

            db.commit()

            logger.info("Admin added to The database successfully")

    except Exception as e:

        logger.error(f"Error inserting the admin : {e}")

    finally:

        db.close()

admin_insertion()
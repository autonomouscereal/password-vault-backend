# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from db_helper import DBHelper
from credential_manager import CredentialManager
import logging

db_helper = DBHelper()

# Use the same tokenUrl as before
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:3100/token")

# Use the same SECRET_KEY and ALGORITHM as your OAuth server
SECRET_KEY = CredentialManager.get_secret_key()
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode and verify the token using the shared SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None or email is None:
            logging.warning("Token validation failed: user_id or email not found in token")
            raise HTTPException(status_code=401, detail="Invalid token")
        # Convert user_id to integer if necessary
        user_id = int(user_id)

        # Ensure the user exists in the password vault backend
        user = await db_helper.get_user_by_id(user_id)
        if not user:
            # Create the user in the password vault's users table
            await db_helper.add_user(id=user_id, email=email)
            user = {"id": user_id, "email": email}

        # Return user information
        return user
    except jwt.ExpiredSignatureError:
        logging.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logging.error(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logging.error(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
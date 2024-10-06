# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List

from models import PasswordEntryCreate, PasswordEntryUpdate, PasswordEntry
from db_helper import DBHelper
import logging
from utils import encrypt_password, decrypt_password
import asyncpg
from auth import get_current_user

# Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Initialize DBHelper and database
db_helper = DBHelper()

@app.on_event("startup")
async def startup():
    await db_helper.init_db()

# Define allowed origins
origins = [
    "http://localhost:3300",
    "http://localhost:3300/add",
    "http://localhost:3300/dashboard",# Your frontend app's URL
    # Add other origins if needed
]

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
)

@app.post("/passwords/", response_model=PasswordEntry)
async def create_password_entry(
    entry: PasswordEntryCreate,
    current_user: dict = Depends(get_current_user)
):
    encrypted_pwd = encrypt_password(entry.password)
    try:
        await db_helper.add_password_entry(
            user_id=current_user['id'],
            website=entry.website,
            username=entry.username,
            encrypted_password=encrypted_pwd,
            notes=entry.notes
        )
        # Retrieve the newly created entry to return
        entries = await db_helper.get_password_entries(current_user['id'])
        new_entry = entries[-1]  # Assuming the last one is the new one
        return PasswordEntry(
            id=new_entry['id'],
            user_id=new_entry['user_id'],
            website=new_entry['website'],
            username=new_entry['username'],
            notes=new_entry['notes'],
            last_used=new_entry['last_used'],
            last_updated=new_entry['last_updated'],
            created_at=new_entry['created_at']
        )
    except Exception as e:
        logging.error(f"Error creating password entry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/passwords/", response_model=List[PasswordEntry])
async def get_password_entries(
    current_user: dict = Depends(get_current_user)
):
    try:
        entries = await db_helper.get_password_entries(current_user['id'])
        return [
            PasswordEntry(
                id=entry['id'],
                user_id=entry['user_id'],
                website=entry['website'],
                username=entry['username'],
                notes=entry['notes'],
                last_used=entry['last_used'],
                last_updated=entry['last_updated'],
                created_at=entry['created_at']
            ) for entry in entries
        ]
    except Exception as e:
        logging.error(f"Error retrieving password entries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/passwords/{entry_id}", response_model=PasswordEntry)
async def get_password_entry(
    entry_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        entry = await db_helper.get_password_entry(current_user['id'], entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Password entry not found")
        # Decrypt password
        decrypted_password = decrypt_password(entry['encrypted_password'])
        # Update last_used timestamp
        await db_helper.update_last_used(current_user['id'], entry_id)
        return PasswordEntry(
            id=entry['id'],
            user_id=entry['user_id'],
            website=entry['website'],
            username=entry['username'],
            password=decrypted_password,  # Include decrypted password
            notes=entry['notes'],
            last_used=entry['last_used'],
            last_updated=entry['last_updated'],
            created_at=entry['created_at']
        )
    except Exception as e:
        logging.error(f"Error retrieving password entry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/passwords/{entry_id}", response_model=PasswordEntry)
async def update_password_entry(
    entry_id: int,
    entry_update: PasswordEntryUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        existing_entry = await db_helper.get_password_entry(current_user['id'], entry_id)
        if not existing_entry:
            raise HTTPException(status_code=404, detail="Password entry not found")

        # Encrypt new password if provided
        if entry_update.password:
            encrypted_pwd = encrypt_password(entry_update.password)
        else:
            encrypted_pwd = existing_entry['encrypted_password']

        # Update the entry
        await db_helper.update_password_entry(
            user_id=current_user['id'],
            entry_id=entry_id,
            website=entry_update.website or existing_entry['website'],
            username=entry_update.username or existing_entry['username'],
            encrypted_password=encrypted_pwd,
            notes=entry_update.notes or existing_entry['notes']
        )

        # Retrieve updated entry
        updated_entry = await db_helper.get_password_entry(current_user['id'], entry_id)
        return PasswordEntry(
            id=updated_entry['id'],
            user_id=updated_entry['user_id'],
            website=updated_entry['website'],
            username=updated_entry['username'],
            notes=updated_entry['notes'],
            last_used=updated_entry['last_used'],
            last_updated=updated_entry['last_updated'],
            created_at=updated_entry['created_at']
        )
    except Exception as e:
        logging.error(f"Error updating password entry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/passwords/{entry_id}")
async def delete_password_entry(
    entry_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        await db_helper.delete_password_entry(current_user['id'], entry_id)
        return {"msg": "Password entry deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting password entry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# db_helper.py
import asyncpg
import sys
from credential_manager import CredentialManager


class DBHelper:
    def __init__(self):
        self.credentials = CredentialManager.get_db_credentials()

    async def init_db(self):
        print("Initializing the database...")
        await self.connect_create_if_not_exists(
            user=self.credentials['user'],
            database=self.credentials['database'],
            password=self.credentials['password'],
            port=self.credentials['port'],
            host=self.credentials['host']
        )

        conn = await self.get_db_connection()

        # Create Users table if it doesn't exist
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY NOT NULL,
                email VARCHAR UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # Create PasswordEntries table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS password_entries(
                id SERIAL PRIMARY KEY NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                website VARCHAR NOT NULL,
                username VARCHAR NOT NULL,
                encrypted_password TEXT NOT NULL,
                notes TEXT,
                last_used TIMESTAMPTZ,
                last_updated TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        # Commit and close the connection
        await conn.execute("COMMIT;")
        await conn.close()
        print("Database initialization complete.")

    @staticmethod
    async def connect_create_if_not_exists(user, database, password, port, host):
        try:
            conn = await asyncpg.connect(
                user=user, database=database, password=password, port=port, host=host
            )
            await conn.close()
        except asyncpg.InvalidCatalogNameError:
            print(f"Database '{database}' does not exist. Creating it...")
            sys_conn = await asyncpg.connect(
                database='postgres', user=user, password=password, port=port, host=host
            )
            await sys_conn.execute(f'CREATE DATABASE "{database}" OWNER "{user}"')
            await sys_conn.close()
            print(f"Database '{database}' created successfully.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)

    async def get_db_connection(self):
        return await asyncpg.connect(
            user=self.credentials['user'],
            database=self.credentials['database'],
            password=self.credentials['password'],
            port=self.credentials['port'],
            host=self.credentials['host']
        )

    # User-related methods
    async def get_user_by_email(self, email: str):
        conn = await self.get_db_connection()
        try:
            user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
            return user
        finally:
            await conn.close()

    async def get_user_by_id(self, user_id: int):
        conn = await self.get_db_connection()
        try:
            user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            return user
        finally:
            await conn.close()

    async def add_user(self, user_id: int, email: str):
        conn = await self.get_db_connection()
        try:
            await conn.execute("""
                 INSERT INTO users (id, email)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING;
            """, user_id, email)
        except asyncpg.UniqueViolationError as e:
            raise e
        finally:
            await conn.close()

    # Password Entry methods
    async def add_password_entry(self, user_id: int, website: str, username: str, encrypted_password: str,
                                 notes: str = None):
        conn = await self.get_db_connection()
        try:
            await conn.execute("""
                INSERT INTO password_entries(user_id, website, username, encrypted_password, notes)
                VALUES ($1, $2, $3, $4, $5)
            """, user_id, website, username, encrypted_password, notes)
        finally:
            await conn.close()

    async def get_password_entries(self, user_id: int):
        conn = await self.get_db_connection()
        try:
            entries = await conn.fetch("""
                SELECT * FROM password_entries WHERE user_id = $1
            """, user_id)
            return entries
        finally:
            await conn.close()

    async def get_password_entry(self, user_id: int, entry_id: int):
        conn = await self.get_db_connection()
        try:
            entry = await conn.fetchrow("""
                SELECT * FROM password_entries WHERE user_id = $1 AND id = $2
            """, user_id, entry_id)
            return entry
        finally:
            await conn.close()

    async def update_password_entry(self, user_id: int, entry_id: int, website: str, username: str,
                                    encrypted_password: str, notes: str):

        conn = await self.get_db_connection()
        try:
            await conn.execute("""
                UPDATE password_entries
                SET website = $1,
                    username = $2,
                    encrypted_password = $3,
                    notes = $4,
                    last_updated = NOW()
                WHERE user_id = $5 AND id = $6
            """, website, username, encrypted_password, notes, user_id, entry_id)
        finally:
            await conn.close()

    async def delete_password_entry(self, user_id: int, entry_id: int):
        conn = await self.get_db_connection()
        try:
            await conn.execute("""
                DELETE FROM password_entries WHERE user_id = $1 AND id = $2
            """, user_id, entry_id)
        finally:
            await conn.close()

    async def update_last_used(self, user_id: int, entry_id: int):
        conn = await self.get_db_connection()
        try:
            await conn.execute("""
                UPDATE password_entries
                SET last_used = NOW()
                WHERE user_id = $1 AND id = $2
            """, user_id, entry_id)
        finally:
            await conn.close()

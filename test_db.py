#!/usr/bin/env python3
import asyncpg
import asyncio

async def test_db_connection():
    try:
        # Try with password first
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5432/vocelio')
        print("✅ Database connection successful with password!")
        await conn.close()
        return True
    except Exception as e1:
        try:
            # Try without password (trust authentication)
            conn = await asyncpg.connect('postgresql://postgres@localhost:5432/vocelio')
            print("✅ Database connection successful without password!")
            await conn.close()
            return True
        except Exception as e2:
            print(f"❌ Database connection failed with password: {e1}")
            print(f"❌ Database connection failed without password: {e2}")
            return False

if __name__ == "__main__":
    asyncio.run(test_db_connection())

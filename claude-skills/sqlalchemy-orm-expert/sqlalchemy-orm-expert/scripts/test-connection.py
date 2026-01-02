#!/usr/bin/env python3
"""
Test database connection and verify SQLAlchemy setup.

Usage:
    python test-connection.py postgresql+asyncpg://user:pass@localhost/db
"""

import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection(database_url: str):
    """Test database connection."""
    print(f"Testing connection to: {database_url.split('@')[1] if '@' in database_url else database_url}")
    print("-" * 50)
    
    try:
        # Create engine
        print("Creating async engine...")
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0
        )
        
        # Test connection
        print("Testing connection...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            
            if value == 1:
                print("✅ Connection successful!")
            else:
                print("❌ Unexpected result")
                return False
        
        # Test database version
        print("\nQuerying database version...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"Database version: {version[:100]}...")
        
        # Check pool status
        pool = engine.pool
        print(f"\nConnection pool status:")
        print(f"  Pool size: {pool.size()}")
        print(f"  Checked out: {pool.checkedout()}")
        print(f"  Overflow: {pool.overflow()}")
        
        # Cleanup
        await engine.dispose()
        print("\n✅ All checks passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {type(e).__name__}")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test-connection.py DATABASE_URL")
        print("\nExamples:")
        print("  python test-connection.py postgresql+asyncpg://user:pass@localhost/db")
        print("  python test-connection.py sqlite+aiosqlite:///./test.db")
        sys.exit(1)
    
    database_url = sys.argv[1]
    
    success = asyncio.run(test_connection(database_url))
    
    sys.exit(0 if success else 1)

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from api.routes import auth_router, core_router
from db.database import Base, engine

# Import models so Base.metadata knows about all tables (required for create_all)
import db.models  # noqa: F401

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    """
    # Startup
    print("\n" + "=" * 60)
    print("🚀 Starting Chatbox API")
    print("=" * 60)

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

    # Check database connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("⚠️  Application may not function correctly!")

    yield

    # Shutdown
    engine.dispose()
    print("👋 Chatbox API shutdown complete")


app = FastAPI(lifespan=lifespan)

app.include_router(core_router)
app.include_router(auth_router)

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

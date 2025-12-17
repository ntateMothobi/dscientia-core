from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.api.v1 import lead, followup, listing, analytics, governance, ingestion, system
from app.core.database import engine, Base

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ProSi-mini API",
    description="A mini Property Sales Intelligence system.",
    version="0.3.0"
)

# --- Exception Handler ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # ... (existing handler)
    pass

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # ... (existing handler)
    pass

# Include API routers
app.include_router(lead.router, prefix="/api/v1")
app.include_router(followup.router, prefix="/api/v1")
app.include_router(listing.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(governance.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1") # New system router

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the ProSi-mini API"}

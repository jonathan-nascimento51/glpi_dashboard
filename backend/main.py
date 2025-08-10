from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from api.fastapi_routes import router as api_router
from api.v2_routes import router as v2_router

app = FastAPI(title="GLPI Dashboard API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/v1")

# Include v2 routes if feature flag is enabled
if os.getenv("FLAG_USE_V2_KPIS", "false").lower() == "true":
    app.include_router(v2_router, prefix="/v2")

@app.get("/")
def read_root():
    return {"message": "GLPI Dashboard API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.v1.endpoints import router as api_v1_router
from api.v2_routes import router as v2_router
from api.hexagonal_routes import router as hexagonal_router

app = FastAPI(
    title="GLPI Dashboard API",
    version="1.0.0",
    description="API para fornecer dados de KPIs do GLPI para um dashboard.",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para o domínio do frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include API routes
app.include_router(api_v1_router, prefix="/api/v1", tags=["v1"])

# Include v2 routes if feature flag is enabled
if os.getenv("FLAG_USE_V2_KPIS", "false").lower() == "true":
    app.include_router(v2_router, prefix="/api/v2", tags=["v2"])

# Include hexagonal architecture routes if feature flag is enabled
if os.getenv("FLAG_USE_HEXAGONAL", "false").lower() == "true":
    app.include_router(hexagonal_router, prefix="/hexagonal", tags=["Hexagonal"])

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "GLPI Dashboard API is running."}

@app.get("/health", tags=["Monitoring"])
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

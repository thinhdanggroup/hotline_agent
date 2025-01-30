from fastapi import FastAPI

app = FastAPI(
    title="Hotline Agent",
    description="FastAPI application for hotline agent",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Hotline Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

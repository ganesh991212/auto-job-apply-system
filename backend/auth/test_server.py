from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Auth Service Test")

@app.get("/")
async def root():
    return {"message": "Auth Service is running!", "timestamp": datetime.utcnow()}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "auth"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

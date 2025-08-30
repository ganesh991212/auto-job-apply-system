from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Core Service Test")

@app.get("/")
async def root():
    return {"message": "Core Service is running!", "timestamp": datetime.utcnow()}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "core"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

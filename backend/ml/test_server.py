from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="ML Service Test")

@app.get("/")
async def root():
    return {"message": "ML Service is running!", "timestamp": datetime.utcnow()}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ml"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

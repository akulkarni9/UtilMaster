from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import shutil

# Load environment variables first
load_dotenv()

from graph import app as agent_app
from ingestion import IngestionService

app = FastAPI(title="UtilMaster Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount uploads directory to serve files
# Files will be accessible at http://localhost:8000/uploads/filename
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

class ChatRequest(BaseModel):
    message: str

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return the absolute path so the agent can use it
        abs_path = os.path.abspath(file_path)
        
        # Trigger Ingestion in Background with fresh service instance
        def ingest_task():
            service = IngestionService()
            service.ingest_file(abs_path)
        
        background_tasks.add_task(ingest_task)
        
        return {"filename": file.filename, "filepath": abs_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_message = HumanMessage(content=request.message)
        
        # Invoke the agent graph with full state
        result = agent_app.invoke({
            "messages": [user_message],
            "uploaded_files": []  # TODO: Track files per session in future enhancement
        })
        
        # Extract the last AI message
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            return {"response": last_message.content}
        else:
            return {"response": "No response generated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

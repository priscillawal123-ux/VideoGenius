# Exemplos FastAPI - Video Genius
# API Básica para Processamento de Vídeos

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid

app = FastAPI(
    title="Video Genius API",
    description="API para processamento inteligente de vídeos",
    version="1.0.0"
)

# Modelos Pydantic
class VideoMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    duration: float
    resolution: str
    format: str

class ProcessingRequest(BaseModel):
    video_id: str
    operations: List[str]  # ["compress", "thumbnail", "transcribe"]

class VideoResponse(BaseModel):
    id: str
    status: str
    metadata: VideoMetadata
    processed_at: Optional[str] = None

# Banco de dados simulado
videos_db = {}

@app.post("/videos/upload", response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None
):
    """
    Faz upload de um vídeo para processamento.

    - **file**: Arquivo de vídeo (MP4, AVI, MOV, etc.)
    - **title**: Título opcional do vídeo
    - **description**: Descrição opcional do vídeo
    """
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(400, "Formato de vídeo não suportado")

    video_id = str(uuid.uuid4())

    # Simulação de processamento de metadados
    metadata = VideoMetadata(
        title=title or file.filename,
        description=description,
        duration=120.5,  # segundos
        resolution="1920x1080",
        format=file.filename.split('.')[-1].upper()
    )

    video = VideoResponse(
        id=video_id,
        status="uploaded",
        metadata=metadata
    )

    videos_db[video_id] = video
    return video

@app.post("/videos/{video_id}/process")
async def process_video(video_id: str, request: ProcessingRequest):
    """
    Inicia processamento do vídeo com operações específicas.

    Operações suportadas:
    - compress: Compressão de vídeo
    - thumbnail: Geração de thumbnail
    - transcribe: Transcrição de áudio
    - subtitles: Geração de legendas
    """
    if video_id not in videos_db:
        raise HTTPException(404, "Vídeo não encontrado")

    video = videos_db[video_id]

    # Validação das operações
    valid_operations = ["compress", "thumbnail", "transcribe", "subtitles"]
    invalid_ops = [op for op in request.operations if op not in valid_operations]

    if invalid_ops:
        raise HTTPException(400, f"Operações inválidas: {invalid_ops}")

    # Simulação de processamento assíncrono
    video.status = "processing"
    # Em produção, isso seria uma tarefa em background

    return {
        "video_id": video_id,
        "status": "processing",
        "operations": request.operations,
        "estimated_time": len(request.operations) * 30  # segundos
    }

@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Obtém informações de um vídeo específico."""
    if video_id not in videos_db:
        raise HTTPException(404, "Vídeo não encontrado")

    return videos_db[video_id]

@app.get("/videos", response_model=List[VideoResponse])
async def list_videos(skip: int = 0, limit: int = 10):
    """Lista vídeos com paginação."""
    videos = list(videos_db.values())[skip:skip + limit]
    return videos

@app.get("/videos/{video_id}/download")
async def download_video(video_id: str):
    """Faz download do vídeo processado."""
    if video_id not in videos_db:
        raise HTTPException(404, "Vídeo não encontrado")

    video = videos_db[video_id]
    if video.status != "completed":
        raise HTTPException(400, "Vídeo ainda não processado")

    # Simulação de streaming de arquivo
    def generate_video():
        # Em produção, isso leria o arquivo real
        yield b"fake video data"

    return StreamingResponse(
        generate_video(),
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename={video.metadata.title}.mp4"}
    )

@app.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    """Remove um vídeo do sistema."""
    if video_id not in videos_db:
        raise HTTPException(404, "Vídeo não encontrado")

    del videos_db[video_id]
    return {"message": "Vídeo removido com sucesso"}
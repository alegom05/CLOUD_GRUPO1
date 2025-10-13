from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slice_manager.models import (
    SliceCreate, SliceResponse, SlicesListResponse, 
    UserLogin, Token, SliceStatusUpdate
)
from slice_manager.manager import SliceManager

# Configuración de FastAPI
app = FastAPI(
    title="PUCP Cloud Orchestrator API",
    description="API para gestión de slices en cloud privado",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Instancia del manager
slice_manager = SliceManager()

# Función para verificar token (simplificada)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Aquí implementarías validación real del JWT
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    return {"username": "admin", "role": "admin"}

# === ENDPOINTS ===

@app.get("/")
async def root():
    return {
        "service": "PUCP Cloud Orchestrator",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint de autenticación"""
    # Aquí implementarías autenticación real
    if form_data.username and form_data.password:
        return {
            "access_token": "fake-jwt-token",
            "token_type": "bearer"
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas"
    )

@app.post("/api/slices", response_model=SliceResponse, status_code=status.HTTP_201_CREATED)
async def create_slice(
    slice_data: SliceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crear un nuevo slice"""
    try:
        slice = await slice_manager.create_slice(slice_data, current_user["username"])
        return SliceResponse(
            message="Slice creado exitosamente",
            slice=slice
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/slices", response_model=SlicesListResponse)
async def get_slices(
    owner: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Listar slices"""
    slices = slice_manager.get_slices(owner)
    return SlicesListResponse(
        slices=slices,
        total=len(slices)
    )

@app.get("/api/slices/{slice_id}")
async def get_slice(
    slice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener detalles de un slice"""
    slice = slice_manager.get_slice(slice_id)
    if not slice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice no encontrado"
        )
    return {"slice": slice}

@app.delete("/api/slices/{slice_id}")
async def delete_slice(
    slice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Eliminar un slice"""
    if not slice_manager.delete_slice(slice_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice no encontrado"
        )
    return {"message": "Slice eliminado exitosamente"}

@app.put("/api/slices/{slice_id}/status")
async def update_slice_status(
    slice_id: str,
    status_update: SliceStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar estado del slice"""
    if not slice_manager.update_slice_status(slice_id, status_update.status):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice no encontrado"
        )
    return {"message": "Estado actualizado exitosamente"}

@app.get("/api/health")
async def health_check():
    """Health check del servicio"""
    return {
        "status": "healthy",
        "service": "UI-APIs",
        "slices_count": len(slice_manager.slices)
    }

if __name__ == "__main__":
    import uvicorn
    print("=== PUCP Cloud Orchestrator API ===")
    print("Docs disponibles en: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
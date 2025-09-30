from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class TopologyType(str, Enum):
    LINEAL = "lineal"
    ANILLO = "anillo"
    ARBOL = "arbol"
    MALLA = "malla"
    BUS = "bus"

class VMBase(BaseModel):
    cpu: int = Field(default=1, ge=1, le=16)
    memory: int = Field(default=1024, ge=512, le=32768)
    disk: int = Field(default=10, ge=1, le=1000)

class VM(VMBase):
    id: str
    name: str
    status: str = "pending"
    host: Optional[str] = None

class SliceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    topology: TopologyType
    num_vms: int = Field(..., ge=1, le=20)
    cpu: int = Field(default=1, ge=1, le=16)
    memory: int = Field(default=1024, ge=512, le=32768)
    disk: int = Field(default=10, ge=1, le=1000)

class Slice(BaseModel):
    id: str
    name: str
    topology: TopologyType
    vms: List[VM]
    owner: str
    created_at: datetime
    status: str = "creating"

class SliceResponse(BaseModel):
    message: str
    slice: Slice

class SlicesListResponse(BaseModel):
    slices: List[Slice]
    total: int

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class SliceStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(creating|active|deleting|error|deleted)$")
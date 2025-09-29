import json
import os
from datetime import datetime
from typing import List, Optional
from .models import Slice, VM, SliceCreate, TopologyType
import asyncio
import uuid

class SliceManager:
    def __init__(self):
        self.storage_file = "slices.json"
        self.slices: List[Slice] = self._load_slices()
        
    def _load_slices(self) -> List[Slice]:
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    slices = []
                    for item in data:
                        # Convertir string a datetime si es necesario
                        if isinstance(item['created_at'], str):
                            item['created_at'] = datetime.fromisoformat(item['created_at'])
                        slice = Slice(**item)
                        slices.append(slice)
                    return slices
            except Exception as e:
                print(f"Error loading slices: {e}")
                return []
        return []
    
    def _save_slices(self):
        data = []
        for slice in self.slices:
            slice_dict = slice.model_dump()
            slice_dict['created_at'] = slice_dict['created_at'].isoformat()
            data.append(slice_dict)
        
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def create_slice(self, slice_data: SliceCreate, owner: str = "admin") -> Slice:
        """Crear slice de forma asíncrona"""
        # Generar ID único
        slice_id = f"slice_{uuid.uuid4().hex[:12]}"
        
        # Crear VMs
        vms = []
        for i in range(slice_data.num_vms):
            vm = VM(
                id=f"{slice_id}_vm_{i}",
                name=f"{slice_data.name}_vm_{i}",
                cpu=slice_data.cpu,
                memory=slice_data.memory,
                disk=slice_data.disk,
                status="pending"
            )
            vms.append(vm)
        
        # Crear slice
        new_slice = Slice(
            id=slice_id,
            name=slice_data.name,
            topology=slice_data.topology,
            vms=vms,
            owner=owner,
            created_at=datetime.now(),
            status="creating"
        )
        
        self.slices.append(new_slice)
        self._save_slices()
        
        # Simular envío asíncrono al gestor de colas
        asyncio.create_task(self._process_slice_async(new_slice))
        
        return new_slice
    
    async def _process_slice_async(self, slice: Slice):
        """Simula procesamiento asíncrono del slice"""
        await asyncio.sleep(2)  # Simular procesamiento
        slice.status = "active"
        self._save_slices()
        print(f"[SLICE MANAGER] Slice {slice.id} procesado y activo")
    
    def get_slices(self, owner: Optional[str] = None) -> List[Slice]:
        if owner:
            return [s for s in self.slices if s.owner == owner]
        return self.slices
    
    def get_slice(self, slice_id: str) -> Optional[Slice]:
        for slice in self.slices:
            if slice.id == slice_id:
                return slice
        return None
    
    def delete_slice(self, slice_id: str) -> bool:
        original_count = len(self.slices)
        self.slices = [s for s in self.slices if s.id != slice_id]
        
        if len(self.slices) < original_count:
            self._save_slices()
            return True
        return False
    
    def update_slice_status(self, slice_id: str, status: str) -> bool:
        slice = self.get_slice(slice_id)
        if slice:
            slice.status = status
            self._save_slices()
            return True
        return False
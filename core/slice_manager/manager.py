import json
import os
from datetime import datetime
from typing import List, Optional
from .models import Slice, VM, SliceCreate, TopologyType, TopologySegment, FlavorType
import uuid


class SliceManager:
    def __init__(self):
        self.storage_file = "slices.json"
        self.database_file = "base_de_datos.json"
        self.slices: List[Slice] = self._load_slices()
    
    def _load_slices(self) -> List[Slice]:
        slices = []
        
        # Cargar desde base_de_datos.json (prioridad)
        if os.path.exists(self.database_file):
            try:
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    if json_data and 'slices' in json_data:
                        for item in json_data['slices']:
                            # Convertir diccionario JSON a objeto Slice
                            slice_dict = {
                                'id': str(item.get('id', '')),
                                'name': item.get('nombre', ''),
                                'topology': TopologyType.LINEAR,  # Default
                                'owner': item.get('usuario', ''),
                                'created_at': datetime.now(),
                                'status': item.get('estado', 'activo'),
                                'vms': []
                            }
                            
                            # Convertir VMs
                            if 'vms' in item:
                                for vm_data in item['vms']:
                                    vm = VM(
                                        id=vm_data.get('nombre', ''),
                                        name=vm_data.get('nombre', ''),
                                        cpu=vm_data.get('cpu', 1),
                                        memory=vm_data.get('memory', 512),
                                        disk=vm_data.get('disk', 1),
                                        flavor=vm_data.get('flavor', 'small')
                                    )
                                    slice_dict['vms'].append(vm)
                            
                            slice_obj = Slice(**slice_dict)
                            slices.append(slice_obj)
                            
            except Exception as e:
                print(f"Error loading database JSON slices: {e}")
        
        # Cargar desde slices.json (complementario)
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        # Convertir string a datetime si es necesario
                        if isinstance(item['created_at'], str):
                            item['created_at'] = datetime.fromisoformat(item['created_at'])
                        # Reconstruir VMs como objetos VM
                        if 'vms' in item:
                            item['vms'] = [VM(**vm) if isinstance(vm, dict) else vm for vm in item['vms']]
                        slice = Slice(**item)
                        slices.append(slice)
            except Exception as e:
                print(f"Error loading JSON slices: {e}")
        
        return slices
    
    def _save_slices(self):
        """Guardar slices en archivo JSON"""
        data = []
        for slice in self.slices:
            # Convertir Slice a diccionario manualmente
            slice_dict = {
                'id': slice.id,
                'name': slice.name,
                'topology': slice.topology.value if hasattr(slice.topology, 'value') else str(slice.topology),
                'owner': slice.owner,
                'created_at': slice.created_at.isoformat() if isinstance(slice.created_at, datetime) else str(slice.created_at),
                'status': slice.status,
                'vms': []
            }
            
            # Convertir cada VM a diccionario
            for vm in slice.vms:
                vm_dict = {
                    'id': vm.id,
                    'name': vm.name,
                    'cpu': vm.cpu,
                    'memory': vm.memory,
                    'disk': vm.disk,
                    'status': vm.status,
                    'flavor': getattr(vm, 'flavor', 'small'),
                    'host': getattr(vm, 'host', ''),
                    'ip': getattr(vm, 'ip', ''),
                    'topology_group': getattr(vm, 'topology_group', 0),
                    'connections': getattr(vm, 'connections', [])
                }
                slice_dict['vms'].append(vm_dict)
            
            data.append(slice_dict)
        
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[DEBUG] Guardados {len(data)} slices en {self.storage_file}")
    
    def create_slice(self, slice_data: SliceCreate, owner: str = "cliente", vms_override: list = None) -> Slice:
        """Crear slice de forma síncrona"""
        slice_id = f"slice_{uuid.uuid4().hex[:12]}"

        # Usar vms_override si está presente, si no crear VMs por defecto
        if vms_override is not None:
            vms = vms_override
        else:
            vms = []
            for i in range(slice_data.num_vms):
                vm = VM(
                    id=f"{slice_id}_vm_{i}",
                    name=f"{slice_data.name}_vm_{i}",
                    cpu=slice_data.cpu,
                    memory=slice_data.memory,
                    disk=slice_data.disk,
                    status="pending",
                    flavor="small"
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
        
        print(f"[DEBUG] Slice creado: {slice_id}")
        print(f"[DEBUG] Total slices en memoria: {len(self.slices)}")

        return new_slice
    
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
import json
import os
from datetime import datetime
from typing import List, Optional
from .models import Slice, VM, SliceCreate, TopologyType, TopologySegment, FlavorType
import uuid


class SliceManager:
    def __init__(self):
        self.database_file = "base_de_datos.json"
        self.slices: List[Slice] = self._load_slices()
    
    def _load_slices(self) -> List[Slice]:
        slices = []
        
        # Cargar solo desde base_de_datos.json
        if os.path.exists(self.database_file):
            try:
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    if json_data and 'slices' in json_data:
                        for item in json_data['slices']:
                            slice_id = str(item.get('id', ''))
                            if slice_id:
                                # Convertir diccionario JSON a objeto Slice
                                slice_dict = {
                                    'id': slice_id,
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
                                            flavor=vm_data.get('flavor', 'f1')
                                        )
                                        slice_dict['vms'].append(vm)
                                
                                slice_obj = Slice(**slice_dict)
                                slices.append(slice_obj)
                            
            except Exception as e:
                print(f"Error loading database JSON slices: {e}")
        
        print(f"[DEBUG] Cargados {len(slices)} slices desde {self.database_file}")
        return slices
    
    def _save_slices(self):
        """Guardar slices solo en base_de_datos.json"""
        # Cargar estructura existente de base_de_datos.json
        database_data = {}
        if os.path.exists(self.database_file):
            try:
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    database_data = json.load(f)
            except:
                database_data = {}
        
        if 'slices' not in database_data:
            database_data['slices'] = []
        
        # Convertir slices al formato de base_de_datos.json
        database_slices = []
        for slice in self.slices:
            db_slice = {
                'id': slice.id,
                'nombre': slice.name,
                'topologia': slice.topology.value if hasattr(slice.topology, 'value') else str(slice.topology),
                'usuario': slice.owner,
                'estado': 'activo' if slice.status == 'creating' else slice.status,
                'vlan': len(database_slices) + 1,  # Generar VLAN incremental
                'vms': []
            }
            
            # Convertir VMs al formato de base_de_datos.json
            for vm in slice.vms:
                db_vm = {
                    'nombre': vm.name,
                    'cpu': vm.cpu,
                    'memory': vm.memory,
                    'disk': vm.disk,
                    'flavor': getattr(vm, 'flavor', 'f1')
                }
                db_slice['vms'].append(db_vm)
            
            database_slices.append(db_slice)
        
        database_data['slices'] = database_slices
        
        with open(self.database_file, 'w', encoding='utf-8') as f:
            json.dump(database_data, f, indent=2, ensure_ascii=False)
        
        print(f"[DEBUG] Guardados {len(database_slices)} slices en {self.database_file}")
    
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
                    flavor="f1"
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
            status="activo"
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
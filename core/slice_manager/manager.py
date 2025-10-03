import json
import os
from datetime import datetime
from typing import List, Optional
from .models import Slice, VM, SliceCreate, TopologyType, TopologySegment, FlavorType
import asyncio
import uuid

class SliceManager:
    def __init__(self):
        self.storage_file = "slices.json"
        self.slices: List[Slice] = self._load_slices()
    def _load_slices(self) -> List[Slice]:
        if os.path.exists(self.storage_file):
            try:
                from .models import VM
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    slices = []
                    for item in data:
                        # Convertir string a datetime si es necesario
                        if isinstance(item['created_at'], str):
                            item['created_at'] = datetime.fromisoformat(item['created_at'])
                        # Reconstruir VMs como objetos VM
                        if 'vms' in item:
                            item['vms'] = [VM(**vm) if isinstance(vm, dict) else vm for vm in item['vms']]
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
            slice_dict = slice.to_dict()
            # Si created_at es datetime, convertir a isoformat
            if isinstance(slice_dict['created_at'], (str, int)):
                pass
            else:
                slice_dict['created_at'] = slice_dict['created_at'].isoformat()
            data.append(slice_dict)
        
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def create_slice(self, slice_data: SliceCreate, owner: str = "cliente", vms_override: list = None) -> Slice:
        """Crear slice de forma asíncrona"""
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
    
    def create_mixed_slice(self, slice_data: dict, owner: str = "admin") -> Slice:
        """Crear un slice con topología mixta"""
        import uuid
        slice_id = f"slice_{uuid.uuid4().hex[:12]}"
        
        all_vms = []
        vm_counter = 0
        
        # Crear VMs para cada segmento de topología
        segment_vm_indices = []  # Para guardar los índices de las VMs de cada segmento
        for seg_idx, segment in enumerate(slice_data['topology_segments']):
            flavor_specs = get_flavor_specs(segment['flavor'])
            seg_vm_indices = []
            for i in range(segment['num_vms']):
                vm = VM(
                    id=f"vm_{vm_counter}",
                    name=f"Máquina {vm_counter + 1}",
                    cpu=flavor_specs['cpu'],
                    memory=flavor_specs['memory'],
                    disk=flavor_specs['disk'],
                    flavor=segment['flavor'],
                    status="running",
                    host=f"nodo{(vm_counter % 2) + 1}",
                    ip=f"10.0.0.{100 + vm_counter}",
                    topology_group=seg_idx,
                    connections=[]
                )
                # Conexiones internas de la topología
                if segment['type'] == 'lineal' and i > 0:
                    vm.connections.append(f"vm_{vm_counter - 1}")
                    all_vms[vm_counter - 1].connections.append(vm.id)
                elif segment['type'] == 'anillo':
                    if i > 0:
                        vm.connections.append(f"vm_{vm_counter - 1}")
                        all_vms[vm_counter - 1].connections.append(vm.id)
                    if i == segment['num_vms'] - 1:
                        first_vm_idx = vm_counter - segment['num_vms'] + 1
                        vm.connections.append(f"vm_{first_vm_idx}")
                        all_vms[first_vm_idx].connections.append(vm.id)
                seg_vm_indices.append(vm_counter)
                all_vms.append(vm)
                vm_counter += 1
            segment_vm_indices.append(seg_vm_indices)

        # Si hay más de un segmento, pedir al usuario qué VMs conectar entre segmentos
        if len(segment_vm_indices) > 1:
            print("\nSeleccione las VMs que conectarán los segmentos:")
            for i in range(len(segment_vm_indices)-1):
                seg1 = segment_vm_indices[i]
                seg2 = segment_vm_indices[i+1]
                print(f"  Segmento {i+1} VMs: {[f'vm_{idx}' for idx in seg1]}")
                print(f"  Segmento {i+2} VMs: {[f'vm_{idx}' for idx in seg2]}")
                vm1_idx = int(input(f"Seleccione el número de VM del segmento {i+1} para conectar: "))
                vm2_idx = int(input(f"Seleccione el número de VM del segmento {i+2} para conectar: "))
                vm1_id = f"vm_{seg1[vm1_idx]}"
                vm2_id = f"vm_{seg2[vm2_idx]}"
                all_vms[seg1[vm1_idx]].connections.append(vm2_id)
                all_vms[seg2[vm2_idx]].connections.append(vm1_id)

        # Crear objetos TopologySegment
        topology_segments = []
        current_vm = 0
        for segment in slice_data['topology_segments']:
            segment_vms = all_vms[current_vm:current_vm + segment['num_vms']]
            topology_segment = TopologySegment()
            topology_segment.type = TopologyType(segment['type'])
            topology_segment.vms = segment_vms
            topology_segment.flavor = FlavorType(segment['flavor'])
            topology_segments.append(topology_segment)
            current_vm += segment['num_vms']

        # Crear el slice
        new_slice = Slice(
            id=slice_id,
            name=slice_data['name'],
            topology=TopologyType.MIXED,
            vms=all_vms,
            owner=owner,
            created_at=datetime.now().isoformat(),
            status="active",
            topology_segments=topology_segments
        )

        self.slices.append(new_slice)
        self._save_slices()
        return new_slice

# --- Función utilitaria para specs de flavor ---
def get_flavor_specs(flavor_name):
    """Devuelve las especificaciones de CPU, memoria y disco para un flavor dado."""
    specs = {
        'tiny':   {'cpu': 1, 'memory': 512,  'disk': 1},
        'small':  {'cpu': 1, 'memory': 2048, 'disk': 20},
        'medium': {'cpu': 2, 'memory': 4096, 'disk': 40},
        'large':  {'cpu': 4, 'memory': 8192, 'disk': 80},
        'xlarge': {'cpu': 8, 'memory': 16384,'disk': 160},
    }
    return specs.get(flavor_name.lower(), specs['small'])
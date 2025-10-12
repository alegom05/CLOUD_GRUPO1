import yaml
import json
import os

BASE_YAML = os.path.join(os.path.dirname(__file__), '..', 'base_de_datos.yaml')
VMS_JSON = os.path.join(os.path.dirname(__file__), '..', 'vms.json')

def guardar_slice(slice_data):
    """Agrega un slice al archivo base_de_datos.yaml"""
    if os.path.exists(BASE_YAML):
        with open(BASE_YAML, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
    if 'slices' not in data:
        data['slices'] = []

    # Calcular id autoincremental
    if data['slices']:
        max_id = max([s.get('id', 0) for s in data['slices'] if isinstance(s.get('id', 0), int)] + [0])
        new_id = max_id + 1
        new_vlan = len(data['slices']) + 1
    else:
        new_id = 1
        new_vlan = 1

    slice_data = dict(slice_data)  # Copia para no modificar el original
    slice_data['id'] = new_id
    slice_data['vlan'] = new_vlan
    data['slices'].append(slice_data)
    with open(BASE_YAML, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)

def guardar_vms(vms_list):
    """Agrega VMs al archivo vms.json (sobrescribe todo el array)"""
    if os.path.exists(VMS_JSON):
        with open(VMS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"vms": []}
    data['vms'].extend(vms_list)
    with open(VMS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

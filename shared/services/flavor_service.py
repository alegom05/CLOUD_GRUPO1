"""
Servicio de gestión de flavors (tamaños de VMs)
"""

from shared.ui_helpers import show_error


def get_flavor_specs(flavor_name: str) -> dict:
    """
    Obtener especificaciones de un flavor
    
    Args:
        flavor_name: Nombre del flavor
        
    Returns:
        Diccionario con especificaciones (cpu, memory, disk)
    """
    flavors = {
        'tiny': {'cpu': 1, 'memory': 512, 'disk': 1},
        'small': {'cpu': 1, 'memory': 2048, 'disk': 20},
        'medium': {'cpu': 2, 'memory': 4096, 'disk': 40},
        'large': {'cpu': 4, 'memory': 8192, 'disk': 80},
        'xlarge': {'cpu': 8, 'memory': 16384, 'disk': 160}
    }
    return flavors.get(flavor_name, flavors['small'])


def select_flavor() -> str:
    """
    Seleccionar un flavor para las VMs de forma interactiva
    
    Returns:
        Nombre del flavor seleccionado
    """
    print("\n  Flavors disponibles:")
    print("  1. Tiny   (1 vCPU, 512MB RAM, 1GB Disk), Cirros-0.5.1")
    print("  2. Small  (1 vCPU, 2GB RAM, 20GB Disk), Cirros-0.5.1")
    print("  3. Medium (2 vCPU, 4GB RAM, 40GB Disk), Cirros-0.5.1")
    print("  4. Large  (4 vCPU, 8GB RAM, 80GB Disk), Cirros-0.5.1")
    print("  5. XLarge (8 vCPU, 16GB RAM, 160GB Disk), Cirros-0.5.1")
    
    choice = input("\n  Seleccione flavor (1-5): ")
    
    flavors = ['tiny', 'small', 'medium', 'large', 'xlarge']
    
    if choice.isdigit() and 1 <= int(choice) <= 5:
        return flavors[int(choice) - 1]
    
    show_error("Opción inválida, usando 'small' por defecto")
    return 'small'  # Default


def list_flavors() -> dict:
    """
    Obtiene la lista completa de flavors disponibles
    
    Returns:
        Diccionario con todos los flavors
    """
    return {
        'tiny': {'cpu': 1, 'memory': 512, 'disk': 1},
        'small': {'cpu': 1, 'memory': 2048, 'disk': 20},
        'medium': {'cpu': 2, 'memory': 4096, 'disk': 40},
        'large': {'cpu': 4, 'memory': 8192, 'disk': 80},
        'xlarge': {'cpu': 8, 'memory': 16384, 'disk': 160}
    }
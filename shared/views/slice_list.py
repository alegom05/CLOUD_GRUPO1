
from shared.ui_helpers import print_header, pause
from shared.colors import Colors

"""
Vista para listar slices
"""

def view_my_slices(slice_manager, user):
    """Ver MIS slices (CLIENTE)"""
    print_header(user)
    print(Colors.BOLD + "\n  MIS SLICES" + Colors.ENDC)
    
    slices = [s for s in slice_manager.get_slices() if s.owner == user.username]
    
    if not slices:
        print("\n  No tienes slices creados")
    else:
        for s in slices:
            print(f"\n  • {Colors.YELLOW}{s.name}{Colors.ENDC}")
            print(f"    ID: {s.id}")
            topology_name = s.topology.value if hasattr(s.topology, 'value') else s.topology
            print(f"    Topología: {topology_name}")
            print(f"    VMs: {len(s.vms)}")
        
    pause()


def view_all_slices(slice_manager):
    """Ver TODOS los slices (ADMIN)"""
    print_header()
    print(Colors.BOLD + "\n  TODOS LOS SLICES DEL SISTEMA" + Colors.ENDC)
    
    slices = slice_manager.get_slices()
    
    if not slices:
        print("\n  No hay slices en el sistema")
    else:
        print(f"\n  Total: {len(slices)} slices\n")
        for s in slices:
            print(f"  • {Colors.YELLOW}{s.id}{Colors.ENDC}")
            print(f"    Nombre: {s.name}")
            print(f"    Owner: {s.owner}")
            print(f"    Topología: {s.topology.value}")
            print(f"    VMs: {len(s.vms)}")
            print()
    
    pause()
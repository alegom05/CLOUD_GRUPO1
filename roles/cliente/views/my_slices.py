"""Vista para ver slices del cliente"""

from shared.ui_helpers import print_header
from shared.colors import Colors

def view_my_slices(user, slice_manager):
    """Muestra los slices del usuario"""
    print_header(user)
    print(Colors.BOLD + "\n  MIS SLICES" + Colors.ENDC)
    
    # DEBUG: Ahora SÍ se verán porque están DESPUÉS del header
    all_slices = slice_manager.get_slices()
    # print(f"\n[DEBUG] Total de slices en el sistema: {len(all_slices)}")
    # print(f"[DEBUG] Usuario actual: '{user.username}'")
    
    # DEBUG: Ver detalles de cada slice
    # for s in all_slices:
    #     print(f"[DEBUG] Slice: {s.name}, Owner: '{s.owner}'")
    
    # Filtrar por owner
    slices = [s for s in all_slices if s.owner == user.username]
    # print(f"[DEBUG] Slices filtrados para este usuario: {len(slices)}")
    
    if not slices:
        print("\n  No tienes slices creados")
    else:
        for s in slices:
            topology_name = s.topology.value if hasattr(s.topology, 'value') else s.topology
            print(f"\n  • {Colors.YELLOW}{s.name}{Colors.ENDC}")
            print(f"    ID: {s.id}")
            print(f"    Topología: {topology_name}")
            print(f"    VMs: {len(s.vms)}")
    
    input("\n  Presione Enter para continuar...")
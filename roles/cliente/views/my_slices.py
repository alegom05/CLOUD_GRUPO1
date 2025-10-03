"""Vista para ver slices del cliente"""

from shared.ui_helpers import print_header
from shared.colors import Colors

def view_my_slices(user, slice_manager):
    """Muestra los slices del usuario"""
    print_header(user)
    print(Colors.BOLD + "\n  MIS SLICES" + Colors.ENDC)
    
    slices = [s for s in slice_manager.get_slices() if s.owner == user.username]
    
    if not slices:
        print("\n  No tienes slices creados")
    else:
        for s in slices:
            print(f"\n  • {Colors.YELLOW}{s.name}{Colors.ENDC}")
            print(f"    ID: {s.id}")
            print(f"    Topología: {s.topology.value}")
            print(f"    VMs: {len(s.vms)}")
    
    input("\n  Presione Enter para continuar...")
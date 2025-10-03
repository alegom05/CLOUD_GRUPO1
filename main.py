from core.slice_manager.manager import SliceManager
from core.auth_manager import AuthManager
from core.slice_manager.models import UserRole, SliceCreate, TopologyType
from shared.ui_helpers import print_header, login_screen
from shared.colors import Colors
from shared.topology.ascii_drawer import draw_topology
from roles.admin.admin_menu import admin_menu
from roles.cliente.cliente_menu import cliente_menu



# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal del sistema"""
    slice_manager = SliceManager()
    auth_manager = AuthManager()
    
    while True:
        # Login
        if not auth_manager.current_user:
            login_screen(auth_manager)
        
        # Redirigir según rol
        if auth_manager.current_user:
            if auth_manager.current_user.role == UserRole.ADMIN:
                admin_menu(auth_manager, slice_manager)
            elif auth_manager.current_user.role == UserRole.CLIENTE:
                cliente_menu(auth_manager, slice_manager)


if __name__ == "__main__":
    main()
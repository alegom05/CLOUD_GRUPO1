"""Menú del cliente"""

from shared.ui_helpers import print_header, get_menu_choice
from shared.colors import Colors
from shared.views.slice_list import view_my_slices
from shared.views.slice_creation import create_slice_basic, create_mixed_slice
from shared.views.slice_details import show_slice_details_enhanced
from shared.views.slice_deletion import delete_my_slice


def cliente_menu(auth_manager, slice_manager):
    """Menú actualizado para CLIENTE"""
    
    while True:
        print_header(auth_manager.current_user)
        print(Colors.BOLD + "\n  MENÚ CLIENTE" + Colors.ENDC)
        print("  " + "="*40)
        
        print(Colors.YELLOW + "\n  Mis Recursos:" + Colors.ENDC)
        print("  1. Ver MIS Slices")
        print("  2. Crear Slice Simple")
        print("  3. Crear Slice con Topología Mixta")
        print("  4. Ver Detalles de Slice")
        print("  5. Eliminar MI Slice")
      
        
        print(Colors.RED + "\n  0. Cerrar Sesión" + Colors.ENDC)
        
        choice = get_menu_choice()
        
        if choice == '1':
            view_my_slices(slice_manager, auth_manager.current_user)
        elif choice == '2':
            create_slice_basic(slice_manager, auth_manager.current_user)
        elif choice == '3':
            create_mixed_slice(slice_manager, auth_manager.current_user)
        elif choice == '4':
            show_slice_details_enhanced(slice_manager, auth_manager.current_user)
        elif choice == '5':
            delete_my_slice(slice_manager, auth_manager.current_user)
        elif choice == '0':
            auth_manager.logout()
            break
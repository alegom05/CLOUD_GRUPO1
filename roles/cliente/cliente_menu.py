"""Menú principal para el rol CLIENTE"""

from shared.ui_helpers import print_header, get_menu_choice, pause
from shared.colors import Colors
from shared.views.slice_builder import SliceBuilder
from core.services.slice_api_service import SliceAPIService
import os


def cliente_menu(auth_manager, slice_manager):
    """Menú del cliente con nuevo constructor de slices"""
    
    # Obtener token del auth_manager
    token = auth_manager.api_service.token
    api_url = os.getenv('AUTH_API_URL', 'http://localhost:8080').replace('/auth', '')
    
    # Inicializar servicio de slices
    slice_api = SliceAPIService(api_url, token)
    
    while True:
        print_header(auth_manager.current_user)
        print(Colors.BOLD + "\n  MENÚ CLIENTE" + Colors.ENDC)
        print("  " + "="*50)
        
        print(Colors.YELLOW + "\n  Gestión de Slices:" + Colors.ENDC)
        print("  1. Crear Nuevo Slice")
        print("  2. Ver Mis Slices")
        print("  3. Ver Detalles de Slice")
        print("  4. Eliminar Slice")
        
        print(Colors.RED + "\n  0. Cerrar Sesión" + Colors.ENDC)
        
        choice = get_menu_choice()
        
        if choice == '1':
            # Usar constructor interactivo
            builder = SliceBuilder(auth_manager.current_user)
            nombre, topologia, vms_data = builder.start()
            
            if nombre and topologia and vms_data:
                # Crear slice en la API
                resultado = slice_api.create_slice(nombre, topologia, vms_data)
                if resultado:
                    from shared.ui_helpers import show_success
                    show_success(f"Slice creado exitosamente - VLAN: {resultado.get('vlan')}")
                    pause()
        
        elif choice == '2':
            _ver_mis_slices(slice_api, auth_manager.current_user)
        
        elif choice == '3':
            _ver_detalles_slice(slice_api, auth_manager.current_user)
        
        elif choice == '4':
            _eliminar_slice(slice_api, auth_manager.current_user)
        
        elif choice == '0':
            auth_manager.logout()
            break


def _ver_mis_slices(slice_api, user):
    """Ver slices del usuario"""
    print_header(user)
    print(Colors.BOLD + "\n  MIS SLICES" + Colors.ENDC)
    
    slices = slice_api.get_my_slices()
    
    if not slices:
        print("\n  No tienes slices creados")
    else:
        for s in slices:
            print(f"\n  • {Colors.YELLOW}{s['nombre_slice']}{Colors.ENDC}")
            print(f"    ID: {s['id']}")
            print(f"    VLAN: {s['vlan']}")
            print(f"    Topología: {s['topologia']}")
            print(f"    VMs: {len(s.get('vms', []))}")
    
    pause()


def _ver_detalles_slice(slice_api, user):
    """Ver detalles de un slice"""
    slices = slice_api.get_my_slices()
    
    if not slices:
        from shared.ui_helpers import show_info
        show_info("No tienes slices")
        pause()
        return
    
    print("\n  Seleccione slice:")
    for i, s in enumerate(slices):
        print(f"  {i+1}. {s['nombre_slice']}")
    
    choice = input("\n  Opción: ")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(slices):
            slice_id = slices[idx]['id']
            detalles = slice_api.get_slice_details(slice_id)
            
            if detalles:
                print_header(user)
                print(f"\n  SLICE: {detalles['nombre_slice']}")
                print(f"  VLAN: {detalles['vlan']}")
                print(f"  Topología: {detalles['topologia']}")
                print("\n  VMs:")
                for vm in detalles.get('vms', []):
                    print(f"  • {vm['nombre']} - IP: {vm['ip']} - VNC: {vm['puerto_vnc']}")
    except:
        pass
    
    pause()


def _eliminar_slice(slice_api, user):
    """Eliminar un slice"""
    slices = slice_api.get_my_slices()
    
    if not slices:
        from shared.ui_helpers import show_info
        show_info("No tienes slices")
        pause()
        return
    
    print("\n  Seleccione slice a eliminar:")
    for i, s in enumerate(slices):
        print(f"  {i+1}. {s['nombre_slice']}")
    
    choice = input("\n  Opción (0 para cancelar): ")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(slices):
            from shared.ui_helpers import confirm_action, show_success, show_error
            if confirm_action(f"¿Eliminar '{slices[idx]['nombre_slice']}'?"):
                if slice_api.delete_slice(slices[idx]['id']):
                    show_success("Slice eliminado")
                else:
                    show_error("Error al eliminar")
    except:
        pass
    
    pause()
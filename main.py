"""
Sistema de Orquestación PUCP Cloud
Main principal con autenticación externa vía API
"""

from core.slice_manager.manager import SliceManager
from core.auth_manager import AuthManager
from core.slice_manager.models import UserRole, SliceCreate, TopologyType
from shared.ui_helpers import print_header
from shared.colors import Colors
from shared.topology.ascii_drawer import draw_topology
from roles.admin.admin_menu import admin_menu
from roles.cliente.cliente_menu import cliente_menu
from shared.ui_styles import print_banner, print_credential, print_section
from shared.ui_helpers import login_screen

# Importar el servicio de API externa
from auth_api_service import AuthAPIService
from getpass import getpass
import sys


# ============================================================================
# FUNCIONES DE LOGIN CON API EXTERNA
# ============================================================================


def check_api_availability(auth_service: AuthAPIService) -> bool:
    """
    Verificar si la API de autenticación está disponible
    
    Args:
        auth_service: Instancia del servicio de autenticación
        
    Returns:
        True si la API está disponible
    """
    print(f"\n{Colors.CYAN}⏳ Verificando API de autenticación...{Colors.RESET}")
    
    if auth_service.check_health():
        print(f"{Colors.GREEN}✅ API disponible{Colors.RESET}\n")
        return True
    else:
        print(f"{Colors.RED}❌ API de autenticación no disponible{Colors.RESET}")
        print(f"\n{Colors.YELLOW}💡 Soluciones:{Colors.RESET}")
        print("   1. Verifica que Docker esté corriendo")
        print("   2. Ejecuta: sudo docker compose up -d")
        print("   3. Verifica el estado: sudo docker compose ps")
        print("   4. Revisa los logs: sudo docker compose logs -f")
        print(f"\n{Colors.YELLOW}   URL esperada: https://localhost:8443/auth{Colors.RESET}\n")
        
        respuesta = input(f"{Colors.CYAN}¿Deseas continuar sin conexión a la API? (s/n): {Colors.RESET}").lower()
        return respuesta in ['s', 'si', 'yes', 'y']

def login_with_api(auth_manager: AuthManager, auth_service: AuthAPIService) -> bool:
    """Realizar login usando la API externa"""
    
    # Verificar API
    api_available = check_api_availability(auth_service)
    
    if not api_available:
        print(f"{Colors.RED}No se puede continuar sin la API{Colors.ENDC}")
        return False
    
    max_intentos = 3
    
    for intento in range(max_intentos):
        # Llamar a la función de pantalla de login SOLO para pedir datos
        correo, password = login_screen(auth_manager)
        if not correo or not password:
            print(f"\n{Colors.RED}❌ Email y contraseña son requeridos{Colors.ENDC}")
            continue
        print(f"\n{Colors.CYAN}⏳ Autenticando...{Colors.ENDC}")
        # Llamar al login real de la API
        if auth_service.login(correo, password):
            # Si login exitoso, crear un usuario mínimo en auth_manager
            from types import SimpleNamespace
            user_data = auth_service.get_user_data() or {}
            from core.slice_manager.models import UserRole
            # Forzar el uso del rol mapeado
            rol_str = (auth_service.user_role or '').lower()
            if rol_str not in ['admin', 'cliente', 'usuario_avanzado']:
                rol_str = (user_data.get('rol', '') or 'cliente').lower()
            try:
                rol_enum = UserRole(rol_str)
            except Exception:
                rol_enum = UserRole.CLIENTE
            # Usar el método external_login para crear el usuario correctamente
            auth_manager.external_login(
                email=user_data.get('correo', correo),
                name=user_data.get('nombre', ''),
                role=rol_enum,
                token=auth_service.token,
                api_data=user_data
            )
            return True
        else:
            print(f"\n{Colors.RED}❌ Credenciales incorrectas o error de conexión{Colors.ENDC}")
    return False

def login_screen_api(auth_manager: AuthManager, auth_service: AuthAPIService):
    """
    Pantalla de login usando API externa
    
    Args:
        auth_manager: Gestor de autenticación local
        auth_service: Servicio de API externa
    """
    while not auth_manager.current_user:
        if not login_with_api(auth_manager, auth_service):
            print(f"\n{Colors.YELLOW}¿Desea intentar nuevamente? (s/n): {Colors.RESET}", end='')
            if input().lower() not in ['s', 'si', 'yes', 'y']:
                print(f"\n{Colors.CYAN}Saliendo del sistema...{Colors.RESET}")
                sys.exit(0)


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal del sistema con autenticación externa"""
    
    # Inicializar componentes
    slice_manager = SliceManager()
    auth_manager = AuthManager()
    auth_service = AuthAPIService()  # Servicio de API externa
    
    try:
        while True:
            # Login con API externa
            if not auth_manager.current_user:
                login_screen_api(auth_manager, auth_service)
            
            # Verificar que el token siga siendo válido
            if auth_manager.current_user and not auth_service.verify_token():
                print(f"\n{Colors.YELLOW}⚠️  Su sesión ha expirado. Por favor, inicie sesión nuevamente.{Colors.RESET}")
                auth_manager.logout()
                auth_service.logout()
                continue
            
            # Redirigir según rol
            if auth_manager.current_user:
                try:
                    if auth_manager.current_user.role == UserRole.ADMIN:
                        admin_menu(auth_manager, slice_manager, auth_service)

                    elif auth_manager.current_user.role == UserRole.CLIENTE:
                        cliente_menu(auth_manager, slice_manager, auth_service)

                except KeyboardInterrupt:
                    print(f"\n\n{Colors.YELLOW}Operación cancelada por el usuario{Colors.RESET}")
                    respuesta = input(f"\n{Colors.CYAN}¿Desea cerrar sesión? (s/n): {Colors.RESET}").lower()
                    if respuesta in ['s', 'si', 'yes', 'y']:
                        auth_manager.logout()
                        auth_service.logout()
                        print(f"{Colors.GREEN}✅ Sesión cerrada{Colors.RESET}")
                    continue
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Saliendo del sistema...{Colors.RESET}")
        if auth_manager.current_user:
            auth_service.logout()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
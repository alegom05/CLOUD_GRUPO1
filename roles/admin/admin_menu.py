"""Menú principal para el rol ADMIN - Ejemplo adaptado"""

from shared.ui_helpers import print_header, get_menu_choice, pause
from shared.colors import Colors
from shared.views.slice_builder import SliceBuilder
from core.services.slice_api_service import SliceAPIService
import os


def admin_menu(auth_manager, slice_manager, auth_service=None):
    """
    Menú principal para administradores
    
    Args:
        auth_manager: Gestor de autenticación local
        slice_manager: Gestor de slices
        auth_service: Servicio de API externa (opcional)
    """
    
    # Obtener token - priorizar auth_service si está disponible
    if auth_service and auth_service.token:
        token = auth_service.token
    elif hasattr(auth_manager, 'api_service') and auth_manager.api_service:
        token = auth_manager.api_service.token
    elif auth_manager.get_api_token():
        token = auth_manager.get_api_token()
    else:
        print(f"{Colors.RED}[ERROR] No se pudo obtener token de autenticación{Colors.ENDC}")
        pause()
        return
    
    # Configurar URL de la API
    api_url = os.getenv('AUTH_API_URL', 'http://localhost:8080').replace('/auth', '')
    
    # Obtener email del usuario
    user_email = auth_manager.get_current_user_email()
    
    # Inicializar servicio de slices
    slice_api = SliceAPIService(api_url, token, user_email)
    
    while True:
        # Verificar sesión
        if auth_service and not _verificar_sesion(auth_service, auth_manager):
            break

        # Encabezado unificado
        print(Colors.BLUE + "="*70 + Colors.ENDC)
        print(Colors.BOLD + Colors.GREEN + "\n  PUCP CLOUD ORCHESTRATOR - PANEL DE ADMINISTRACIÓN".center(70) + Colors.ENDC)
        print(Colors.BLUE + "="*70 + Colors.ENDC)

        # Usuario y rol
        user_email = auth_manager.get_current_user_email()
        user_name = auth_manager.get_current_user_name()
        print(f"\n  Administrador: {Colors.YELLOW}{user_name} ({user_email}){Colors.ENDC} | Rol: {Colors.RED}ADMIN{Colors.ENDC}")
        print(Colors.BLUE + "-"*70 + Colors.ENDC)

        print_header(auth_manager.current_user)
        print(Colors.BOLD + "\n  MENÚ ADMINISTRADOR" + Colors.ENDC)
        print("  " + "="*60)

        print(Colors.YELLOW + "\n  Gestión de Slices:" + Colors.ENDC)
        print("  1. Listar Slices")
        print("  2. Crear Slice")
        print("  3. Editar Slice")
        print("  4. Eliminar Slice")
        print("  5. Servicio de Monitoreo")
        print("  6. Ver Logs")
        print(Colors.RED + "\n  0. Cerrar Sesión" + Colors.ENDC)

        choice = input("\nSeleccione opción: ")

        if choice == '1':
            _ver_todos_slices(slice_api, auth_manager)
        elif choice == '2':
            _crear_slice_admin(slice_api, auth_manager)
        elif choice == '3':
            _editar_slice_admin(slice_api, auth_manager)
        elif choice == '4':
            _eliminar_slice_admin(slice_api, auth_manager)
        elif choice == '5':
            _servicio_monitoreo()
        elif choice == '6':
            _ver_logs(auth_manager)
        elif choice == '0':
            _cerrar_sesion(auth_manager, auth_service)
            break
        else:
            print(f"\n{Colors.RED}  ❌ Opción inválida{Colors.ENDC}")
            pause()
def _servicio_monitoreo():
    """Muestra información de acceso al servicio de monitoreo Grafana"""
    print("\n" + Colors.CYAN + "SERVICIO DE MONITOREO" + Colors.ENDC)
    print("  " + "="*50)
    print("\n  Acceso a Grafana:")
    print("  URL: https://localhost:8443/grafana")
    print("  Usuario: admin")
    print("  Contraseña: admin123\n")
    print("  Ya puedes ver tu servicio de monitoreo en el navegador.")
    input("\nPresiona Enter para continuar...")


def _verificar_sesion(auth_service, auth_manager):
    """Verificar si la sesión con la API sigue siendo válida"""
    if not auth_service:
        return True
    
    if not auth_service.verify_token():
        print(f"\n{Colors.RED}⚠️  Su sesión ha expirado{Colors.ENDC}")
        print(f"{Colors.YELLOW}Por favor, inicie sesión nuevamente{Colors.ENDC}")
        auth_manager.logout()
        auth_service.logout()
        pause()
        return False
    
    return True


def _verificar_estado_sesion(auth_service):
    """Verificar y mostrar estado de la sesión"""
    print_header(None)
    print(Colors.BOLD + "\n  ESTADO DE SESIÓN" + Colors.ENDC)
    print("  " + "="*50)
    
    print(f"\n{Colors.CYAN}⏳ Verificando token con la API...{Colors.ENDC}")
    
    if auth_service.verify_token():
        print(f"{Colors.GREEN}✅ Sesión válida y activa{Colors.ENDC}")
        user_data = auth_service.get_user_data()
        if user_data:
            print(f"\n{Colors.YELLOW}Información del usuario:{Colors.ENDC}")
            print(f"  • Nombre: {user_data.get('nombre', 'N/A')}")
            print(f"  • Email: {user_data.get('email', 'N/A')}")
            print(f"  • Rol: {user_data.get('rol', 'N/A')}")
    else:
        print(f"{Colors.RED}❌ Sesión inválida o expirada{Colors.ENDC}")
    
    pause()


def _ver_todos_slices(slice_api, auth_manager):
    """
    Ver todos los slices del sistema (Admin puede ver todos)
    
    Args:
        slice_api: Servicio de API de slices
        auth_manager: Gestor de autenticación
    """
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  TODOS LOS SLICES" + Colors.ENDC)
    print("  " + "="*50)
    
    try:
        print(f"\n{Colors.CYAN}⏳ Cargando slices...{Colors.ENDC}")
        
        # Leer todos los slices desde el archivo local
        import yaml, os
        BASE_YAML = os.path.join(os.path.dirname(__file__), '..', '..', 'base_de_datos.yaml')
        if os.path.exists(BASE_YAML):
            with open(BASE_YAML, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            slices = data.get('slices', [])
        else:
            slices = []
        
        if not slices:
            print(f"\n{Colors.YELLOW}  � No hay slices en el sistema{Colors.ENDC}")
        else:
            print(f"\n{Colors.GREEN}  Total de slices: {len(slices)}{Colors.ENDC}\n")
            
            for i, s in enumerate(slices, 1):
                nombre = s.get('nombre', s.get('nombre_slice', 'Sin nombre'))
                usuario = s.get('usuario', 'N/A')
                print(f"{Colors.YELLOW}  [{i}] {nombre}{Colors.ENDC}")
                print(f"      Usuario: {Colors.CYAN}{usuario}{Colors.ENDC}")
                print(f"      ID: {Colors.CYAN}{s.get('id', 'N/A')}{Colors.ENDC}")
                print(f"      VLAN: {Colors.GREEN}{s.get('vlan', 'N/A')}{Colors.ENDC}")
                print(f"      Topología: {s.get('topologia', 'N/A')}")
                print(f"      VMs: {len(s.get('vms', []))}")
                print(f"      Estado: {s.get('estado', 'activo')}")
                print()
    
    except Exception as e:
        from shared.ui_helpers import show_error
        show_error(f"Error al cargar slices: {str(e)}")
    
    pause()


def _ver_slices_por_usuario(slice_api, auth_manager):
    """Ver slices de un usuario específico"""
    if not auth_manager.has_permission("view_all_slices"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos{Colors.ENDC}")
        pause()
        return
    
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  SLICES POR USUARIO" + Colors.ENDC)
    print("  " + "="*50)
    
    email = input(f"\n{Colors.CYAN}  Email del usuario: {Colors.ENDC}").strip()
    
    if email:
        print(f"\n{Colors.CYAN}⏳ Buscando slices de {email}...{Colors.ENDC}")
        print(f"\n{Colors.YELLOW}💡 Implementar búsqueda por usuario{Colors.ENDC}")
    
    pause()


def _crear_slice_admin(slice_api, auth_manager):
    """
    Crear un nuevo slice como administrador usando el constructor interactivo
    
    Args:
        slice_api: Servicio de API de slices
        auth_manager: Gestor de autenticación
    """
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  CREAR NUEVO SLICE (ADMIN)" + Colors.ENDC)
    print("  " + "="*50 + "\n")
    
    # Verificar permisos
    if not auth_manager.has_permission("create_slice"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos para crear slices{Colors.ENDC}")
        print(f"{Colors.YELLOW}  Contacte al administrador{Colors.ENDC}")
        pause()
        return
    
    try:
        # Usar constructor interactivo
        builder = SliceBuilder(auth_manager.current_user)
        nombre, topologia, vms_data = builder.start()
        
        if nombre and topologia and vms_data:
            try:
                print(f"\n{Colors.CYAN}⏳ Creando slice en la API...{Colors.ENDC}")
                resultado = slice_api.create_slice(nombre, topologia, vms_data)
                if resultado:
                    from shared.ui_helpers import show_success
                    vlan = resultado.get('vlan', 'N/A')
                    slice_id = resultado.get('id', 'N/A')
                    show_success(f"Slice creado exitosamente")
                    print(f"\n{Colors.GREEN}  Detalles del Slice:{Colors.ENDC}")
                    print(f"  • ID: {slice_id}")
                    print(f"  • VLAN: {vlan}")
                    print(f"  • Nombre: {nombre}")
                    print(f"  • Topología: {topologia}")
                    print(f"  • VMs: {len(vms_data)}")
                else:
                    raise Exception("API no respondió correctamente")
            except Exception:
                # Ocultar logs de error de API, solo mostrar mensaje de guardado local
                vlan = 'local'
                slice_id = 'local'
                print(f"{Colors.YELLOW}No se pudo conectar con la API. El slice y las VMs se guardarán localmente...{Colors.ENDC}")
            # Guardar slice y VMs en archivos SIEMPRE
            try:
                from shared.data_store import guardar_slice, guardar_vms
                # Guardar slice primero para obtener el id y vlan reales
                slice_obj = {
                    'id': slice_id,
                    'nombre': nombre,
                    'usuario': getattr(auth_manager.current_user, 'username', ''),
                    'vlan': vlan,
                    'topologia': topologia,
                    'vms': vms_data
                }
                guardar_slice(slice_obj)

                # Leer el valor real de vlan (autoincremental) desde base_de_datos.yaml
                import yaml, os
                BASE_YAML = os.path.join(os.path.dirname(__file__), '..', '..', 'base_de_datos.yaml')
                with open(BASE_YAML, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                vlan_real = None
                if 'slices' in data and data['slices']:
                    for s in reversed(data['slices']):
                        if s.get('nombre') == nombre and s.get('usuario') == getattr(auth_manager.current_user, 'username', ''):
                            vlan_real = s.get('vlan')
                            break
                if vlan_real is None:
                    vlan_real = vlan if isinstance(vlan, int) else 1

                # Leer cuántas VMs existen ya en vms.json para calcular puerto_vnc
                import json
                VMS_JSON = os.path.join(os.path.dirname(__file__), '..', '..', 'vms.json')
                if os.path.exists(VMS_JSON):
                    with open(VMS_JSON, 'r', encoding='utf-8') as f:
                        vms_data_json = json.load(f)
                    total_vms = len(vms_data_json.get('vms', []))
                else:
                    total_vms = 0

                vms_guardar = []
                for idx, vm in enumerate(vms_data):
                    num_vm = idx + 1
                    ip = f"10.7.{vlan_real}.{num_vm+1}"
                    puerto_vnc = 5900 + total_vms + num_vm
                    vm_dict = dict(vm)
                    vm_dict['usuario'] = getattr(auth_manager.current_user, 'username', '')
                    vm_dict['nombre'] = f"vm{num_vm}"
                    vm_dict['ip'] = ip
                    vm_dict['puerto_vnc'] = puerto_vnc
                    vms_guardar.append(vm_dict)

                guardar_vms(vms_guardar)
                print(f"{Colors.OKGREEN}✔ Slice y VMs guardados correctamente en base_de_datos.yaml y vms.json{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}  [WARN] No se pudo guardar en base_de_datos.yaml o vms.json: {e}{Colors.ENDC}")
        else:
            print(f"\n{Colors.YELLOW}  Creación cancelada{Colors.ENDC}")
    
    except Exception as e:
        from shared.ui_helpers import show_error
        show_error(f"Error inesperado: {str(e)}")
        print(f"{Colors.RED}  Detalles técnicos: {e}{Colors.ENDC}")
    
    pause()


def _editar_slice_admin(slice_api, auth_manager):
    """Llama a la función de edición de slices desde slice_editor.py (admin puede editar cualquier slice)"""
    try:
        from roles.cliente.slice_editor import editar_slice
        editar_slice(slice_api, auth_manager)
    except ImportError as e:
        print(f"\nError importando editor: {e}")
    except Exception as e:
        print(f"\nError al editar slice: {e}")

def _eliminar_slice_admin(slice_api, auth_manager):
    """
    Eliminar cualquier slice del sistema (Admin puede eliminar todos)
    
    Args:
        slice_api: Servicio de API de slices
        auth_manager: Gestor de autenticación
    """
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  ELIMINAR SLICE (ADMIN)" + Colors.ENDC)
    print("  " + "="*50)
    
    # Verificar permisos
    if not auth_manager.has_permission("delete_any_slice"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos para eliminar slices{Colors.ENDC}")
        pause()
        return
    
    try:
        # Leer todos los slices
        import yaml, os
        BASE_YAML = os.path.join(os.path.dirname(__file__), '..', '..', 'base_de_datos.yaml')
        if os.path.exists(BASE_YAML):
            with open(BASE_YAML, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            slices = data.get('slices', [])
        else:
            slices = []

        if not slices:
            from shared.ui_helpers import show_info
            show_info("No hay slices en el sistema para eliminar")
            pause()
            return

        print(f"\n{Colors.YELLOW}  Seleccione slice a eliminar:{Colors.ENDC}")
        for i, s in enumerate(slices, 1):
            nombre = s.get('nombre', s.get('nombre_slice', 'Sin nombre'))
            usuario = s.get('usuario', 'N/A')
            print(f"  {i}. {nombre} (Usuario: {usuario}, VLAN: {s.get('vlan')})")

        print(f"  0. Cancelar")

        choice = input(f"\n{Colors.CYAN}  Opción: {Colors.ENDC}").strip()

        if choice == '0':
            print(f"\n{Colors.YELLOW}  Operación cancelada{Colors.ENDC}")
            pause()
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(slices):
                slice_seleccionado = slices[idx]
                from shared.ui_helpers import confirm_action, show_success, show_error

                print(f"\n{Colors.RED}  ⚠️  ADVERTENCIA (ADMIN):{Colors.ENDC}")
                print(f"  Esta acción eliminará permanentemente el slice")
                print(f"  '{slice_seleccionado.get('nombre', slice_seleccionado.get('nombre_slice', ''))}' del usuario '{slice_seleccionado.get('usuario')}'")
                print(f"  y todas sus VMs asociadas")

                if confirm_action(f"¿Confirmar eliminación?"):
                    print(f"\n{Colors.CYAN}⏳ Eliminando slice...{Colors.ENDC}")
                    # Eliminar slice del archivo
                    slices = [s for s in slices if s.get('id') != slice_seleccionado.get('id')]
                    data['slices'] = slices
                    with open(BASE_YAML, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, allow_unicode=True)
                    show_success("Slice eliminado exitosamente por Admin")
                else:
                    print(f"\n{Colors.YELLOW}  Eliminación cancelada{Colors.ENDC}")
            else:
                print(f"\n{Colors.RED}  ❌ Opción inválida{Colors.ENDC}")

        except ValueError:
            print(f"\n{Colors.RED}  ❌ Debe ingresar un número{Colors.ENDC}")
        except Exception as e:
            from shared.ui_helpers import show_error
            show_error(f"Error: {str(e)}")

    except Exception as e:
        from shared.ui_helpers import show_error
        show_error(f"Error al cargar slices: {str(e)}")

    pause()


def _ver_detalles_slice(slice_api, auth_manager):
    """Ver detalles de cualquier slice"""
    if not auth_manager.has_permission("view_all_slices"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos{Colors.ENDC}")
        pause()
        return
    
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  DETALLES DE SLICE" + Colors.ENDC)
    print("  " + "="*50)
    
    slice_id = input(f"\n{Colors.CYAN}  ID del slice: {Colors.ENDC}").strip()
    
    if slice_id:
        try:
            detalles = slice_api.get_slice_details(slice_id)
            if detalles:
                print(f"\n{Colors.YELLOW}Nombre:{Colors.ENDC} {detalles['nombre_slice']}")
                print(f"{Colors.YELLOW}VLAN:{Colors.ENDC} {detalles['vlan']}")
                print(f"{Colors.YELLOW}Topología:{Colors.ENDC} {detalles['topologia']}")
                print(f"\n{Colors.YELLOW}VMs:{Colors.ENDC}")
                for vm in detalles.get('vms', []):
                    print(f"  • {vm['nombre']} - IP: {vm['ip']}")
        except Exception as e:
            from shared.ui_helpers import show_error
            show_error(f"Error: {str(e)}")
    
    pause()


def _mostrar_estadisticas(slice_api, auth_manager):
    """Mostrar estadísticas del sistema"""
    if not auth_manager.has_permission("monitor_all"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos{Colors.ENDC}")
        pause()
        return
    
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  ESTADÍSTICAS DEL SISTEMA" + Colors.ENDC)
    print("  " + "="*60)
    
    print(f"\n{Colors.YELLOW}💡 Implementar endpoint de estadísticas en el backend{Colors.ENDC}")
    print(f"{Colors.CYAN}Información sugerida:{Colors.ENDC}")
    print("  • Total de slices activos")
    print("  • Total de VMs")
    print("  • Recursos utilizados")
    print("  • Slices por usuario")
    print("  • Topologías más usadas")
    
    pause()


def _gestionar_usuarios(auth_manager):
    """Gestionar usuarios del sistema"""
    if not auth_manager.has_permission("manage_users"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos para gestionar usuarios{Colors.ENDC}")
        pause()
        return
    
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  GESTIÓN DE USUARIOS" + Colors.ENDC)
    print("  " + "="*60)
    
    print(f"\n{Colors.YELLOW}💡 Los usuarios se gestionan en el sistema de autenticación{Colors.ENDC}")
    print(f"{Colors.CYAN}Acciones disponibles:{Colors.ENDC}")
    print("  • Crear usuario")
    print("  • Modificar usuario")
    print("  • Desactivar usuario")
    print("  • Asignar roles")
    
    print(f"\n{Colors.CYAN}Esta funcionalidad requiere endpoints específicos en la API{Colors.ENDC}")
    
    pause()


def _ver_logs(auth_manager):
    """Ver logs del sistema"""
    if not auth_manager.has_permission("access_all_logs"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos para ver logs{Colors.ENDC}")
        pause()
        return
    
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  LOGS DEL SISTEMA" + Colors.ENDC)
    print("  " + "="*60)
    
    print(f"\n{Colors.YELLOW}💡 Implementar visualización de logs{Colors.ENDC}")
    print(f"{Colors.CYAN}Tipos de logs sugeridos:{Colors.ENDC}")
    print("  • Acciones de usuarios")
    print("  • Creación/eliminación de slices")
    print("  • Errores del sistema")
    print("  • Accesos al sistema")
    
    pause()


def _cerrar_sesion(auth_manager, auth_service):
    """Cerrar sesión limpiando ambos sistemas"""
    print(f"\n{Colors.CYAN}👋 Cerrando sesión de administrador...{Colors.ENDC}")
    
    auth_manager.logout()
    print(f"{Colors.GREEN}  ✅ Sesión local cerrada{Colors.ENDC}")
    
    if auth_service:
        auth_service.logout()
        print(f"{Colors.GREEN}  ✅ Sesión API cerrada{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}¡Hasta pronto!{Colors.ENDC}")
    pause()
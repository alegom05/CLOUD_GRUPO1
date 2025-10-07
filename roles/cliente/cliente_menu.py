"""Menú principal para el rol CLIENTE"""

from shared.ui_helpers import print_header, get_menu_choice, pause
from shared.colors import Colors
from shared.views.slice_builder import SliceBuilder
from core.services.slice_api_service import SliceAPIService
import os


def cliente_menu(auth_manager, slice_manager, auth_service=None):
    """
    Menú del cliente con nuevo constructor de slices
    
    Args:
        auth_manager: Gestor de autenticación local
        slice_manager: Gestor de slices
        auth_service: Servicio de API externa (opcional)
    """
    
    # Obtener token - priorizar auth_service si está disponible
    if auth_service and auth_service.token:
        token = auth_service.token
        print(f"{Colors.GREEN}[DEBUG] Usando token de auth_service{Colors.ENDC}")
    elif hasattr(auth_manager, 'api_service') and auth_manager.api_service:
        token = auth_manager.api_service.token
        print(f"{Colors.YELLOW}[DEBUG] Usando token de auth_manager.api_service{Colors.ENDC}")
    elif auth_manager.get_api_token():
        token = auth_manager.get_api_token()
        print(f"{Colors.YELLOW}[DEBUG] Usando token de auth_manager{Colors.ENDC}")
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
        # Verificar que la sesión siga válida (solo para sesiones externas)
        if auth_service and not _verificar_sesion(auth_service, auth_manager):
            break

        # Encabezado unificado
        print(Colors.BLUE + "="*70 + Colors.ENDC)
        print(Colors.BOLD + Colors.GREEN + "\n  BIENVENIDO A PUCP CLOUD ORCHESTRATOR".center(70) + Colors.ENDC)
        print(Colors.BLUE + "="*70 + Colors.ENDC)

        # Usuario y rol
        user_email = auth_manager.get_current_user_email()
        print(f"\n  Usuario: {Colors.YELLOW}{user_email}{Colors.ENDC} | Rol: {Colors.GREEN}CLIENTE{Colors.ENDC}")
        print(Colors.BLUE + "-"*70 + Colors.ENDC)

        # Título del menú
        print_header(auth_manager.current_user)
        print(Colors.BOLD + "\n  MENÚ CLIENTE" + Colors.ENDC)
        print("  " + "="*50)

        # Sección Mis Recursos
        print(Colors.YELLOW + "\n  Gestión de Slices:" + Colors.ENDC)
        print("  1. Crear Nuevo Slice")
        print("  2. Ver Mis Slices")
        print("  3. Ver Detalles de Slice")
        print("  4. Editar Slice (Agregar VMs)")
        print("  5. Eliminar Slice")
        print("  6. Pausar/Reactivar Slice")
        print(Colors.RED + "\n  0. Cerrar Sesión" + Colors.ENDC)

        choice = input("\nSeleccione opción: ")

        if choice == '1':
            _crear_slice(slice_api, auth_manager, slice_builder=SliceBuilder)
        elif choice == '2':
            _ver_mis_slices(slice_api, auth_manager.current_user)
        elif choice == '3':
            _ver_detalles_slice(slice_api, auth_manager.current_user)
        elif choice == '4':
            _editar_slice(slice_api, auth_manager)
        elif choice == '5':
            _eliminar_slice(slice_api, auth_manager)
        elif choice == '6':
            _pausar_reactivar_slice(auth_manager)
        elif choice == '0':
            _cerrar_sesion(auth_manager, auth_service)
            break
        else:
            print(f"\n{Colors.RED}  ❌ Opción inválida{Colors.ENDC}")
            pause()
def _pausar_reactivar_slice(auth_manager):
    """Permite pausar o reactivar un slice del usuario actual"""
    import yaml, os
    BASE_YAML = os.path.join(os.path.dirname(__file__), '..', 'base_de_datos.yaml')
    if os.path.exists(BASE_YAML):
        with open(BASE_YAML, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        slices = data.get('slices', [])
    else:
        slices = []

    usuario_actual = getattr(auth_manager.current_user, 'username', '')
    slices_usuario = [s for s in slices if s.get('usuario') == usuario_actual]

    if not slices_usuario:
        from shared.ui_helpers import show_info
        show_info("No tienes slices para pausar/reactivar")
        pause()
        return

    print(f"\n{Colors.YELLOW}  Seleccione slice a pausar/reactivar:{Colors.ENDC}")
    for i, s in enumerate(slices_usuario, 1):
        estado = s.get('estado', 'activo')
        print(f"  {i}. {s.get('nombre', s.get('nombre_slice', ''))} (Estado: {estado})")
    print(f"  0. Cancelar")

    choice = input(f"\n{Colors.CYAN}  Opción: {Colors.ENDC}").strip()
    if choice == '0':
        print(f"\n{Colors.YELLOW}  Operación cancelada{Colors.ENDC}")
        pause()
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(slices_usuario):
            slice_sel = slices_usuario[idx]
            from shared.ui_helpers import confirm_action, show_success
            estado_actual = slice_sel.get('estado', 'activo')
            nuevo_estado = 'inactivo' if estado_actual == 'activo' else 'activo'
            accion = 'pausar' if nuevo_estado == 'inactivo' else 'reactivar'
            if confirm_action(f"¿Desea {accion} el slice '{slice_sel.get('nombre', slice_sel.get('nombre_slice', ''))}'?"):
                # Actualizar estado en base_de_datos.yaml
                for s in slices:
                    if s.get('id') == slice_sel.get('id'):
                        s['estado'] = nuevo_estado
                # Guardar
                data = {'slices': slices}
                with open(BASE_YAML, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True)
                show_success(f"Slice {'pausado' if nuevo_estado == 'inactivo' else 'reactivado'} exitosamente")
            else:
                print(f"\n{Colors.YELLOW}  Operación cancelada{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}  ❌ Opción inválida{Colors.ENDC}")
    except ValueError:
        print(f"\n{Colors.RED}  ❌ Debe ingresar un número{Colors.ENDC}")
    except Exception as e:
        from shared.ui_helpers import show_error
        show_error(f"Error: {str(e)}")
    pause()


def _verificar_sesion(auth_service, auth_manager):
    """
    Verificar si la sesión con la API sigue siendo válida
    
    Args:
        auth_service: Servicio de API externa
        auth_manager: Gestor de autenticación local
        
    Returns:
        True si la sesión es válida, False si expiró
    """
    if not auth_service:
        return True  # Si no hay auth_service, no verificamos
    
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
        print(f"{Colors.CYAN}Token autenticado correctamente{Colors.ENDC}")
        
        # Mostrar info adicional del usuario si está disponible
        user_data = auth_service.get_user_data()
        if user_data:
            print(f"\n{Colors.YELLOW}Información del usuario:{Colors.ENDC}")
            print(f"  • Nombre: {user_data.get('nombre', 'N/A')}")
            print(f"  • Email: {user_data.get('email', 'N/A')}")
            print(f"  • Rol: {user_data.get('rol', 'N/A')}")
    else:
        print(f"{Colors.RED}❌ Sesión inválida o expirada{Colors.ENDC}")
        print(f"{Colors.YELLOW}Deberá iniciar sesión nuevamente{Colors.ENDC}")
    
    pause()


def _crear_slice(slice_api, auth_manager, slice_builder):
    """
    Crear un nuevo slice usando el constructor interactivo
    
    Args:
        slice_api: Servicio de API de slices
        auth_manager: Gestor de autenticación
        slice_builder: Clase SliceBuilder para construcción interactiva
    """
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  CREAR NUEVO SLICE" + Colors.ENDC)
    print("  " + "="*50 + "\n")
    
    # Verificar permisos
    if not auth_manager.has_permission("create_slice"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos para crear slices{Colors.ENDC}")
        print(f"{Colors.YELLOW}  Contacte al administrador{Colors.ENDC}")
        pause()
        return
    
    try:
        # Usar constructor interactivo
        builder = slice_builder(auth_manager.current_user)
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
                BASE_YAML = os.path.join(os.path.dirname(__file__), '..', 'base_de_datos.yaml')
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
                VMS_JSON = os.path.join(os.path.dirname(__file__), '..', 'vms.json')
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


def _ver_mis_slices(slice_api, user):
    """
    Ver slices del usuario
    
    Args:
        slice_api: Servicio de API de slices
        user: Usuario actual
    """
    print_header(user)
    print(Colors.BOLD + "\n  MIS SLICES" + Colors.ENDC)
    print("  " + "="*50)
    
    try:
        print(f"\n{Colors.CYAN}⏳ Cargando slices...{Colors.ENDC}")
        slices = slice_api.get_my_slices()
        
        if not slices:
            print(f"\n{Colors.YELLOW}  📋 No tienes slices creados{Colors.ENDC}")
            print(f"{Colors.CYAN}  Usa la opción 1 para crear tu primer slice{Colors.ENDC}")
        else:
            print(f"\n{Colors.GREEN}  Total de slices: {len(slices)}{Colors.ENDC}\n")
            
            for i, s in enumerate(slices, 1):
                print(f"{Colors.YELLOW}  [{i}] {s['nombre_slice']}{Colors.ENDC}")
                print(f"      ID: {Colors.CYAN}{s['id']}{Colors.ENDC}")
                print(f"      VLAN: {Colors.GREEN}{s['vlan']}{Colors.ENDC}")
                print(f"      Topología: {s['topologia']}")
                print(f"      VMs: {len(s.get('vms', []))}")
                print(f"      Estado: {s.get('estado', 'activo')}")
                print()
    
    except Exception as e:
        from shared.ui_helpers import show_error
        show_error(f"Error al cargar slices: {str(e)}")
    
    pause()


def _ver_detalles_slice(slice_api, user):
    """
    Ver detalles completos de un slice
    
    Args:
        slice_api: Servicio de API de slices
        user: Usuario actual
    """
    print_header(user)
    print(Colors.BOLD + "\n  DETALLES DE SLICE" + Colors.ENDC)
    print("  " + "="*50)
    
    try:
        slices = slice_api.get_my_slices()
        
        if not slices:
            from shared.ui_helpers import show_info
            show_info("No tienes slices")
            pause()
            return
        
        print(f"\n{Colors.CYAN}  Seleccione slice:{Colors.ENDC}")
        for i, s in enumerate(slices, 1):
            print(f"  {i}. {s['nombre_slice']} (VLAN: {s['vlan']})")
        
        print(f"  0. Cancelar")
        
        choice = input(f"\n{Colors.CYAN}  Opción: {Colors.ENDC}").strip()
        
        if choice == '0':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(slices):
                slice_id = slices[idx]['id']
                
                print(f"\n{Colors.CYAN}⏳ Cargando detalles...{Colors.ENDC}")
                detalles = slice_api.get_slice_details(slice_id)
                
                if detalles:
                    print_header(user)
                    print(Colors.BOLD + f"\n  SLICE: {detalles['nombre_slice']}" + Colors.ENDC)
                    print("  " + "="*50)
                    
                    print(f"\n{Colors.YELLOW}  Información General:{Colors.ENDC}")
                    print(f"  • ID: {detalles['id']}")
                    print(f"  • VLAN: {Colors.GREEN}{detalles['vlan']}{Colors.ENDC}")
                    print(f"  • Topología: {detalles['topologia']}")
                    print(f"  • Estado: {detalles.get('estado', 'activo')}")
                    
                    vms = detalles.get('vms', [])
                    if vms:
                        print(f"\n{Colors.YELLOW}  Máquinas Virtuales ({len(vms)}):{Colors.ENDC}")
                        for vm in vms:
                            print(f"\n  {Colors.CYAN}• {vm['nombre']}{Colors.ENDC}")
                            print(f"    IP: {vm.get('ip', 'N/A')}")
                            print(f"    VNC: {vm.get('puerto_vnc', 'N/A')}")
                            print(f"    Estado: {vm.get('estado', 'N/A')}")
                    else:
                        print(f"\n{Colors.YELLOW}  No hay VMs asociadas{Colors.ENDC}")
                else:
                    from shared.ui_helpers import show_error
                    show_error("No se pudieron cargar los detalles")
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
    pause()


def _editar_slice(slice_api, auth_manager):
    """Llama a la función de edición de slices desde slice_editor.py"""
    try:
        from roles.cliente.slice_editor import editar_slice
        editar_slice(slice_api, auth_manager)
    except ImportError as e:
        print(f"\nError importando editor: {e}")
    except Exception as e:
        print(f"\nError al editar slice: {e}")


def _eliminar_slice(slice_api, auth_manager):
    """
    Eliminar un slice del usuario
    
    Args:
        slice_api: Servicio de API de slices
        auth_manager: Gestor de autenticación
    """
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  ELIMINAR SLICE" + Colors.ENDC)
    print("  " + "="*50)
    
    # Verificar permisos
    if not auth_manager.has_permission("delete_own_slice"):
        print(f"\n{Colors.RED}  ❌ No tiene permisos para eliminar slices{Colors.ENDC}")
        pause()
        return
    
    try:
        # Leer slices locales
        import yaml, os
        BASE_YAML = os.path.join(os.path.dirname(__file__), '..', 'base_de_datos.yaml')
        if os.path.exists(BASE_YAML):
            with open(BASE_YAML, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            slices = data.get('slices', [])
        else:
            slices = []

        # Filtrar slices del usuario actual
        usuario_actual = getattr(auth_manager.current_user, 'username', '')
        slices_usuario = [s for s in slices if s.get('usuario') == usuario_actual]

        if not slices_usuario:
            from shared.ui_helpers import show_info
            show_info("No tienes slices para eliminar")
            pause()
            return

        print(f"\n{Colors.YELLOW}  Seleccione slice a eliminar:{Colors.ENDC}")
        for i, s in enumerate(slices_usuario, 1):
            print(f"  {i}. {s.get('nombre', s.get('nombre_slice', ''))} (VLAN: {s.get('vlan')})")

        print(f"  0. Cancelar")

        choice = input(f"\n{Colors.CYAN}  Opción: {Colors.ENDC}").strip()

        if choice == '0':
            print(f"\n{Colors.YELLOW}  Operación cancelada{Colors.ENDC}")
            pause()
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(slices_usuario):
                slice_seleccionado = slices_usuario[idx]
                from shared.ui_helpers import confirm_action, show_success, show_error

                print(f"\n{Colors.RED}  ⚠️  ADVERTENCIA:{Colors.ENDC}")
                print(f"  Esta acción eliminará permanentemente el slice")
                print(f"  '{slice_seleccionado.get('nombre', slice_seleccionado.get('nombre_slice', ''))}' y todas sus VMs")

                if confirm_action(f"¿Confirmar eliminación?"):
                    print(f"\n{Colors.CYAN}⏳ Eliminando slice...{Colors.ENDC}")
                    # Eliminar slice del archivo
                    slices = [s for s in slices if s.get('id') != slice_seleccionado.get('id')]
                    data['slices'] = slices
                    with open(BASE_YAML, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, allow_unicode=True)
                    show_success("Slice eliminado exitosamente")
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


def _cerrar_sesion(auth_manager, auth_service):
    """
    Cerrar sesión limpiando ambos sistemas
    
    Args:
        auth_manager: Gestor de autenticación local
        auth_service: Servicio de API externa
    """
    print(f"\n{Colors.CYAN}👋 Cerrando sesión...{Colors.ENDC}")
    
    # Cerrar sesión local
    auth_manager.logout()
    print(f"{Colors.GREEN}  ✅ Sesión local cerrada{Colors.ENDC}")
    
    # Cerrar sesión en la API externa si existe
    if auth_service:
        auth_service.logout()
        print(f"{Colors.GREEN}  ✅ Sesión API cerrada{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}¡Hasta pronto!{Colors.ENDC}")
    pause()
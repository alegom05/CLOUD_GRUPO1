"""Menú principal para el rol CLIENTE"""

from shared.ui_helpers import print_header, get_menu_choice, pause
from shared.colors import Colors
from shared.views.slice_builder import SliceBuilder
import os


def cliente_menu(auth_manager, slice_manager, auth_service=None):
    """
    Menú del cliente con funcionamiento local
    
    Args:
        auth_manager: Gestor de autenticación local
        slice_manager: Gestor de slices
        auth_service: Servicio de API externa (no usado)
    """
    
    while True:
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
        print("  2. Ver mis slices")
        print("  3. Eliminar Slice")
        print("  4. Pausar/Reactivar Slice")
        print(Colors.RED + "\n  0. Cerrar Sesión" + Colors.ENDC)

        choice = input("\nSeleccione opción: ")

        if choice == '1':
            _crear_slice(auth_manager, slice_manager, slice_builder=SliceBuilder)
        elif choice == '2':
            ver_mis_slices_y_detalles(auth_manager, slice_manager)
        elif choice == '3':
            _eliminar_slice(auth_manager, slice_manager)
        elif choice == '4':
            _pausar_reactivar_slice(auth_manager, slice_manager)
        elif choice == '0':
            _cerrar_sesion(auth_manager, auth_service)
            return
        else:
            print(f"\n{Colors.RED}  ❌ Opción inválida{Colors.ENDC}")
            pause()
def _pausar_reactivar_slice(auth_manager, slice_manager):
    """Permite pausar o reactivar un slice del usuario actual"""
    # Obtener slices del usuario usando SliceManager
    usuario_actual_email = getattr(auth_manager.current_user, 'email', '')
    usuario_actual_username = getattr(auth_manager.current_user, 'username', '')
    
    # Obtener todos los slices del SliceManager
    all_slices = slice_manager.get_slices()
    
    # Filtrar slices del usuario actual (usando email o username)
    slices_usuario = []
    for s in all_slices:
        if (s.owner == usuario_actual_email or 
            s.owner == usuario_actual_username or
            (hasattr(s, 'usuario') and s.usuario == usuario_actual_username)):
            slices_usuario.append(s)

    if not slices_usuario:
        from shared.ui_helpers import show_info
        show_info("No tienes slices para pausar/reactivar")
        pause()
        return

    print(f"\n{Colors.YELLOW}  Seleccione slice a pausar/reactivar:{Colors.ENDC}")
    for i, s in enumerate(slices_usuario, 1):
        estado = s.status
        print(f"  {i}. {s.name} (Estado: {estado})")
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
            estado_actual = slice_sel.status
            nuevo_estado = 'inactivo' if estado_actual == 'activo' else 'activo'
            accion = 'pausar' if nuevo_estado == 'inactivo' else 'reactivar'
            if confirm_action(f"¿Desea {accion} el slice '{slice_sel.name}'?"):
                # Actualizar estado usando SliceManager
                if slice_manager.update_slice_status(slice_sel.id, nuevo_estado):
                    show_success(f"Slice {'pausado' if nuevo_estado == 'inactivo' else 'reactivado'} exitosamente")
                else:
                    from shared.ui_helpers import show_error
                    show_error("No se pudo actualizar el estado del slice")
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


def _crear_slice(auth_manager, slice_manager, slice_builder):
    """
    Crear un nuevo slice usando el constructor interactivo
    
    Args:
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
        builder = slice_builder(auth_manager.current_user)
        nombre, topologia, vms_data, salida_internet = builder.start()

        if nombre and topologia and vms_data:
            print(f"{Colors.CYAN}📁 Guardando slice localmente...{Colors.ENDC}")
            try:
                # Debug para ver qué usuario se está usando
                current_username = getattr(auth_manager.current_user, 'username', '')
                current_email = getattr(auth_manager.current_user, 'email', '')
                print(f"[DEBUG CREAR] Username: '{current_username}'")
                print(f"[DEBUG CREAR] Email: '{current_email}'")

                # Crear objeto slice usando SliceManager
                from core.slice_manager.models import SliceCreate, TopologyType, VM

                # Determinar topología
                topology = TopologyType.LINEAR  # Default
                if 'anillo' in topologia.lower():
                    topology = TopologyType.RING
                elif 'estrella' in topologia.lower():
                    topology = TopologyType.STAR
                elif 'malla' in topologia.lower():
                    topology = TopologyType.MESH

                slice_create_obj = SliceCreate(
                    name=nombre,
                    topology=topology,
                    num_vms=len(vms_data),
                    cpu=1,
                    memory=512,
                    disk=1
                )

                # Crear VMs override con los datos específicos
                vms_override = []
                for i, vm_data in enumerate(vms_data):
                    vm = VM(
                        id=f"{nombre}_vm_{i}",
                        name=vm_data.get('nombre', f"vm{i+1}"),
                        cpu=vm_data.get('cpu', 1),
                        memory=vm_data.get('memory', 512),
                        disk=vm_data.get('disk', 1),
                        flavor=vm_data.get('flavor', 'f1'),
                        status="activo"
                    )
                    # Añadir atributo conexion_remota si existe
                    if 'conexion_remota' in vm_data:
                        vm.conexion_remota = vm_data['conexion_remota']
                    vms_override.append(vm)

                # Usar email en lugar de username para consistencia
                usuario_owner = current_email if current_email else current_username

                # Crear slice usando SliceManager
                slice_obj = slice_manager.create_slice(slice_create_obj, usuario_owner, vms_override)

                # Guardar salida_internet en el JSON
                import json
                dbfile = 'base_de_datos.json'
                with open(dbfile, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for s in data['slices']:
                    if s['id'] == slice_obj.id:
                        s['salida_internet'] = salida_internet
                        # Actualizar conexion_remota en cada VM
                        for idx, vm in enumerate(s.get('vms', [])):
                            if idx < len(vms_data):
                                vm['conexion_remota'] = vms_data[idx].get('conexion_remota', 'no')
                with open(dbfile, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                print(f"{Colors.GREEN}✅ Slice '{nombre}' creado exitosamente{Colors.ENDC}")
                print(f"  • ID: {slice_obj.id}")
                print(f"  • Nombre: {nombre}")
                print(f"  • Topología: {topologia}")
                print(f"  • VMs: {len(vms_data)}")
                print(f"  • Owner: {slice_obj.owner}")

            except Exception as e:
                print(f"{Colors.RED}❌ Error guardando slice: {e}{Colors.ENDC}")
                # Fallback al método anterior si falla
                from shared.data_store import guardar_slice
                slice_obj = {
                    'id': 'local',
                    'nombre': nombre,
                    'usuario': current_email if current_email else current_username,
                    'vlan': 'local',
                    'topologia': topologia,
                    'vms': vms_data,
                    'salida_internet': salida_internet
                }
                guardar_slice(slice_obj)
                print(f"{Colors.YELLOW}⚠️  Slice guardado usando método de respaldo{Colors.ENDC}")

            pause()
            return
        else:
            print(f"\n{Colors.YELLOW}  Creación cancelada{Colors.ENDC}")
    except Exception as e:
        from shared.ui_helpers import show_error
        show_error(f"Error inesperado: {str(e)}")
        print(f"{Colors.RED}  Detalles técnicos: {e}{Colors.ENDC}")
def _ver_mis_slices(user):
    """
    Ver slices del usuario
    
    Args:
        user: Usuario actual
    """
    print_header(user)
    print(Colors.BOLD + "\n  MIS SLICES" + Colors.ENDC)
    print("  " + "="*50)
    
    try:
        print(f"\n{Colors.CYAN}📁 Cargando slices desde archivos locales...{Colors.ENDC}")
        # Leer slices desde archivo local
        import yaml, os
        BASE_YAML = os.path.join(os.path.dirname(__file__), '..', '..', 'base_de_datos.yaml')
        if os.path.exists(BASE_YAML):
            with open(BASE_YAML, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            slices = data.get('slices', [])
        else:
            slices = []
        
        # Filtrar slices del usuario actual
        usuario_actual = getattr(user, 'username', '')
        slices_usuario = [s for s in slices if s.get('usuario') == usuario_actual]
        
        if not slices_usuario:
            print(f"\n{Colors.YELLOW}  📋 No tienes slices creados{Colors.ENDC}")
            print(f"{Colors.CYAN}  Usa la opción 1 para crear tu primer slice{Colors.ENDC}")
        else:
            print(f"\n{Colors.GREEN}  Total de slices: {len(slices_usuario)}{Colors.ENDC}\n")
            
            for i, s in enumerate(slices_usuario, 1):
                nombre = s.get('nombre', s.get('nombre_slice', 'Sin nombre'))
                print(f"{Colors.YELLOW}  [{i}] {nombre}{Colors.ENDC}")
                print(f"      ID: {Colors.CYAN}{s.get('id', 'local')}{Colors.ENDC}")
                print(f"      Topología: {s.get('topologia', 'N/A')}")
                print(f"      VMs: {len(s.get('vms', []))}")
                # Mostrar imagen de cada VM
                vms = s.get('vms', [])
                for idx, vm in enumerate(vms, 1):
                    imagen = vm.get('imagen', 'cirros-0.5.1-x86_64-disk.img')
                    conexion_remota = vm.get('conexion_remota', 'no')
                    print(f"         VM{idx} imagen: {imagen} | Conexión remota: {conexion_remota}")
                print(f"      Estado: {s.get('estado', 'activo')}")
                print(f"      Salida a internet: {s.get('salida_internet', 'no')}")
                print()
    
    except Exception as e:
        from shared.ui_helpers import show_error
        show_error(f"Error al cargar slices: {str(e)}")
    
    pause()


def _ver_detalles_slice(user):
    """
    Ver detalles completos de un slice
    
    Args:
        user: Usuario actual
    """
    print_header(user)
    print(Colors.BOLD + "\n  DETALLES DE SLICE" + Colors.ENDC)
    print("  " + "="*50)
    
    try:
        print(f"\n{Colors.CYAN}📁 Cargando slices desde archivos locales...{Colors.ENDC}")
        
        # Leer slices desde archivo local
        import yaml, os
        BASE_YAML = os.path.join(os.path.dirname(__file__), '..', '..', 'base_de_datos.yaml')
        if os.path.exists(BASE_YAML):
            with open(BASE_YAML, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            slices = data.get('slices', [])
        else:
            slices = []
        
        # Filtrar slices del usuario actual
        usuario_actual = getattr(user, 'username', '')
        slices_usuario = [s for s in slices if s.get('usuario') == usuario_actual]
        
        if not slices_usuario:
            from shared.ui_helpers import show_info
            show_info("No tienes slices")
            pause()
            return
        
        print(f"\n{Colors.CYAN}  Seleccione slice:{Colors.ENDC}")
        for i, s in enumerate(slices_usuario, 1):
            nombre = s.get('nombre', s.get('nombre_slice', 'Sin nombre'))
            print(f"  {i}. {nombre}")
        
        print(f"  0. Cancelar")
        
        choice = input(f"\n{Colors.CYAN}  Opción: {Colors.ENDC}").strip()
        
        if choice == '0':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(slices_usuario):
                slice_seleccionado = slices_usuario[idx]
                
                print_header(user)
                nombre = slice_seleccionado.get('nombre', slice_seleccionado.get('nombre_slice', 'Sin nombre'))
                print(Colors.BOLD + f"\n  SLICE: {nombre}" + Colors.ENDC)
                print("  " + "="*50)
                
                print(f"\n{Colors.YELLOW}  Información General:{Colors.ENDC}")
                print(f"  • ID: {slice_seleccionado.get('id', 'local')}")
                print(f"  • Topología: {slice_seleccionado.get('topologia', 'N/A')}")
                print(f"  • Estado: {slice_seleccionado.get('estado', 'activo')}")
                print(f"CPU por VM: {s.vms[0].cpu if s.vms else 'N/A'}")
                print(f"Memoria por VM: {s.vms[0].memory if s.vms else 'N/A'} MB")
                print(f"Disco por VM: {s.vms[0].disk if s.vms else 'N/A'} GB")
                
                vms = slice_seleccionado.get('vms', [])
                if vms:
                    print(f"\n{Colors.YELLOW}  Máquinas Virtuales ({len(vms)}):{Colors.ENDC}")
                    for vm in vms:
                        nombre_vm = vm.get('nombre', vm.get('tipo', 'VM'))
                        print(f"\n  {Colors.CYAN}• {nombre_vm}{Colors.ENDC}")
                        print(f"    Tipo: {vm.get('tipo', 'N/A')}")
                        print(f"    Flavor: {vm.get('flavor', 'N/A')}")
                        print(f"    IP: {vm.get('ip', 'N/A')}")
                        print(f"    VNC: {vm.get('puerto_vnc', 'N/A')}")
                        print(f"    Estado: {vm.get('estado', 'activo')}")
                else:
                    print(f"\n{Colors.YELLOW}  No hay VMs asociadas{Colors.ENDC}")
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


def _editar_slice(auth_manager):
    """Llama a la función de edición de slices desde slice_editor.py"""
    try:
        from roles.cliente.slice_editor import editar_slice
        editar_slice(auth_manager)
    except ImportError as e:
        print(f"\nError importando editor: {e}")
    except Exception as e:
        print(f"\nError al editar slice: {e}")


def _eliminar_slice(auth_manager, slice_manager):
    """
    Eliminar un slice del usuario
    
    Args:
        auth_manager: Gestor de autenticación
        slice_manager: Gestor de slices
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
        # Obtener slices del usuario usando SliceManager
        usuario_actual_email = getattr(auth_manager.current_user, 'email', '')
        usuario_actual_username = getattr(auth_manager.current_user, 'username', '')
        
        # Obtener todos los slices del SliceManager
        all_slices = slice_manager.get_slices()
        
        # Filtrar slices del usuario actual (usando email o username)
        slices_usuario = []
        for s in all_slices:
            if (s.owner == usuario_actual_email or 
                s.owner == usuario_actual_username or
                (hasattr(s, 'usuario') and s.usuario == usuario_actual_username)):
                slices_usuario.append(s)

        if not slices_usuario:
            from shared.ui_helpers import show_info
            show_info("No tienes slices para eliminar")
            pause()
            return

        print(f"\n{Colors.YELLOW}  Seleccione slice a eliminar:{Colors.ENDC}")
        for i, s in enumerate(slices_usuario, 1):
            print(f"  {i}. {s.name}")

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
                print(f"  '{slice_seleccionado.name}' y todas sus VMs")

                if confirm_action(f"¿Confirmar eliminación?"):
                    print(f"\n{Colors.CYAN}⏳ Eliminando slice...{Colors.ENDC}")
                    # Eliminar slice usando SliceManager
                    if slice_manager.delete_slice(slice_seleccionado.id):
                        show_success("Slice eliminado exitosamente")
                    else:
                        show_error("No se pudo eliminar el slice")
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

def ver_mis_slices_y_detalles(auth_manager, slice_manager):
    from shared.ui_helpers import print_header, pause
    from shared.colors import Colors
    user = auth_manager.current_user
    user_email = getattr(user, 'email', None) or getattr(user, 'username', None)
    user_username = getattr(user, 'username', None) or getattr(user, 'email', None)
    print_header(user)
    print(Colors.BOLD + "\n  MIS SLICES" + Colors.ENDC)
    # Cargar mapa de datos extra desde JSON (salida_internet y conexion_remota por VM)
    db_slices_map = {}
    try:
        import json, os
        db_path = os.path.join(os.getcwd(), 'base_de_datos.json')
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f) or {}
            for item in db.get('slices', []):
                sid = item.get('id') or item.get('slice_id')
                if sid:
                    db_slices_map[str(sid)] = {
                        'salida_internet': item.get('salida_internet', 'no'),
                        'vms': item.get('vms', [])
                    }
    except Exception:
        db_slices_map = {}

    all_slices = slice_manager.get_slices()
    def es_mi_slice(s):
        if isinstance(s, dict):
            slice_user = s.get('usuario') or s.get('owner') or s.get('user')
            return slice_user == user_email or slice_user == user_username
        else:
            slice_owner = (getattr(s, 'owner', None) or 
                          getattr(s, 'usuario', None) or 
                          getattr(s, 'user', None))
            return slice_owner == user_email or slice_owner == user_username
    slices = [s for s in slice_manager.get_slices() if es_mi_slice(s)]
    if not slices:
        print("\n  No tienes slices creados")
        pause()
        return
    # Mostrar tabla
    print("\n{:<7} {:<25} {:<40} {:<13} {:<10}".format("N°", "Nombre de slice", "Topologias-VMs", "Internet", "Estado"))
    print("-"*100)
    def clean_topo_name(val):
        # Convert enums or other types to string, then clean
        val_str = str(val)
        if '.' in val_str:
            val_str = val_str.split('.')[-1]
        return val_str.capitalize()

    def get_all_topologies(s):
        # Returns a list of all topology names for a slice
        topo_raw = getattr(s, 'topologia', None) or getattr(s, 'topology', None) or ''
        if hasattr(s, 'topology_segments') and getattr(s, 'topology_segments', None):
            return [clean_topo_name(seg.type.value) if hasattr(seg.type, 'value') else clean_topo_name(str(seg.type)) for seg in s.topology_segments]
        elif isinstance(topo_raw, str) and '+' in topo_raw:
            return [clean_topo_name(segment.split('-')[0]) for segment in topo_raw.split('+')]
        elif isinstance(topo_raw, str) and '-' in topo_raw:
            return [clean_topo_name(topo_raw.split('-')[0])]
        elif topo_raw:
            return [clean_topo_name(topo_raw)]
        else:
            return []

    for i, s in enumerate(slices, 1):
        topologia_literal = getattr(s, 'topologia', None) or getattr(s, 'topology', None) or ''
        estado = getattr(s, 'status', None) or getattr(s, 'estado', 'activo')
        nombre = getattr(s, 'name', None) or getattr(s, 'nombre', '')
        vms = getattr(s, 'vms', None) or []
        topovms = f"{topologia_literal} ({len(vms)} VMs)"
        sid = getattr(s, 'id', None) or getattr(s, 'slice_id', None) or ''
        internet = db_slices_map.get(str(sid), {}).get('salida_internet', 'no')
        print("{:<7} {:<25} {:<40} {:<13} {:<10}".format(i, nombre, topovms, internet, estado))
    # Selección de slice
    print("\nSeleccione slice (1, 2, 3, ...) para ver más detalles o 0 para salir:", end=" ")
    sel = input().strip()
    if not sel.isdigit() or int(sel) == 0:
        return
    idx = int(sel) - 1
    if idx < 0 or idx >= len(slices):
        print(Colors.RED + "Selección inválida." + Colors.ENDC)
        pause()
        return
    s = slices[idx]
    nombre = getattr(s, 'name', None) or getattr(s, 'nombre', '')
    topo = ', '.join(get_all_topologies(s))
    print("\n" + Colors.BOLD + f"DETALLES DEL SLICE: {nombre}" + Colors.ENDC)
    print(f"Topologías: {topo}")
    print("-"*60)
    # Mostrar si el slice tiene salida a Internet
    sid = getattr(s, 'id', None) or getattr(s, 'slice_id', None) or ''
    internet = db_slices_map.get(str(sid), {}).get('salida_internet', 'no')
    print(f"Salida a Internet: {internet}")
    vms = getattr(s, 'vms', None) or []
    # VMs del JSON para enriquecer datos (conexion_remota)
    vms_db = db_slices_map.get(str(sid), {}).get('vms', [])
    for i, vm in enumerate(vms, 1):
        # Obtener imagen
        imagen = getattr(vm, 'imagen', None) or vm.get('imagen', 'cirros-0.5.1-x86_64-disk.img') if isinstance(vm, dict) else 'cirros-0.5.1-x86_64-disk.img'
        # Obtener conexion_remota
        if isinstance(vm, dict):
            conexion_remota = vm.get('conexion_remota', 'no')
        else:
            conexion_remota = 'no'
            if 0 <= (i - 1) < len(vms_db):
                conexion_remota = vms_db[i - 1].get('conexion_remota', 'no')
        print(f"VM {i} ({imagen}):")
        # Mostrar solo campos relevantes
        campos = ['nombre', 'flavor', 'cpu', 'memory', 'disk', 'imagen']
        for k in campos:
            val = getattr(vm, k, None) if not isinstance(vm, dict) else vm.get(k, None)
            if val is not None and k != 'imagen':
                print(f"   {k}: {val}")
        print(f"   conexion_remota: {conexion_remota}")
        print("-")
    pause()
    # Volver a mostrar la lista de slices en vez de salir al menú principal
    return ver_mis_slices_y_detalles(auth_manager, slice_manager)
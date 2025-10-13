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
        print("  1. Ver slice")
        print("  2. Crear Slice")
        print("  3. Eliminar Slice")
        print("  4. Servicio de Monitoreo")
        print(Colors.RED + "\n  0. Cerrar Sesión" + Colors.ENDC)

        choice = input("\nSeleccione opción: ")

        if choice == '1':
            _submenu_ver_slice_admin(auth_manager, slice_manager)
        elif choice == '2':
            # Crear slice como admin usando el mismo flujo y formato que el cliente
            try:
                builder = SliceBuilder(auth_manager.current_user)
                nombre, topologia, vms_data, salida_internet = builder.start()
                if nombre and topologia and vms_data:
                    print(f"{Colors.CYAN}Guardando slice localmente...{Colors.ENDC}")
                    import json, os
                    dbfile = 'base_de_datos.json'
                    if os.path.exists(dbfile):
                        with open(dbfile, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    else:
                        data = []
                    # id_slice incremental
                    if data:
                        ids = [int(s.get('id_slice')) for s in data if str(s.get('id_slice')).isdigit()]
                        new_id = str(max(ids) + 1) if ids else "1"
                    else:
                        new_id = "1"
                    cantidad_vms = str(len(vms_data))
                    vlans_separadas = str(len(data) + 1)
                    topologia_nombre = topologia.split('-')[0] if '-' in topologia else topologia
                    topologia_obj = {
                        "nombre": topologia_nombre,
                        "cantidad_vms": cantidad_vms,
                        "internet": salida_internet,
                        "vms": []
                    }
                    for vm in vms_data:
                        topologia_obj["vms"].append({
                            "nombre": vm.get("nombre", ""),
                            "cores": str(vm.get("cpu", 1)),
                            "ram": f"{vm.get('memory', 512)}M",
                            "almacenamiento": f"{vm.get('disk', 1)}G",
                            "puerto_vnc": "",
                            "image": vm.get("imagen", ""),
                            "conexiones_vlans": "",
                            "acceso": vm.get("conexion_remota", "no"),
                            "server": ""
                        })
                    admin_email = auth_manager.get_current_user_email()
                    new_slice = {
                        "id_slice": new_id,
                        "cantidad_vms": cantidad_vms,
                        "vlans_separadas": vlans_separadas,
                        "vlans_usadas": "",
                        "vncs_separadas": "",
                        "conexión_topologias": "",
                        "topologias": [topologia_obj],
                        "owner": admin_email
                    }
                    data.append(new_slice)
                    with open(dbfile, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"{Colors.GREEN}Slice '{nombre}' creado exitosamente{Colors.ENDC}")
                    print(f"  • ID: {new_id}")
                    print(f"  • Nombre: {nombre}")
                    print(f"  • Topología: {topologia}")
                    print(f"  • VMs: {len(vms_data)}")
                    pause()
            except Exception as e:
                from shared.ui_helpers import show_error
                show_error(f"Error inesperado: {str(e)}")
            return
        elif choice == '3':
            _eliminar_todos_los_slices_admin(slice_manager)
        elif choice == '4':
            _servicio_monitoreo()
        elif choice == '0':
            _cerrar_sesion(auth_manager, auth_service)
            break
        else:
            print(f"\n{Colors.RED}  ❌ Opción inválida{Colors.ENDC}")
            pause()

def _submenu_ver_slice_admin(auth_manager, slice_manager):
    from shared.ui_helpers import pause
    while True:
        print("\n  1. Ver slices de Clientes")
        print("  2. Ver mis slices")
        print("  0. Volver")
        op = input("Seleccione opción: ").strip()
        if op == '1':
            _ver_slices_clientes(slice_manager, auth_manager)
        elif op == '2':
            _ver_mis_slices_admin(auth_manager, slice_manager)
        elif op == '0':
            return
        else:
            print("Opción inválida"); pause()

def _ver_slices_clientes(slice_manager, auth_manager):
    """Ver solo slices de clientes (NO del admin actual)"""
    from shared.ui_helpers import print_header, pause
    from shared.colors import Colors
    
    print_header(None)
    print(Colors.BOLD + "\n  SLICES DE CLIENTES" + Colors.ENDC)
    print("  " + "="*50)
    
    slices = slice_manager.get_slices()

    # Cargar mapa desde base_de_datos.json para salida_internet y conexion_remota
    db_slices_map = {}
    try:
        import json, os
        db_path = os.path.join(os.getcwd(), 'base_de_datos.json')
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f) or []
            for item in db if isinstance(db, list) else db.get('slices', []):
                sid = item.get('id') or item.get('slice_id')
                if sid is not None:
                    db_slices_map[str(sid)] = {
                        'salida_internet': item.get('salida_internet', 'no'),
                        'vms': item.get('vms', [])
                    }
    except Exception:
        db_slices_map = {}
    
    # Obtener email del admin actual
    admin_email = auth_manager.get_current_user_email()
    
    # Solo mostrar slices que NO sean del admin actual
    clientes = []
    for s in slices:
        slice_owner = getattr(s, 'owner', getattr(s, 'usuario', ''))
        # Excluir slices del admin actual
        if slice_owner.lower() != admin_email.lower():
            clientes.append(s)
    
    if not clientes:
        print(f"\n{Colors.YELLOW}  No hay slices de clientes{Colors.ENDC}")
        pause()
        return
    
    print(f"\n{Colors.GREEN}  Total de slices de clientes: {len(clientes)}{Colors.ENDC}\n")
    
    # Mostrar tabla (incluye Internet)
    print(f"{Colors.CYAN}{'N°':<4} {'Nombre del Slice':<25} {'Usuario/Email':<35} {'Estado':<10} {'Internet':<8}{Colors.ENDC}")
    print("-" * 83)
    
    for i, s in enumerate(clientes, 1):
        nombre = getattr(s, 'name', getattr(s, 'nombre', 'Sin nombre'))[:24]
        usuario = getattr(s, 'owner', getattr(s, 'usuario', 'N/A'))[:34]
        estado = getattr(s, 'status', getattr(s, 'estado', 'activo'))[:9]
        sid = getattr(s, 'id', getattr(s, 'slice_id', ''))
        internet = db_slices_map.get(str(sid), {}).get('salida_internet', 'no')
        print(f"{i:<4} {nombre:<25} {usuario:<35} {estado:<10} {internet:<8}")
    
    print("\nSeleccione el número de un slice para ver detalles, o 0 para volver:", end=" ")
    sel = input().strip()
    
    if not sel.isdigit() or int(sel) == 0:
        return
    
    idx = int(sel) - 1
    if idx < 0 or idx >= len(clientes):
        print(f"{Colors.RED}Selección inválida.{Colors.ENDC}")
        pause()
        return
    
    s = clientes[idx]

    # Helper para topologías
    def clean_topo_name(val):
        val_str = str(val)
        if '.' in val_str:
            val_str = val_str.split('.')[-1]
        return val_str.capitalize()
    def get_all_topologies(slice_obj):
        topo_raw = getattr(slice_obj, 'topologia', None) or getattr(slice_obj, 'topology', None) or ''
        if hasattr(slice_obj, 'topology_segments') and getattr(slice_obj, 'topology_segments', None):
            return [clean_topo_name(getattr(seg.type, 'value', str(seg.type))) for seg in slice_obj.topology_segments]
        elif isinstance(topo_raw, str) and '+' in topo_raw:
            return [clean_topo_name(segment.split('-')[0]) for segment in topo_raw.split('+')]
        elif isinstance(topo_raw, str) and '-' in topo_raw:
            return [clean_topo_name(topo_raw.split('-')[0])]
        elif topo_raw:
            return [clean_topo_name(topo_raw)]
        else:
            return []

    # Mostrar detalles del slice seleccionado
    print("\n" + Colors.BOLD + f"DETALLES DEL SLICE: {getattr(s, 'name', getattr(s, 'nombre', ''))}" + Colors.ENDC)
    print(f"Usuario/Email: {getattr(s, 'owner', getattr(s, 'usuario', 'N/A'))}")
    estado = getattr(s, 'status', getattr(s, 'estado', 'activo'))
    sid = getattr(s, 'id', getattr(s, 'slice_id', ''))
    internet = db_slices_map.get(str(sid), {}).get('salida_internet', 'no')
    print(f"Topologías: {', '.join(get_all_topologies(s))}")
    print(f"Estado: {estado}")
    print(f"Salida a internet: {internet}")
    
    vms = getattr(s, 'vms', [])
    vms_db = db_slices_map.get(str(sid), {}).get('vms', [])
    print(f"VMs: {len(vms)}")
    
    for i, vm in enumerate(vms, 1):
        print(f"  VM {i}:")
        campos = ['nombre', 'flavor', 'cpu', 'memory', 'disk', 'imagen']
        for k in campos:
            val = getattr(vm, k, None) if not isinstance(vm, dict) else vm.get(k, None)
            if val is not None:
                print(f"    {k}: {val}")
        if isinstance(vm, dict):
            conexion = vm.get('conexion_remota', 'no')
        else:
            conexion = 'no'
            if 0 <= (i - 1) < len(vms_db):
                conexion = vms_db[i - 1].get('conexion_remota', 'no')
        print(f"    conexion_remota: {conexion}")
    
    pause()
    return

def _eliminar_todos_los_slices_admin(slice_manager):
    """
    Eliminar cualquier slice del sistema (Admin puede eliminar todos)
    Muestra todos los slices con el email del usuario propietario
    
    Args:
        slice_manager: Gestor de slices
    """
    from shared.ui_helpers import print_header, pause, confirm_action, show_success, show_error
    from shared.colors import Colors
    
    print_header(None)
    print(Colors.BOLD + "\n  ELIMINAR SLICE (ADMIN)" + Colors.ENDC)
    print("  " + "="*70)
    
    # Obtener todos los slices
    slices = slice_manager.get_slices()
    
    if not slices:
        show_error("No hay slices en el sistema para eliminar")
        pause()
        return
    
    print(f"\n{Colors.YELLOW}  Seleccione slice a eliminar:{Colors.ENDC}")
    print(f"{Colors.CYAN}{'N°':<4} {'Nombre del Slice':<25} {'Usuario/Email':<35}{Colors.ENDC}")
    print("-" * 64)
    
    for i, s in enumerate(slices, 1):
        nombre = getattr(s, 'name', getattr(s, 'nombre', 'Sin nombre'))[:24]
        usuario = getattr(s, 'owner', getattr(s, 'usuario', 'N/A'))[:34]
        print(f"{i:<4} {nombre:<25} {usuario:<35}")
    
    print(f"\n  0. Cancelar")
    
    choice = input(f"\n{Colors.CYAN}  Opción: {Colors.ENDC}").strip()
    
    if choice == '0':
        print(f"\n{Colors.YELLOW}  Operación cancelada{Colors.ENDC}")
        pause()
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(slices):
            slice_seleccionado = slices[idx]
            slice_nombre = getattr(slice_seleccionado, 'name', getattr(slice_seleccionado, 'nombre', 'Sin nombre'))
            slice_usuario = getattr(slice_seleccionado, 'owner', getattr(slice_seleccionado, 'usuario', 'N/A'))
            
            print(f"\n{Colors.RED}  ⚠️  ADVERTENCIA (ADMIN):{Colors.ENDC}")
            print(f"  Esta acción eliminará permanentemente el slice")
            print(f"  '{slice_nombre}' del usuario '{slice_usuario}'")
            print(f"  y todas sus VMs asociadas")
            
            if confirm_action(f"¿Confirmar eliminación?"):
                print(f"\n{Colors.CYAN}⏳ Eliminando slice...{Colors.ENDC}")
                # Eliminar slice usando SliceManager
                if slice_manager.delete_slice(slice_seleccionado.id):
                    show_success("Slice eliminado exitosamente por Admin")
                else:
                    show_error("No se pudo eliminar el slice")
            else:
                print(f"\n{Colors.YELLOW}  Eliminación cancelada{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}  ❌ Opción inválida{Colors.ENDC}")
    
    except ValueError:
        print(f"\n{Colors.RED}  ❌ Debe ingresar un número{Colors.ENDC}")
    except Exception as e:
        show_error(f"Error: {str(e)}")
    
    pause()

def _ver_mis_slices_admin(auth_manager, slice_manager):
    """Ver solo los slices creados por el admin actual"""
    from shared.ui_helpers import print_header, pause
    from shared.colors import Colors
    
    print_header(auth_manager.current_user)
    print(Colors.BOLD + "\n  MIS SLICES (ADMIN)" + Colors.ENDC)
    print("  " + "="*50)
    
    slices = slice_manager.get_slices()

    # Cargar mapa desde base_de_datos.json para salida_internet y conexion_remota
    db_slices_map = {}
    try:
        import json, os
        db_path = os.path.join(os.getcwd(), 'base_de_datos.json')
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f) or []
            for item in db if isinstance(db, list) else db.get('slices', []):
                sid = item.get('id') or item.get('slice_id')
                if sid is not None:
                    db_slices_map[str(sid)] = {
                        'salida_internet': item.get('salida_internet', 'no'),
                        'vms': item.get('vms', [])
                    }
    except Exception:
        db_slices_map = {}
    
    # Obtener email del admin actual
    admin_email = auth_manager.get_current_user_email()
    
    # Solo mostrar slices del admin actual
    slices_admin = []
    for s in slices:
        slice_owner = getattr(s, 'owner', getattr(s, 'usuario', ''))
        if slice_owner.lower() == admin_email.lower():
            slices_admin.append(s)
    
    if not slices_admin:
        print(f"\n{Colors.YELLOW}  No tienes slices como admin{Colors.ENDC}")
        pause()
        return
    
    print(f"\n{Colors.GREEN}  Total de mis slices: {len(slices_admin)}{Colors.ENDC}\n")
    
    # Mostrar tabla (incluye Internet)
    print(f"{Colors.CYAN}{'N°':<4} {'Nombre del Slice':<25} {'Estado':<10} {'Internet':<8}{Colors.ENDC}")
    print("-" * 48)
    
    for i, s in enumerate(slices_admin, 1):
        nombre = getattr(s, 'nombre', getattr(s, 'name', 'Sin nombre'))[:24]
        estado = getattr(s, 'status', getattr(s, 'estado', 'activo'))[:9]
        sid = getattr(s, 'id_slice', getattr(s, 'id', getattr(s, 'slice_id', '')))
        internet = db_slices_map.get(str(sid), {}).get('salida_internet', 'no')
        print(f"{i:<4} {nombre:<25} {estado:<10} {internet:<8}")
    
    print("\nSeleccione el número de un slice para ver detalles, o 0 para volver:", end=" ")
    sel = input().strip()
    
    if not sel.isdigit() or int(sel) == 0:
        return
    
    idx = int(sel) - 1
    if idx < 0 or idx >= len(slices_admin):
        print(f"{Colors.RED}Selección inválida.{Colors.ENDC}")
        pause()
        return
    
    s = slices_admin[idx]

    # Helper topologías
    def clean_topo_name(val):
        val_str = str(val)
        if '.' in val_str:
            val_str = val_str.split('.')[-1]
        return val_str.capitalize()
    def get_all_topologies(slice_obj):
        topo_raw = getattr(slice_obj, 'topologia', None) or getattr(slice_obj, 'topology', None) or ''
        if hasattr(slice_obj, 'topology_segments') and getattr(slice_obj, 'topology_segments', None):
            return [clean_topo_name(getattr(seg.type, 'value', str(seg.type))) for seg in slice_obj.topology_segments]
        elif isinstance(topo_raw, str) and '+' in topo_raw:
            return [clean_topo_name(segment.split('-')[0]) for segment in topo_raw.split('+')]
        elif isinstance(topo_raw, str) and '-' in topo_raw:
            return [clean_topo_name(topo_raw.split('-')[0])]
        elif topo_raw:
            return [clean_topo_name(topo_raw)]
        else:
            return []

    # Mostrar detalles del slice seleccionado
    print("\n" + Colors.BOLD + f"DETALLES DEL SLICE: {getattr(s, 'name', getattr(s, 'nombre', ''))}" + Colors.ENDC)
    estado = getattr(s, 'status', getattr(s, 'estado', 'activo'))
    sid = getattr(s, 'id', getattr(s, 'slice_id', ''))
    internet = db_slices_map.get(str(sid), {}).get('salida_internet', 'no')
    print(f"Topologías: {', '.join(get_all_topologies(s))}")
    print(f"Estado: {estado}")
    print(f"Salida a internet: {internet}")
    
    vms = getattr(s, 'vms', [])
    print(f"VMs: {len(vms)}")
    
    # Obtener vms_db para el slice seleccionado (si existe en el mapa)
    sid = getattr(s, 'id_slice', getattr(s, 'id', getattr(s, 'slice_id', '')))
    vms_db = db_slices_map.get(str(sid), {}).get('vms', [])
    for i, vm in enumerate(vms, 1):
        print(f"  VM {i}:")
        campos = ['nombre', 'flavor', 'cpu', 'memory', 'disk', 'imagen']
        for k in campos:
            val = getattr(vm, k, None) if not isinstance(vm, dict) else vm.get(k, None)
            if val is not None:
                print(f"    {k}: {val}")
        if isinstance(vm, dict):
            conexion = vm.get('conexion_remota', 'no')
        else:
            conexion = 'no'
            if 0 <= (i - 1) < len(vms_db):
                conexion = vms_db[i - 1].get('conexion_remota', 'no')
        print(f"    conexion_remota: {conexion}")
    
    pause()
    return
def _servicio_monitoreo():
    """Solicita credenciales de Grafana vía API y muestra la respuesta"""
    import requests
    import json
    print("\n" + Colors.CYAN + "SERVICIO DE MONITOREO" + Colors.ENDC)
    print("  " + "="*50)
    # Obtener token JWT y email del usuario desde el contexto de autenticación
    from inspect import currentframe
    frame = currentframe()
    while frame:
        if 'auth_manager' in frame.f_locals:
            auth_manager = frame.f_locals['auth_manager']
            break
        frame = frame.f_back
    else:
        auth_manager = None
    token = None
    email = None
    if auth_manager:
        if hasattr(auth_manager, 'token'):
            token = auth_manager.token
        elif hasattr(auth_manager, 'get_api_token'):
            token = auth_manager.get_api_token()
        if hasattr(auth_manager, 'get_current_user_email'):
            email = auth_manager.get_current_user_email()
    if not token:
        print(f"{Colors.RED}No se pudo obtener el token JWT de autenticación.{Colors.ENDC}")
        input("\nPresiona Enter para continuar..."); return
    url = "https://localhost:8443/monitoring/send-credentials"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {"message": "Solicitud de credenciales de Grafana"}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
        if response.ok:
            # Mostrar solo mensaje amigable
            print(f"\n{Colors.GREEN}Las credenciales de Grafana han sido enviadas exitosamente a {email}.{Colors.ENDC}")
            print(f"{Colors.BLUE}La contraseña ha sido enviada por correo electrónico por seguridad{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Error: {response.text}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Error al contactar la API de monitoreo: {e}{Colors.ENDC}")
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
        # Leer todos los slices desde base_de_datos.json
        import json, os
        BASE_JSON = os.path.join(os.path.dirname(__file__), '..', '..', 'base_de_datos.json')
        if os.path.exists(BASE_JSON):
            with open(BASE_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f) or []
            slices = data if isinstance(data, list) else data.get('slices', [])
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
            # DESHABILITADO: Crear slice en API
            # try:
            #     print(f"\n{Colors.CYAN}⏳ Creando slice en la API...{Colors.ENDC}")
            #     resultado = slice_api.create_slice(nombre, topologia, vms_data)
            #     if resultado:
            #         from shared.ui_helpers import show_success
            #         vlan = resultado.get('vlan', 'N/A')
            #         slice_id = resultado.get('id', 'N/A')
            #         show_success(f"Slice creado exitosamente")
            #         print(f"\n{Colors.GREEN}  Detalles del Slice:{Colors.ENDC}")
            #         print(f"  • ID: {slice_id}")
            #         print(f"  • VLAN: {vlan}")
            #         print(f"  • Nombre: {nombre}")
            #         print(f"  • Topología: {topologia}")
            #         print(f"  • VMs: {len(vms_data)}")
            #     else:
            #         raise Exception("API no respondió correctamente")
            # except Exception:
            #     # Ocultar logs de error de API, solo mostrar mensaje de guardado local
            
            # Trabajar solo con archivos locales
            vlan = 'local'
            slice_id = 'local'
            print(f"{Colors.CYAN}📁 Guardando slice localmente...{Colors.ENDC}")
            
            # Guardar slice y VMs en archivos SIEMPRE (solo JSON)
            try:
                from shared.data_store import guardar_slice, guardar_vms
                # Guardar slice primero para obtener el id y vlan reales
                user_email = getattr(auth_manager.current_user, 'email', None)
                user_owner = user_email if user_email else getattr(auth_manager.current_user, 'username', '')
                slice_obj = {
                    'id': slice_id,
                    'nombre': nombre,
                    'usuario': user_owner,
                    'vlan': vlan,
                    'topologia': topologia,
                    'vms': vms_data
                }
                guardar_slice(slice_obj)

                # Leer cuántas VMs existen ya en vms.json para calcular puerto_vnc
                import json, os
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
                    ip = f"10.7.1.{num_vm+1}"
                    puerto_vnc = 5900 + total_vms + num_vm
                    vm_dict = dict(vm)
                    vm_dict['usuario'] = getattr(auth_manager.current_user, 'username', '')
                    vm_dict['nombre'] = f"vm{num_vm}"
                    vm_dict['ip'] = ip
                    vm_dict['puerto_vnc'] = puerto_vnc
                    vms_guardar.append(vm_dict)

                guardar_vms(vms_guardar)
                print(f"{Colors.OKGREEN}✔ Slice y VMs guardados correctamente en base_de_datos.json y vms.json{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}  [WARN] No se pudo guardar en base_de_datos.json o vms.json: {e}{Colors.ENDC}")
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
        # Leer todos los slices (de admin y usuarios) desde base_de_datos.json
        import json, os
        BASE_JSON = os.path.join(os.path.dirname(__file__), '..', '..', 'base_de_datos.json')
        if os.path.exists(BASE_JSON):
            with open(BASE_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f) or []
            slices = data if isinstance(data, list) else data.get('slices', [])
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
            print(f"  {i}. {nombre}  |  Usuario: {usuario}")

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
                    # Guardar la lista actualizada en base_de_datos.json
                    with open(BASE_JSON, 'w', encoding='utf-8') as f:
                        json.dump(slices, f, indent=2, ensure_ascii=False)
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
    
    try:
        print(f"\n{Colors.CYAN}⏳ Cargando slices...{Colors.ENDC}")
        # Leer todos los slices desde base_de_datos.json
        import json, os
        BASE_JSON = os.path.join(os.path.dirname(__file__), '..', '..', 'base_de_datos.json')
        if os.path.exists(BASE_JSON):
            with open(BASE_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f) or []
            slices = data if isinstance(data, list) else data.get('slices', [])
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
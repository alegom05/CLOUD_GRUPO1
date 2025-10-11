"""
Constructor interactivo de slices paso a paso
"""

from shared.ui_helpers import print_header, pause, show_success, show_error, show_info, confirm_action
from shared.colors import Colors
from shared.services.flavor_service import select_flavor, get_flavor_specs
from typing import List, Dict, Tuple


class SliceBuilder:
    """Constructor interactivo de slices"""
    
    def __init__(self, user):
        self.user = user
        self.nombre_slice = ""
        self.vms = []  # Lista de VMs: {"nombre": "vm1", "flavor": "small", ...}
        self.enlaces = []  # Lista de tuplas: (vm_origen, vm_destino)
        self.topologias = []  # Lista de topologías: {"tipo": "lineal", "vms": [0, 1, 2]}
        self.vlan = None  # Se asignará automáticamente
    
    def start(self) -> Tuple[str, str, List[Dict]]:
        """
        Inicia el proceso de creación de slice
        
        Returns:
            (nombre_slice, topologia_str, vms_data)
        """
        print_header(self.user)
        print(Colors.BOLD + "\n  CONSTRUCTOR DE SLICE" + Colors.ENDC)
        print("  " + "="*50)
        
        # Paso 1: Nombre del slice
        self.nombre_slice = self._solicitar_nombre()
        if self.nombre_slice is None:
            return None, None, None
        
        while True:
            print_header(self.user)
            print(Colors.BOLD + f"\n  SLICE: {self.nombre_slice}" + Colors.ENDC)
            print("  " + "="*50)
            
            # Mostrar resumen actual
            self._mostrar_resumen()
            
            # Menú de opciones
            print(Colors.YELLOW + "\n  Opciones:" + Colors.ENDC)
            print("  1. Agregar Topologías Definidas")
            print("  2. Agregar Topologías Mixtas")
            print("  3. Ver Resumen")
            print(Colors.GREEN + "  4. Finalizar y Crear Slice" + Colors.ENDC)
            print(Colors.RED + "  0. Cancelar" + Colors.ENDC)
            
            choice = input("\n  Seleccione opción: ")
            
            if choice == '1':
                self._agregar_topologia()
            elif choice == '2':
                self._agregar_nodos()
            elif choice == '3':
                self._mostrar_resumen_detallado()
            elif choice == '4':
                if self._validar_configuracion():
                    return self._generar_datos_slice()
                else:
                    show_error("Configuración incompleta")
                    pause()
            elif choice == '0':
                if confirm_action("¿Cancelar creación del slice?"):
                    return None, None, None
        
    def _solicitar_nombre(self) -> str:
        """Solicita el nombre del slice. Permite cancelar con '0'."""
        while True:
            nombre = input("\n  Nombre del slice (máx 20 caracteres, 0 para cancelar): ").strip()
            if nombre == '0':
                print("\nOperación cancelada. Regresando al menú principal...")
                return None
            if not nombre:
                show_error("El nombre no puede estar vacío")
                continue
            if len(nombre) > 20:
                show_error("El nombre debe tener máximo 20 caracteres")
                continue
            return nombre
    
    def _agregar_nodos(self):
        """Agregar VMs al slice"""
        print_header(self.user)
        print(Colors.BOLD + "\n  AGREGAR NODOS (VMs)" + Colors.ENDC)
        print("  " + "="*50)
        
        # Preguntar si quiere agregar una topología completa o VMs individuales
        print("\n  ¿Cómo desea agregar VMs?")
        print("  1. Agregar VMs individuales")
        print("  2. Agregar topología completa (configura VMs automáticamente)")
        print("  3. Agregar enlaces") # Validación, mínimo 1 VM

        
        modo = input("\n  Seleccione (0 para cancelar): ")
        if modo == '0':
            print("\nOperación cancelada. Regresando al menú principal...")
            return
        if modo == '2':
            self._agregar_topologia_con_vms()
        if modo == '3':
            self._agregar_enlaces()
        else:
            self._agregar_vms_individuales()

    def _agregar_topologia(self):
        """Agregar topología"""
        print_header(self.user)
        print(Colors.BOLD + "\n  AGREGAR NODOS (VMs)" + Colors.ENDC)
        print("  " + "="*50)
        
        # Preguntar si quiere agregar una topología completa o VMs individuales
        print("\n  ¿Cómo desea agregar VMs?")
        print("  1. Agregar topología completa (configura VMs por separado)")
        
        modo = input("\n  Seleccione (0 para cancelar): ")
        if modo == '0':
            print("\nOperación cancelada. Regresando al menú principal...")
            return
        if modo == '1':
            self._agregar_topologia_con_vms()
        else:
            self._agregar_vms_individuales()
    
    def _agregar_vms_individuales(self):
        """Agregar VMs una por una"""
        while True:
            num_vm = len(self.vms) + 1
            print(f"\n  VM {num_vm}:")
            
            # Seleccionar flavor
            flavor = select_flavor()
            specs = get_flavor_specs(flavor)
            
            vm_data = {
                "nombre": f"vm{num_vm}",
                "flavor": flavor,
                "cpu": specs['cpu'],
                "memory": specs['memory'],
                "disk": specs['disk']
            }
            
            self.vms.append(vm_data)
            show_success(f"VM{num_vm} agregada ({flavor})")
            
            if not confirm_action("¿Agregar otra VM?"):
                break
    
    def _agregar_topologia_con_vms(self):
        """Agregar una topología completa con sus VMs"""
        print("\n  Topologías disponibles:")
        print("  1. Lineal (mínimo 2 VMs)")
        print("  2. Anillo (mínimo 3 VMs)")
        print("  3. Árbol (mínimo 3 VMs)")
        print("  4. Malla (mínimo 3 VMs)")
        print("  5. Bus (mínimo 2 VMs)")

        topo_choice = input("\n  Seleccione topología (0 para cancelar): ")
        if topo_choice == '0':
            print("\nOperación cancelada. Regresando al menú principal...")
            return

        topo_tipos = {
            '1': ('lineal', 2),
            '2': ('anillo', 3),
            '3': ('arbol', 3),
            '4': ('malla', 3),
            '5': ('bus', 2)
        }

        topo_tipo, min_vms = topo_tipos.get(topo_choice, ('lineal', 2))

        while True:
            try:
                num_vms_input = input(f"\n  Número de VMs para {topo_tipo} (mínimo {min_vms}, 0 para cancelar): ")
                if num_vms_input == '0':
                    print("\nOperación cancelada. Regresando al menú principal...")
                    return
                num_vms = int(num_vms_input)
                if num_vms < min_vms:
                    show_error(f"La topología {topo_tipo} requiere al menos {min_vms} VMs.")
                else:
                    break
            except ValueError:
                show_error("Debe ingresar un número válido.")

        # Crear VMs con distintos flavors
        inicio_vm = len(self.vms) + 1
        vms_indices = []

        for i in range(num_vms):
            num_vm = inicio_vm + i
            print(f"\n  Seleccionando flavor para la VM {num_vm}:")
            
            # Solicitar flavor para cada VM de manera individual
            flavor = select_flavor()
            specs = get_flavor_specs(flavor)

            vm_data = {
                "nombre": f"vm{num_vm}",
                "flavor": flavor,
                "cpu": specs['cpu'],
                "memory": specs['memory'],
                "disk": specs['disk']
            }
            self.vms.append(vm_data)
            vms_indices.append(len(self.vms) - 1)

            show_success(f"VM{num_vm} agregada ({flavor})")

        # Guardar topología
        self.topologias.append({
            "tipo": topo_tipo,
            "vms": vms_indices,
            "num_vms": num_vms
        })

        # Crear enlaces automáticamente según la topología
        self._crear_enlaces_automaticos(topo_tipo, vms_indices)

        show_success(f"Topología {topo_tipo} con {num_vms} VMs agregada")


    
    def _crear_enlaces_automaticos(self, tipo: str, vms_indices: List[int]):
        """Crea enlaces automáticos según el tipo de topología"""
        if tipo == 'lineal':
            for i in range(len(vms_indices) - 1):
                self.enlaces.append((vms_indices[i], vms_indices[i + 1]))
        
        elif tipo == 'anillo':
            for i in range(len(vms_indices)):
                next_idx = (i + 1) % len(vms_indices)
                self.enlaces.append((vms_indices[i], vms_indices[next_idx]))
        
        elif tipo == 'arbol':
            for i in range(1, len(vms_indices)):
                parent = (i - 1) // 2
                self.enlaces.append((vms_indices[parent], vms_indices[i]))
        
        elif tipo == 'malla':
            for i in range(len(vms_indices)):
                for j in range(i + 1, len(vms_indices)):
                    self.enlaces.append((vms_indices[i], vms_indices[j]))
        
        elif tipo == 'bus':
            # En bus, todas se conectan a la primera (que actúa como bus)
            bus_idx = vms_indices[0]
            for i in range(1, len(vms_indices)):
                self.enlaces.append((bus_idx, vms_indices[i]))
    
    def _agregar_enlaces(self):
        """Agregar enlaces manualmente entre VMs"""
        if len(self.vms) < 2:
            show_error("Necesita al menos 2 VMs para crear enlaces")
            pause()
            return
        
        print_header(self.user)
        print(Colors.BOLD + "\n  AGREGAR ENLACES" + Colors.ENDC)
        print("  " + "="*50)
        
        # Mostrar VMs disponibles
        print("\n  VMs disponibles:")
        for i, vm in enumerate(self.vms, 1):
            print(f"  {i}. {vm['nombre']} ({vm['flavor']})")
        
        # Mostrar enlaces existentes
        if self.enlaces:
            print("\n  Enlaces existentes:")
            for origen, destino in self.enlaces:
                print(f"  • {self.vms[origen]['nombre']} ↔ {self.vms[destino]['nombre']}")
        
        while True:
            print()
            origen = input("  VM origen (número, 0 para cancelar, o Enter para terminar): ")
            if origen == '0':
                print("\nOperación cancelada. Regresando al menú principal...")
                return
            if not origen:
                break
            destino = input("  VM destino (0 para cancelar): ")
            if destino == '0':
                print("\nOperación cancelada. Regresando al menú principal...")
                return
            
            try:
                origen_num = int(origen)
                destino_num = int(destino)
                
                # Convertir de números basados en 1 a índices basados en 0
                origen_idx = origen_num - 1
                destino_idx = destino_num - 1
                
                if 0 <= origen_idx < len(self.vms) and 0 <= destino_idx < len(self.vms):
                    if origen_idx != destino_idx:
                        # Evitar duplicados
                        enlace = (min(origen_idx, destino_idx), max(origen_idx, destino_idx))
                        if enlace not in self.enlaces:
                            self.enlaces.append(enlace)
                            show_success(f"Enlace creado: {self.vms[origen_idx]['nombre']} ↔ {self.vms[destino_idx]['nombre']}")
                        else:
                            show_error("Este enlace ya existe")
                    else:
                        show_error("No puede enlazar una VM consigo misma")
                else:
                    show_error("Índices de VM inválidos")
            except ValueError:
                show_error("Debe ingresar números")
    
    def _mostrar_resumen(self):
        """Muestra resumen compacto"""
        print(f"\n  VMs: {len(self.vms)} | Enlaces: {len(self.enlaces)} | Topologías: {len(self.topologias)}")
    
    def _mostrar_resumen_detallado(self):
        """Muestra resumen completo de la configuración"""
        print_header(self.user)
        print(Colors.BOLD + f"\n  RESUMEN: {self.nombre_slice}" + Colors.ENDC)
        print("  " + "="*50)
        
        # VMs
        print(Colors.YELLOW + "\n  Máquinas Virtuales:" + Colors.ENDC)
        for i, vm in enumerate(self.vms, 1):
            print(f"  {i}. {vm['nombre']} - Flavor: {vm['flavor']} ({vm['cpu']} CPU, {vm['memory']}MB RAM, {vm['disk']}GB)")
        
        # Enlaces
        print(Colors.YELLOW + "\n  Enlaces:" + Colors.ENDC)
        if self.enlaces:
            for origen, destino in self.enlaces:
                print(f"  • {self.vms[origen]['nombre']} ↔ {self.vms[destino]['nombre']}")
        else:
            print("  (Sin enlaces)")
        
        # Topologías
        print(Colors.YELLOW + "\n  Topologías:" + Colors.ENDC)
        if self.topologias:
            for topo in self.topologias:
                vms_nombres = [self.vms[idx]['nombre'] for idx in topo['vms']]
                print(f"  • {topo['tipo']}: {', '.join(vms_nombres)}")
        else:
            print("  (Manual/Sin topología definida)")
        
        pause()
    
    def _validar_configuracion(self) -> bool:
        """Valida que la configuración sea válida"""
        if len(self.vms) == 0:
            show_error("Debe agregar al menos una VM")
            return False
        
        return True
    
    def _generar_datos_slice(self) -> Tuple[str, str, List[Dict]]:
        """
        Genera los datos finales para enviar a la API
        
        Returns:
            (nombre_slice, topologia_str, vms_data)
        """
        # Generar string de topología
        if self.topologias:
            topo_parts = []
            for topo in self.topologias:
                topo_parts.append(f"{topo['tipo']}-{topo['num_vms']}VMS")
            topologia_str = "+".join(topo_parts)
        else:
            topologia_str = f"manual-{len(self.vms)}VMS"
        
        # Preparar datos de VMs (se calcularán IPs y puertos en el backend)
        vms_data = []
        for vm in self.vms:
            vms_data.append({
                "nombre": vm['nombre'],
                "flavor": vm['flavor'],
                "cpu": vm['cpu'],
                "memory": vm['memory'],
                "disk": vm['disk']
            })
        
        return self.nombre_slice, topologia_str, vms_data
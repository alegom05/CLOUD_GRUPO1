import os
import sys
from slice_manager.manager import SliceManager
from slice_manager.models import SliceCreate


def main():
    manager = SliceManager()
    
    while True:
        # Mostrar el men
        print("\n---- PUCP Cloud Orchestrator ----")
        print("   Bienvenidos al Menú Principal")
        print("---------------------------------")
        print("1. Registrar Usuario")
        print("2. Crear Slice")
        print("3. Listar Slices")
        print("4. Eliminar Slice")
        print("5. Ver Detalles de un Slice")
        print("6. Salir")
        option = input("Seleccione una opción: ")
        
        # Opción de registro
        if option == '1':
            register_user()
        
        # Crear slice
        elif option == '2':
            create_slice_menu(manager)
        
        # Listar slices
        elif option == '3':
            list_slices_menu(manager)
        
        # Eliminar slice
        elif option == '4':
            delete_slice_menu(manager)
        
        # Ver detalles de slice
        elif option == '5':
            view_slice_details(manager)
        
        # Opción de salida
        elif option == '6':
            print("¡Hasta luego!")
            break
        
        # Opción inválida
        else:
            print("Opción inválida. Intente de nuevo.")

def register_user():
    """Función para registrar un nuevo usuario"""
    print("\n--- Registro de Usuario ---")
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")
    # Aquí puedes agregar la lógica para almacenar el usuario
    print(f"Usuario {username} registrado exitosamente.")

def create_slice_menu(manager):
    """Menú para crear un slice"""
    print("\n--- Crear Nuevo Slice ---")
    name = input("Nombre del slice: ")
    
    print("\nTopologías disponibles:")
    print("1. Lineal")
    print("2. Anillo")
    print("3. Arbol")
    print("4. Malla")
    print("5. Bus")
    
    topology_choice = input("Seleccione topología (1-5): ")
    topologies = {
        '1': 'lineal',
        '2': 'anillo',
        '3': 'arbol',
        '4': 'malla',
        '5': 'bus'
    }
    
    topology = topologies.get(topology_choice, 'linear')
    
    num_vms = int(input("Número de VMs (default 3): ") or "3")
    cpu = int(input("CPUs por VM (default 1): ") or "1")
    memory = int(input("Memoria en MB por VM (default 1024): ") or "1024")
    disk = int(input("Disco en GB por VM (default 10): ") or "10")

    print(f"\nCreando slice '{name}' con topología {topology}...")

    from slice_manager.models import SliceCreate, TopologyType
    import asyncio

    # Convertir la topología a TopologyType
    topology_enum = TopologyType(topology)

    slice_data = SliceCreate(
        name=name,
        topology=topology_enum,
        num_vms=num_vms,
        cpu=cpu,
        memory=memory,
        disk=disk
    )

    # Llamada asíncrona
    slice = asyncio.run(manager.create_slice(slice_data))

    print(f"✅ Slice creado exitosamente!")
    print(f"ID: {slice.id}")
    print(f"VMs creadas: {len(slice.vms)}")


def list_slices_menu(manager):
    """Menú para listar slices"""
    print("\n--- Lista de Slices ---")
    slices = manager.get_slices()
    
    if not slices:
        print("No hay slices creados.")
        return
    
    print(f"\nTotal de slices: {len(slices)}")
    print("-" * 60)
    
    for i, slice in enumerate(slices, 1):
        print(f"{i}. ID: {slice.id}")
        print(f"   Nombre: {slice.name}")
        print(f"   Topología: {slice.topology.value}")
        print(f"   VMs: {len(slice.vms)}")
        print(f"   Propietario: {slice.owner}")
        print(f"   Creado: {slice.created_at}")
        print("-" * 60)

def delete_slice_menu(manager):
    """Menú para eliminar un slice"""
    print("\n--- Eliminar Slice ---")
    
    # Primero mostrar los slices disponibles
    slices = manager.get_slices()
    if not slices:
        print("No hay slices para eliminar.")
        return
    
    print("\nSlices disponibles:")
    for i, slice in enumerate(slices, 1):
        print(f"{i}. {slice.id} - {slice.name}")
    
    slice_num = input("\nIngrese el número del slice a eliminar (0 para cancelar): ")
    
    if slice_num == '0':
        print("Operación cancelada.")
        return
    
    try:
        index = int(slice_num) - 1
        if 0 <= index < len(slices):
            slice_to_delete = slices[index]
            confirm = input(f"¿Está seguro de eliminar '{slice_to_delete.name}'? (s/n): ")
            
            if confirm.lower() == 's':
                manager.delete_slice(slice_to_delete.id)
                print(f"✅ Slice {slice_to_delete.name} eliminado exitosamente.")
            else:
                print("Operación cancelada.")
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada inválida.")

def view_slice_details(manager):
    """Ver detalles de un slice específico"""
    print("\n--- Detalles del Slice ---")
    
    slices = manager.get_slices()
    if not slices:
        print("No hay slices creados.")
        return
    
    print("\nSlices disponibles:")
    for i, slice in enumerate(slices, 1):
        print(f"{i}. {slice.id} - {slice.name}")
    
    slice_num = input("\nIngrese el número del slice (0 para volver): ")
    
    if slice_num == '0':
        return
    
    try:
        index = int(slice_num) - 1
        if 0 <= index < len(slices):
            slice = slices[index]
            print(f"\n=== Detalles del Slice: {slice.name} ===")
            print(f"ID: {slice.id}")
            print(f"Topología: {slice.topology.value}")
            print(f"Propietario: {slice.owner}")
            print(f"Creado: {slice.created_at}")
            print(f"\nMáquinas Virtuales ({len(slice.vms)}):")
            
            for vm in slice.vms:
                print(f"  - {vm.name}")
                print(f"    CPU: {vm.cpu} cores")
                print(f"    Memoria: {vm.memory} MB")
                print(f"    Disco: {vm.disk} GB")
                print()
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada inválida.")
    

def draw_topology(topology_type: str, num_vms: int):
    """Visualización clara y profesional de topologías"""
    
    print(f"\n{'='*40}")
    print(f" TOPOLOGÍA: {topology_type.upper()}")
    print(f" VMs: {num_vms}")
    print(f"{'='*40}\n")
    
    if topology_type == 'lineal':
        # Cadena lineal
        print("  ", end="")
        for i in range(num_vms):
            print(f"[VM{i}]", end="")
            if i < num_vms - 1:
                print("──", end="")
        print("\n")
        
    elif topology_type == 'anillo':
        # Representación de anillo
        if num_vms <= 6:
            # Dibujo ASCII para pocos nodos
            if num_vms == 3:
                print("      ╔═VM0═╗")
                print("      ║     ║")
                print("    VM2═════VM1")
                
            elif num_vms == 4:
                print("    VM0═════VM1")
                print("     ║       ║")
                print("     ║       ║")
                print("    VM3═════VM2")
                
            elif num_vms == 5:
                print("        VM0")
                print("       ╱   ╲")
                print("     VM4   VM1")
                print("      │     │")
                print("     VM3───VM2")
                
            elif num_vms == 6:
                print("     VM0───VM1")
                print("      │     │")
                print("    VM5     VM2")
                print("      │     │")
                print("     VM4───VM3")
        else:
            # Representación textual para muchos nodos
            print("  ┌─────────────────────────┐")
            print("  │    Anillo Circular      │")
            print("  └─────────────────────────┘")
            print("\n  Conexiones:")
            for i in range(min(5, num_vms)):
                next_node = (i + 1) % num_vms
                print(f"    VM{i} ↔ VM{next_node}")
            if num_vms > 5:
                print(f"    ... ({num_vms - 5} conexiones más)")
                
    elif topology_type == 'arbol':
        print("         [VM0]")
        print("        /  |  \\")
        if num_vms >= 3:
            print("    VM1  VM2  VM3")
        if num_vms >= 7:
            print("    / \\   |   / \\")
            print("  VM4 VM5 VM6 VM7")
            
    elif topology_type == 'malla':
        if num_vms <= 4:
            print("  Todos ↔ Todos")
            print("  ┌───────────┐")
            for i in range(num_vms):
                print(f"  │    VM{i}    │")
            print("  └───────────┘")
        else:
            print(f"  Malla completa: {num_vms} nodos")
            print(f"  Enlaces totales: {num_vms*(num_vms-1)//2}")
            
    elif topology_type == 'bus':
        print("  ═══════[BUS CENTRAL]═══════")
        for i in range(num_vms):
            print(f"           │")
            print(f"         [VM{i}]")
            
    # Información adicional
    print(f"\n  Estado: Activo")
    print(f"  Conexiones: Establecidas")

def view_slice_details(manager):
    """Ver detalles de un slice con visualización"""
    print("\n--- Detalles del Slice ---")
    
    slices = manager.get_slices()
    if not slices:
        print("No hay slices creados.")
        return
    
    print("\nSlices disponibles:")
    for i, slice in enumerate(slices, 1):
        print(f"{i}. {slice.id} - {slice.name}")
    
    slice_num = input("\nIngrese el número del slice (0 para volver): ")
    
    if slice_num == '0':
        return
    
    try:
        index = int(slice_num) - 1
        if 0 <= index < len(slices):
            slice = slices[index]
            print(f"\n=== Detalles del Slice: {slice.name} ===")
            print(f"ID: {slice.id}")
            print(f"Topología: {slice.topology.value}")
            print(f"Propietario: {slice.owner}")
            print(f"Creado: {slice.created_at}")
            
            # Dibujar la topología
            draw_topology(slice.topology.value, len(slice.vms))
            
            print(f"\nMáquinas Virtuales ({len(slice.vms)}):")
            for vm in slice.vms:
                print(f"  - {vm.name}")
                print(f"    CPU: {vm.cpu} cores")
                print(f"    Memoria: {vm.memory} MB")
                print(f"    Disco: {vm.disk} GB")
                print()
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada inválida.")

# Ejecutar la función principal
if __name__ == "__main__":
    main()
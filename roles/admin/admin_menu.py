
def admin_menu(auth_manager, slice_manager):
    """Menú para ADMIN (área específica)"""
    while True:
        print_header(auth_manager.current_user)
        print(Colors.BOLD + "\n  MENÚ ADMINISTRADOR" + Colors.ENDC)
        print("  " + "="*40)
        
        print(Colors.YELLOW + "\n  Gestión de Recursos (Mi Área):" + Colors.ENDC)
        print("  1. Ver Slices de MI ÁREA")
        print("  2. Crear Nuevo Slice")
        print("  3. Eliminar Slice de MI ÁREA")
        print("  4. Gestionar Recursos de MI ÁREA")
        print("  5. Gestionar Topologías")
        
        print(Colors.YELLOW + "\n  Monitoreo y Seguridad:" + Colors.ENDC)
        print("  6. Monitorear MI ÁREA")
        print("  7. Ver Logs de MI ÁREA")
        print("  8. Configurar Seguridad de MI ÁREA")
        print("  9. Ver Detalles de un Slice")
        
        print(Colors.YELLOW + "\n  Clusters:" + Colors.ENDC)
        print("  10. Provisionar en MI ÁREA")
        print("  11. Acceder APIs del Sistema")
        
        print(Colors.RED + "\n  0. Cerrar Sesión" + Colors.ENDC)
        
        choice = input("\n  Seleccione opción: ")
        
        if choice == '1':
            view_area_slices(slice_manager, auth_manager.current_user)
        elif choice == '2':
            create_slice_advanced(slice_manager, auth_manager.current_user)
        elif choice == '3':
            delete_area_slice(slice_manager, auth_manager.current_user)
        elif choice == '4':
            manage_area_resources(slice_manager)
        elif choice == '5':
            manage_topologies()
        elif choice == '6':
            monitor_area(slice_manager, auth_manager.current_user)
        elif choice == '7':
            view_area_logs(auth_manager.current_user)
        elif choice == '8':
            configure_area_security()
        elif choice == '9':
            ver_detalles_slice(slice_manager, auth_manager.current_user)
        elif choice == '10':
            provision_area_clusters(auth_manager.current_user)
        elif choice == '11':
            access_apis()
        elif choice == '0':
            auth_manager.logout()
            break
def view_area_slices(slice_manager, user):
    """Ver slices del área (ADMIN)"""
    print_header(user)
    print(Colors.BOLD + "\n  SLICES DE MI ÁREA" + Colors.ENDC)
    print("\n  [Mostrando slices del área asignada]")
    slices = slice_manager.get_slices()
    for s in slices:
        print(f"  • {s.name} - {s.topology.value}")
    input("\n  Presione Enter para continuar...")



def manage_area_resources(slice_manager):
    """Gestionar recursos del área"""
    print_header()
    print(Colors.BOLD + "\n  RECURSOS DE MI ÁREA" + Colors.ENDC)
    print("\n  • Servidores: 4")
    print("  • CPU: 128 cores")
    print("  • RAM: 256 GB")
    input("\n  Presione Enter para continuar...")

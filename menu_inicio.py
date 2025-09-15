def main():
     
    print("***************************************")
    print("*                                     *")
    print("*   Bienvenido al Proyecto de Redes   *")
    print("*              CLOUD                  *")
    print("*                                     *")
    print("***************************************")
    
    usuario = input("Usuario: ")
    contraseña = input("Contraseña: ")
    
    print("\n***************************************")
    print("*                                     *")
    print("*    Bienvenido al Menú Principal     *")
    print("*                                     *")
    print("***************************************")
    
    while True:
        print("\n1. Slices")
        print("2. Estado de Recursos")
        print("3. Usuarios")
        print("4. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            print("Has seleccionado Slices.")
        elif opcion == "2":
            print("Has seleccionado Estado de Recursos.")
        elif opcion == "3":
            print("Has seleccionado Usuarios.")
        elif opcion == "4":
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Por favor selecciona una opción válida.")

if __name__ == "__main__":
    main()
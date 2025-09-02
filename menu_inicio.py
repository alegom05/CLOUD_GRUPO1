def main():
    while True:
        # Mostrar el menú 
        print("\n--- Menú Principal ---")
        print("1. Registrarse")
        print("2. Salir")
        option = input("Seleccione una opción: ") # leer la opcion del usuario

        # Opción de registro
        if option == '1':
            register_user()  # Llamada a la función de registro (definirla abajo)

        # Opción de salida
        elif option == '2':
            print("¡Hasta luego!")
            break  # Sale del bucle y termina el programa

        # Opción inválida
        else:
            print("Opción inválida. Intente de nuevo.")

def register_user():
    """Función para registrar un nuevo usuario"""
    print("\n--- Registro de Usuario ---")
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese su contraseña: ")
    
    # Aquí puedes agregar la lógica para almacenar el usuario (en una base de datos o archivo)
    print(f"Usuario {username} registrado exitosamente.")

# Ejecutar la función principal
if __name__ == "__main__":
    main()
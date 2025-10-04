"""
Gestor de autenticación de usuarios
"""

from .services.auth_api_service import AuthAPIService
from .slice_manager.models import User, UserRole


class AuthManager:
    """Gestor de autenticación con API externa"""
    
    def __init__(self):
        """Inicializa el gestor de autenticación"""
        self.api_service = AuthAPIService()
        self.current_user = None
    
    def _map_role(self, api_role: str) -> UserRole:
        """
        Mapea roles de la API a roles del sistema
        
        Args:
            api_role: Rol desde la API (admin/cliente/usuario_avanzado)
            
        Returns:
            UserRole correspondiente
        """
        role_mapping = {
            'admin': UserRole.ADMIN,
            'cliente': UserRole.CLIENTE,
            'usuario_avanzado': UserRole.CLIENTE  # Mapear a CLIENTE por ahora
        }
        return role_mapping.get(api_role.lower(), UserRole.CLIENTE)
    
    def login(self, username: str, password: str) -> bool:
        """
        Autenticar usuario contra API externa
        
        Args:
            username: Email del usuario
            password: Contraseña
            
        Returns:
            True si la autenticación fue exitosa
        """
        # Intentar login con API externa
        if self.api_service.login(username, password):
            user_data = self.api_service.get_user_data()
            
            if user_data:
                # Crear objeto User con datos de la API
                role = self._map_role(user_data.get('rol', 'cliente'))
                
                self.current_user = User(
                    username=user_data.get('correo'),
                    password="",  # No necesitamos el password hasheado
                    role=role
                )
                
                # Agregar datos adicionales
                self.current_user.nombre_completo = user_data.get('nombre_completo', '')
                self.current_user.id = user_data.get('id')
                
                return True
        
        return False
    
    def logout(self):
        """Cerrar sesión del usuario actual"""
        self.api_service.logout()
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.current_user is not None
    
    def verify_session(self) -> bool:
        """Verifica que la sesión siga siendo válida"""
        return self.api_service.verify_token()
    
    def has_role(self, role: UserRole) -> bool:
        """
        Verifica si el usuario actual tiene un rol específico
        
        Args:
            role: Rol a verificar
            
        Returns:
            True si el usuario tiene ese rol
        """
        if not self.is_authenticated():
            return False
        return self.current_user.role == role
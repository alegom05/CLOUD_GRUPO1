from slice_manager.models import User, UserRole
import hashlib

class AuthManager:
    def __init__(self):
        # Usuarios hardcodeados (en producción usarían base de datos)
        self.users = {
            "superadmin": User("superadmin", self._hash_password("123"), UserRole.SUPERADMIN),
            "admin": User("admin", self._hash_password("123"), UserRole.ADMIN),
            "cliente": User("cliente", self._hash_password("123"), UserRole.CLIENTE)
        }
        self.current_user = None
    
    def _hash_password(self, password):
        """Simple hash para demo (usar bcrypt en producción)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        """Autenticar usuario"""
        if username in self.users:
            user = self.users[username]
            if user.password == self._hash_password(password):
                self.current_user = user
                return True
        return False
    
    def logout(self):
        self.current_user = None
    
    def has_permission(self, action):
        """Verificar permisos según rol"""
        if not self.current_user:
            return False
        
        permissions = {
            UserRole.SUPERADMIN: [
                "manage_users", "access_all", "manage_resources", 
                "monitor_all", "access_logs", "manage_security",
                "provision_all_clusters", "manage_topology",
                "configure_firewall", "access_all_resources"
            ],
            UserRole.ADMIN: [
                "access_all", "manage_resources", "monitor_all",
                "access_logs", "manage_security", "provision_area",
                "manage_topology", "configure_firewall", 
                "access_area_resources"
            ],
            UserRole.CLIENTE: [
                "access_ui", "deploy_slices", "access_apis",
                "deploy_clusters", "access_assigned_resources",
                "view_own_logs"
            ]
        }
        
        return action in permissions.get(self.current_user.role, [])
from slice_manager.models import User, UserRole
import hashlib

class AuthManager:
    def __init__(self):
        # Usuarios hardcodeados según especificación
        self.users = {
            "superadmin": User("superadmin", self._hash_password("superadmin"), UserRole.SUPERADMIN),
            "admin": User("admin", self._hash_password("admin"), UserRole.ADMIN),
            "cliente": User("cliente", self._hash_password("cliente"), UserRole.CLIENTE)
        }
        self.current_user = None
    
    def _hash_password(self, password):
        """Simple hash para demo"""
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
        return True
    
    def has_permission(self, action):
        """Verificar permisos según rol basado en las tablas"""
        if not self.current_user:
            return False
        
        permissions = {
            UserRole.SUPERADMIN: [
                "manage_users",
                "access_all_system", 
                "manage_global_resources",
                "monitor_all",
                "access_all_logs",
                "manage_global_security",
                "provision_all_clusters",
                "access_ui",
                "manage_slices",
                "manage_topologies",
                "access_apis",
                "deploy_all_clusters",
                "configure_firewall",
                "access_all_resources",
                "access_test_plans"
            ],
            UserRole.ADMIN: [
                "access_all_system",
                "manage_global_resources",
                "monitor_all", 
                "access_all_logs",
                "manage_global_security",
                "provision_area_clusters",
                "access_ui",
                "manage_slices",
                "manage_topologies",
                "access_apis",
                "deploy_all_clusters",
                "configure_firewall",
                "access_area_resources",
                "access_test_plans_role"
            ],
            UserRole.CLIENTE: [
                "access_ui",
                "manage_slices",
                "access_apis",
                "deploy_all_clusters",
                "access_assigned_resources",
                "view_own_logs"
            ]
        }
        
        user_permissions = permissions.get(self.current_user.role, [])
        return action in user_permissions
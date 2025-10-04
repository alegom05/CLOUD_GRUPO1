"""
Servicio para comunicación con la API de autenticación externa
"""

import requests
import os
from typing import Optional, Dict
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class AuthAPIService:
    """Servicio para autenticación contra API externa"""
    
    def __init__(self):
        self.api_url = os.getenv('AUTH_API_URL', 'http://localhost:8080/auth')
        self.token = None
        self.user_data = None
        
        # DEBUG: Mostrar URL que se está usando
        print(f"[DEBUG] API URL configurada: {self.api_url}")
    
    def login(self, correo: str, password: str) -> bool:
        """
        Autenticar contra la API externa
        
        Args:
            correo: Email del usuario
            password: Contraseña
            
        Returns:
            True si el login fue exitoso
        """
        try:
            url = f"{self.api_url}/login"
            payload = {
                "correo": correo,
                "password": password
            }
            
            # DEBUG: Mostrar lo que se está enviando
            print(f"[DEBUG] URL: {url}")
            print(f"[DEBUG] Payload: {payload}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=5
            )
            
            # DEBUG: Mostrar respuesta
            print(f"[DEBUG] Status Code: {response.status_code}")
            print(f"[DEBUG] Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                
                # La API devuelve user_info, no usuario
                self.user_data = data.get('user_info', {})
                
                print(f"[DEBUG] Token recibido: {self.token[:20]}..." if self.token else "[DEBUG] No token")
                print(f"[DEBUG] User data: {self.user_data}")
                
                return True
            
            print(f"[DEBUG] Login falló con status {response.status_code}")
            return False
            
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] No se puede conectar con la API: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Error en login: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_token(self) -> bool:
        """
        Verificar si el token actual es válido
        
        Returns:
            True si el token es válido
        """
        if not self.token:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/verify-token",
                headers={
                    "Authorization": f"Bearer {self.token}"
                },
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"[ERROR] Error verificando token: {e}")
            return False
    
    def get_user_data(self) -> Optional[Dict]:
        """
        Obtiene los datos del usuario autenticado
        
        Returns:
            Diccionario con datos del usuario o None
        """
        return self.user_data
    
    def logout(self):
        """Cerrar sesión"""
        self.token = None
        self.user_data = None
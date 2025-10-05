"""
Servicio para comunicación con la API de slices
"""

import requests
import os
from typing import List, Dict, Optional


class SliceAPIService:
    """Servicio para gestión de slices con API externa"""
    
    def __init__(self, api_url: str, token: str):
        """
        Inicializa el servicio
        
        Args:
            api_url: URL base de la API (ej: http://localhost:8080)
            token: Token JWT de autenticación
        """
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def create_slice(self, nombre: str, topologia: str, vms_data: List[Dict]) -> Optional[Dict]:
        """
        Crear un nuevo slice
        
        Args:
            nombre: Nombre del slice
            topologia: String de topología (ej: "lineal-3VMS" o "arbol-4VMS+anillo-2VMS")
            vms_data: Lista de diccionarios con datos de VMs
            
        Returns:
            Datos del slice creado o None si falla
        """
        try:
            payload = {
                "nombre_slice": nombre,
                "topologia": topologia,
                "vms": vms_data
            }
            
            response = requests.post(
                f"{self.api_url}/slices/create",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"[ERROR] Error al crear slice: {response.status_code}")
                print(f"[ERROR] {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("[ERROR] No se puede conectar con la API de slices")
            return None
        except Exception as e:
            print(f"[ERROR] Error al crear slice: {e}")
            return None
    
    def get_my_slices(self) -> List[Dict]:
        """
        Obtener todos los slices del usuario actual
        
        Returns:
            Lista de slices
        """
        try:
            response = requests.get(
                f"{self.api_url}/slices/my-slices",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('slices', [])
            else:
                print(f"[ERROR] Error al obtener slices: {response.status_code}")
                return []
                
        except requests.exceptions.ConnectionError:
            print("[ERROR] No se puede conectar con la API de slices")
            return []
        except Exception as e:
            print(f"[ERROR] Error al obtener slices: {e}")
            return []
    
    def get_slice_details(self, slice_id: int) -> Optional[Dict]:
        """
        Obtener detalles de un slice específico
        
        Args:
            slice_id: ID del slice
            
        Returns:
            Datos detallados del slice o None
        """
        try:
            response = requests.get(
                f"{self.api_url}/slices/{slice_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[ERROR] Error al obtener detalles: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error al obtener detalles: {e}")
            return None
    
    def delete_slice(self, slice_id: int) -> bool:
        """
        Eliminar un slice
        
        Args:
            slice_id: ID del slice a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            response = requests.delete(
                f"{self.api_url}/slices/{slice_id}",
                headers=self.headers,
                timeout=10
            )
            
            return response.status_code == 200
                
        except Exception as e:
            print(f"[ERROR] Error al eliminar slice: {e}")
            return False
"""
Utilitaires pour la conversion et validation de données
"""
from typing import Union, Optional


def safe_float(value: Union[str, int, float, None]) -> Optional[float]:
    """
    Convertit une valeur en float de manière sécurisée.
    
    Args:
        value: Valeur à convertir (str, int, float, ou None)
        
    Returns:
        float si la conversion réussit, None sinon
    """
    if value is None:
        return None
    
    if isinstance(value, str) and value.strip() == "":
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int(value: Union[str, int, float, None]) -> Optional[int]:
    """
    Convertit une valeur en int de manière sécurisée.
    
    Args:
        value: Valeur à convertir (str, int, float, ou None)
        
    Returns:
        int si la conversion réussit, None sinon
    """
    if value is None:
        return None
    
    if isinstance(value, str) and value.strip() == "":
        return None
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_str(value: Union[str, int, float, None]) -> Optional[str]:
    """
    Convertit une valeur en string de manière sécurisée.
    
    Args:
        value: Valeur à convertir
        
    Returns:
        str si la conversion réussit, None sinon
    """
    if value is None:
        return None
    
    try:
        return str(value).strip()
    except (ValueError, TypeError):
        return None


def safe_bool(value: Union[str, int, bool, None]) -> Optional[bool]:
    """
    Convertit une valeur en bool de manière sécurisée.
    
    Args:
        value: Valeur à convertir
        
    Returns:
        bool si la conversion réussit, None sinon
    """
    if value is None:
        return None
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', '1', 'yes', 'on'):
            return True
        elif value in ('false', '0', 'no', 'off'):
            return False
    
    try:
        return bool(int(value))
    except (ValueError, TypeError):
        return None


def format_currency(amount: float, currency: str = "€") -> str:
    """
    Formate un montant en devise.
    
    Args:
        amount: Montant à formater
        currency: Symbole de la devise
        
    Returns:
        Montant formaté (ex: "12.50€")
    """
    if amount is None:
        return "N/A"
    
    return f"{amount:.2f}{currency}"


def format_percentage(value: float, total: float) -> str:
    """
    Calcule et formate un pourcentage.
    
    Args:
        value: Valeur
        total: Total
        
    Returns:
        Pourcentage formaté (ex: "25.5%")
    """
    if total is None or total == 0:
        return "N/A"
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Tronque une chaîne de caractères.
    
    Args:
        text: Texte à tronquer
        max_length: Longueur maximale
        suffix: Suffixe à ajouter si tronqué
        
    Returns:
        Texte tronqué
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

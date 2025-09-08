from typing import Dict, List

# Configuration des limites d'événements
EVENT_PARTICIPANT_LIMITS: Dict[str, List[int]] = {
    "Lycans": [8, 10],      # [min, max]
    "Among Us": [10, 12],
    "Matriach": [8, 8],
    "Burger Quiz": [5, 9],
    "First Class Trouble": [5, 6],
}
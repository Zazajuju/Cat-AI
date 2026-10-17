import json
import os
from typing import Dict, Any, List

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

COAT_STYLES = [
    "Roux Tigré",
    "Gingembre Caramel",
    "Blanc",
    "Noir",
    "Gris Chartreux",
    "Bleu Russe",
    "Siamois",
    "Chocolat Point",
    "Calico",
    "Écaille de tortue",
    "Tuxedo",
    "Tigré Argenté",
    "Chat Magique Violet",
]

PERSONALITY_PRESETS = [
    "Gourmand, obsédé par les croquettes et le thon, un peu paresseux",
    "Philosophe existentiel qui médite sur le sens de la vie et le curseur de la souris",
    "Chaotique, hyperactif, veut chasser tous les pixels de l'écran",
    "Aristocrate hautain qui juge secrètement l'humain devant son PC",
    "Très affectueux, curieux et doux, adore ronronner et faire la sieste",
    "Agent secret en mission d'infiltration sur la barre des tâches Windows"
]

DEFAULT_CONFIG: Dict[str, Any] = {
    "ollama_url": "http://localhost:11434",
    "ollama_model": "gemma3:1b",
    "cat_scale": 5,            # Multiplicateur de taille pixel art (2 à 8)
    "cat_speed": 1.8,          # Vitesse de marche (0.5 à 5.0)
    "thought_interval": 20,    # Secondes moyennes entre deux pensées IA
    "chat_interval": 40,       # Secondes moyennes entre deux discussions de chats
    "enable_chat_interactions": True,
    "show_cat_names": True,    # Afficher le petit nom au-dessus du chat
    "screen_mode": "all",      # "all" ou index de l'écran ("0", "1", ...)
    "day_night_mode": "auto",  # "auto" (selon heure réelle), "day" (force jour), "night" (force nuit)
    "enable_laser": False,     # Mode laser rouge interactif avec la souris
    "cats": [
        {
            "id": "cat_1",
            "name": "Mochi",
            "coat": "Roux Tigré",
            "personality": "Gourmand, obsédé par les croquettes et le thon, un peu paresseux"
        },
        {
            "id": "cat_2",
            "name": "Lumi",
            "coat": "Blanc",
            "personality": "Philosophe existentiel qui médite sur le sens de la vie et le curseur de la souris"
        },
        {
            "id": "cat_3",
            "name": "Pixel",
            "coat": "Calico",
            "personality": "Chaotique, hyperactif, veut chasser tous les pixels de l'écran"
        }
    ]
}


class ConfigManager:
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.data = {**DEFAULT_CONFIG, **loaded}
                return
            except Exception as e:
                print(f"Erreur de chargement de la configuration: {e}")
        self.data = json.loads(json.dumps(DEFAULT_CONFIG))
        self.save()

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur de sauvegarde de la configuration: {e}")

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()

    @property
    def cats(self) -> List[Dict[str, str]]:
        return self.data.get("cats", [])

import json
import os
import uuid
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

GIFTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifts.json")

# Catalogue de trésors trouvés sur le PC par les chats
GIFT_TEMPLATES = [
    {
        "name": "Pixel Doré Mystérieux",
        "icon": "🌟",
        "rarity": "Légendaire",
        "color": "#ffd700",
        "lore": "Déterré au fond de la Corbeille Windows. Il brille d'une lueur dorée chaleureuse !",
    },
    {
        "name": "Bug Informatique Sauvage",
        "icon": "🐛",
        "rarity": "Rare",
        "color": "#4fc3f7",
        "lore": "Attrapé par la patte entre deux lignes de code. Il frétille encore un peu !",
    },
    {
        "name": "Câble Réseau Mâchouillé",
        "icon": "🔌",
        "rarity": "Commun",
        "color": "#b0bec5",
        "lore": "Idéal pour faire ses griffes et ralentir la connexion Wi-Fi de 2 millisecondes.",
    },
    {
        "name": "Cookie Web au Chocolat",
        "icon": "🍪",
        "rarity": "Commun",
        "color": "#bcaaa4",
        "lore": "Accepté sur un site web obscur. Le chat l'a croqué avant de vous l'apporter.",
    },
    {
        "name": "Vieille Disquette 1.44 Mo",
        "icon": "💾",
        "rarity": "Rare",
        "color": "#81d4fa",
        "lore": "Une relique ancienne du siècle dernier. Elle contient peut-être un poème de chat.",
    },
    {
        "name": "Touche Échap Égarée",
        "icon": "⌨️",
        "rarity": "Rare",
        "color": "#80cbc4",
        "lore": "Détachée discrètement du clavier. Pratique pour fuir les réunions ennuyeuses.",
    },
    {
        "name": "Flocon de Ventilateur GPU",
        "icon": "❄️",
        "rarity": "Commun",
        "color": "#cfd8dc",
        "lore": "Ultra doux et tiède, parfait comme mini-coussin de sieste pour un chat.",
    },
    {
        "name": "Boîte de Thon Virtuel Doré",
        "icon": "🐟",
        "rarity": "Légendaire",
        "color": "#ffb300",
        "lore": "Le Graal absolu de tous les félins de la Terre. Mochi bave rien qu'en la regardant.",
    },
    {
        "name": "Cristal de Mémoire RAM",
        "icon": "💎",
        "rarity": "Épique",
        "color": "#ce93d8",
        "lore": "Contient 8 Go de ronronnements haute fidélité et de souvenirs de siestes.",
    },
    {
        "name": "Pelote de Fibre Optique",
        "icon": "🧶",
        "rarity": "Épique",
        "color": "#ba68c8",
        "lore": "Elle roule à la vitesse de la lumière quand on donne un coup de patte dedans !",
    },
    {
        "name": "Éclair d'Overclocking",
        "icon": "⚡",
        "rarity": "Épique",
        "color": "#ffca28",
        "lore": "Fait courir le chat deux fois plus vite pendant sa folie de minuit.",
    },
    {
        "name": "Couronne de la Barre des Tâches",
        "icon": "👑",
        "rarity": "Légendaire",
        "color": "#ffab00",
        "lore": "Forgée dans les flammes du GPU. Déclare officiellement votre chat Souverain du PC.",
    },
]


class GiftManager:
    """Manages virtual gifts and treasures retrieved by cats on the PC."""

    def __init__(self):
        self.gifts: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        if os.path.exists(GIFTS_FILE):
            try:
                with open(GIFTS_FILE, "r", encoding="utf-8") as f:
                    self.gifts = json.load(f)
                return
            except Exception as e:
                print(f"[Cat AI] Erreur chargement trésors: {e}")
        # Starter gift
        self.gifts = [
            {
                "id": "gift_starter",
                "name": "Pixel Doré Mystérieux",
                "icon": "🌟",
                "rarity": "Légendaire",
                "color": "#ffd700",
                "found_by": "Mochi",
                "found_at": datetime.now().strftime("%d/%m %H:%M"),
                "lore": "Déterré au fond de la Corbeille Windows. Il brille d'une lueur dorée chaleureuse !",
            }
        ]
        self.save()

    def save(self):
        try:
            with open(GIFTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.gifts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Cat AI] Erreur sauvegarde trésors: {e}")

    def get_all_gifts(self) -> List[Dict[str, Any]]:
        return self.gifts

    def get_gifts_for_cat(self, cat_name: str) -> List[Dict[str, Any]]:
        return [g for g in self.gifts if g.get("found_by") == cat_name]

    def create_random_gift(self, finder_cat_name: str) -> Dict[str, Any]:
        template = random.choice(GIFT_TEMPLATES)
        gift = {
            "id": f"gift_{uuid.uuid4().hex[:6]}",
            "name": template["name"],
            "icon": template["icon"],
            "rarity": template["rarity"],
            "color": template["color"],
            "found_by": finder_cat_name,
            "found_at": datetime.now().strftime("%d/%m %H:%M"),
            "lore": template["lore"],
        }
        self.gifts.insert(0, gift)
        self.save()
        return gift

import json
import os
import uuid
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

QUESTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quests.json")

# Quêtes disponibles par défaut (catégorisées par type d'action)
DEFAULT_QUEST_TEMPLATES = [
    {
        "template_id": "pet_cats",
        "title": "Câlins & Caresses 🐾",
        "description": "Caresser un chat 3 fois",
        "action_type": "pet",
        "target_count": 3,
        "icon": "✨",
        "reward_xp": 60,
    },
    {
        "template_id": "laser_chase",
        "title": "Chasseur de Laser 🔴",
        "description": "Faire bondir les chats vers le pointeur laser 2 fois",
        "action_type": "laser_jump",
        "target_count": 2,
        "icon": "🔴",
        "reward_xp": 75,
    },
    {
        "template_id": "todo_progress",
        "title": "Maître de la Productivité 📋",
        "description": "Cocher 1 tâche dans la To-Do List",
        "action_type": "todo",
        "target_count": 1,
        "icon": "📋",
        "reward_xp": 100,
    },
    {
        "template_id": "chat_with_cat",
        "title": "Discussion Secrète 💬",
        "description": "Envoyer un message de discussion à un chat",
        "action_type": "chat",
        "target_count": 1,
        "icon": "💬",
        "reward_xp": 50,
    },
    {
        "template_id": "make_jump",
        "title": "Salto & Acrobaties 🦘",
        "description": "Faire sauter un chat en l'air 3 fois",
        "action_type": "jump",
        "target_count": 3,
        "icon": "🦘",
        "reward_xp": 50,
    },
    {
        "template_id": "multi_chat",
        "title": "Réunion Féline 🗣️",
        "description": "Faire discuter deux chats ensemble",
        "action_type": "multi_chat",
        "target_count": 1,
        "icon": "🗣️",
        "reward_xp": 80,
    },
    {
        "template_id": "loaf_mode",
        "title": "Boulangerie Féline 🥖",
        "description": "Mettre un chat en mode pain (loaf)",
        "action_type": "loaf",
        "target_count": 1,
        "icon": "🥖",
        "reward_xp": 40,
    },
    {
        "template_id": "feed_cat",
        "title": "Festin de Croquettes 🥣",
        "description": "Nourrir un chat au distributeur de croquettes",
        "action_type": "feed",
        "target_count": 1,
        "icon": "🥣",
        "reward_xp": 65,
    },
    {
        "template_id": "drink_cat",
        "title": "Oasis Féline 💧",
        "description": "Faire boire un chat à la fontaine d'eau",
        "action_type": "drink",
        "target_count": 1,
        "icon": "💧",
        "reward_xp": 65,
    },
    {
        "template_id": "teach_rule",
        "title": "Éducation & Répliques 🧠",
        "description": "Apprendre une réplique ou poser une question dans le chat",
        "action_type": "chat",
        "target_count": 2,
        "icon": "🧠",
        "reward_xp": 70,
    },
]


class QuestManager:
    """Manages interactive daily quests and player progression."""

    def __init__(self):
        self.data: Dict[str, Any] = {
            "xp": 0,
            "level": 1,
            "active_quests": [],
            "completed_count": 0,
            "last_refresh_date": "",
        }
        self.load()

    def load(self):
        if os.path.exists(QUESTS_FILE):
            try:
                with open(QUESTS_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self._check_daily_refresh()
                return
            except Exception as e:
                print(f"[Cat AI] Erreur chargement quêtes: {e}")
        self._generate_new_daily_quests()
        self.save()

    def save(self):
        try:
            with open(QUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Cat AI] Erreur sauvegarde quêtes: {e}")

    def _check_daily_refresh(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.data.get("last_refresh_date") != today or not self.data.get("active_quests"):
            self._generate_new_daily_quests()
            self.save()

    def _generate_new_daily_quests(self):
        today = datetime.now().strftime("%Y-%m-%d")
        # Sélectionne 3 ou 4 quêtes variées
        chosen = random.sample(DEFAULT_QUEST_TEMPLATES, min(4, len(DEFAULT_QUEST_TEMPLATES)))
        active = []
        for q in chosen:
            active.append({
                "id": f"quest_{uuid.uuid4().hex[:6]}",
                "template_id": q["template_id"],
                "title": q["title"],
                "description": q["description"],
                "action_type": q["action_type"],
                "current_count": 0,
                "target_count": q["target_count"],
                "icon": q["icon"],
                "reward_xp": q["reward_xp"],
                "completed": False,
                "claimed": False,
            })
        self.data["active_quests"] = active
        self.data["last_refresh_date"] = today

    def get_active_quests(self) -> List[Dict[str, Any]]:
        self._check_daily_refresh()
        return self.data.get("active_quests", [])

    def get_player_stats(self) -> Dict[str, int]:
        xp = self.data.get("xp", 0)
        level = max(1, 1 + xp // 150)
        xp_in_level = xp % 150
        return {
            "xp": xp,
            "level": level,
            "xp_in_level": xp_in_level,
            "xp_for_next": 150,
            "completed_count": self.data.get("completed_count", 0),
        }

    def record_action(self, action_type: str, count: int = 1) -> List[Dict[str, Any]]:
        """Records an interaction event and advances matching quests.
        Returns list of newly completed quests if any.
        """
        self._check_daily_refresh()
        just_completed = []
        modified = False

        for q in self.data.get("active_quests", []):
            if not q["completed"] and q["action_type"] == action_type:
                q["current_count"] = min(q["target_count"], q["current_count"] + count)
                modified = True
                if q["current_count"] >= q["target_count"]:
                    q["completed"] = True
                    q["claimed"] = True
                    xp_gain = q.get("reward_xp", 50)
                    self.data["xp"] = self.data.get("xp", 0) + xp_gain
                    self.data["completed_count"] = self.data.get("completed_count", 0) + 1
                    just_completed.append(q)

        if modified:
            self.save()
        return just_completed

    def refresh_quests_manual(self):
        """Force refreshes active daily quests."""
        self._generate_new_daily_quests()
        self.save()

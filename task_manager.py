import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


class TaskManager:
    """Manages persistent to-do tasks per cat with checkboxes."""

    def __init__(self):
        # Structure per cat_id:
        # {
        #   "cat_1": [
        #       {"id": "t1", "text": "...", "done": False, "created_at": "..."},
        #       ...
        #   ]
        # }
        self.tasks_by_cat: Dict[str, List[Dict[str, Any]]] = {}
        self.load()

    def load(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.tasks_by_cat = data
                    return
                elif isinstance(data, list):
                    # Migration from old flat list to cat_1
                    self.tasks_by_cat = {"cat_1": data}
                    self.save()
                    return
            except Exception as e:
                print(f"[Cat AI] Erreur chargement to-do: {e}")
        self.tasks_by_cat = {}

    def save(self):
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks_by_cat, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Cat AI] Erreur sauvegarde to-do: {e}")

    def get_tasks(self, cat_id: Optional[str] = None) -> List[Dict[str, Any]]:
        target_id = cat_id or "cat_1"
        if target_id not in self.tasks_by_cat:
            # Starter tasks for new cats
            self.tasks_by_cat[target_id] = [
                {
                    "id": f"t_{uuid.uuid4().hex[:4]}",
                    "text": "Donner une friandise ou une caresse 🐾",
                    "done": False,
                    "created_at": datetime.now().strftime("%d/%m %H:%M"),
                },
                {
                    "id": f"t_{uuid.uuid4().hex[:4]}",
                    "text": "Faire une pause café ☕",
                    "done": False,
                    "created_at": datetime.now().strftime("%d/%m %H:%M"),
                },
            ]
            self.save()
        return self.tasks_by_cat.get(target_id, [])

    def add_task(self, cat_id_or_text: str, text: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if text is None:
            cat_id = "cat_1"
            task_text = cat_id_or_text.strip()
        else:
            cat_id = cat_id_or_text
            task_text = text.strip()

        if not task_text:
            return None

        if cat_id not in self.tasks_by_cat:
            self.tasks_by_cat[cat_id] = []

        task = {
            "id": f"task_{uuid.uuid4().hex[:6]}",
            "text": task_text,
            "done": False,
            "created_at": datetime.now().strftime("%d/%m %H:%M"),
        }
        self.tasks_by_cat[cat_id].append(task)
        self.save()
        return task

    def set_task_done(self, arg1: str, arg2: Any, arg3: Optional[bool] = None):
        if arg3 is None:
            # Called as set_task_done(task_id, done_bool)
            task_id = arg1
            done = bool(arg2)
            for cid, tasks in self.tasks_by_cat.items():
                for t in tasks:
                    if t["id"] == task_id:
                        t["done"] = done
                        self.save()
                        return
            return

        cat_id = arg1
        task_id = str(arg2)
        done = bool(arg3)
        for t in self.tasks_by_cat.get(cat_id, []):
            if t["id"] == task_id:
                t["done"] = done
                self.save()
                return

    def remove_task(self, cat_id_or_task_id: str, task_id: Optional[str] = None):
        if task_id is None:
            target_id = cat_id_or_task_id
            for cid in list(self.tasks_by_cat.keys()):
                self.tasks_by_cat[cid] = [
                    t for t in self.tasks_by_cat[cid] if t["id"] != target_id
                ]
            self.save()
            return

        cat_id = cat_id_or_task_id
        if cat_id in self.tasks_by_cat:
            self.tasks_by_cat[cat_id] = [
                t for t in self.tasks_by_cat[cat_id] if t["id"] != task_id
            ]
            self.save()

    def clear_completed(self, cat_id: Optional[str] = None):
        if cat_id is None:
            for cid in self.tasks_by_cat:
                self.tasks_by_cat[cid] = [
                    t for t in self.tasks_by_cat[cid] if not t["done"]
                ]
        elif cat_id in self.tasks_by_cat:
            self.tasks_by_cat[cat_id] = [
                t for t in self.tasks_by_cat[cat_id] if not t["done"]
            ]
        self.save()

import sys
import random
from datetime import datetime
from typing import Dict, List, Optional
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QIcon, QCursor

from config import ConfigManager
from memory_manager import MemoryManager
from task_manager import TaskManager
from quest_manager import QuestManager
from gift_manager import GiftManager
from accessory_widget import AccessoryManager
from sprites import SpriteBank
from cat_widget import CatActor, LaserDot
from ollama_worker import SoloThoughtWorker, MultiCatDialogueWorker, UserChatWorker
from settings_dialog import SettingsDialog
from chat_dialog import CatChatBubble


class CatManager(QObject):
    """Coordinates all taskbar pixel cats, persistent memories, to-do tasks, quests, gifts, accessories, Ollama AI workers, and overhead chat bubbles."""

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.config = ConfigManager()
        self.memory = MemoryManager()
        self.tasks = TaskManager()
        self.quests = QuestManager()
        self.gifts = GiftManager()
        self.accessories = AccessoryManager(scale=int(self.config.get("cat_scale", 5)))
        self.accessories.request_call_cat.connect(self.call_cat_to_accessory)
        self.accessories.quest_action_triggered.connect(self.notify_quest_action)
        self.sprite_bank = SpriteBank()

        self.cats: Dict[str, CatActor] = {}
        self.chat_bubbles: Dict[str, CatChatBubble] = {}
        self.active_workers: List[QObject] = []
        self.settings_dlg: Optional[SettingsDialog] = None
        self.dialogue_busy = False

        # Interactive Laser Pointer
        self.laser_dot = LaserDot()
        self.laser_enabled = bool(self.config.get("enable_laser", False))

        # Setup System Tray Icon
        self._setup_tray()

        # 60 FPS physics timer
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self._tick_all_physics)

        # Autonomous treasure hunt timer (every 3 minutes, 25% chance)
        self.treasure_timer = QTimer(self)
        self.treasure_timer.timeout.connect(self._maybe_trigger_autonomous_treasure)
        self.treasure_timer.start(180 * 1000)
        self.physics_timer.start(16)

        # Autonomous solo thought timer
        self.thought_timer = QTimer(self)
        self.thought_timer.timeout.connect(self.trigger_random_solo_thought)

        # Autonomous multi-cat conversation timer
        self.chat_timer = QTimer(self)
        self.chat_timer.timeout.connect(self.trigger_random_multi_chat)

        # Day / Night cycle check timer (every 10s)
        self.day_night_timer = QTimer(self)
        self.day_night_timer.timeout.connect(self._check_day_night_cycle)
        self.day_night_timer.start(10000)

        # Spawn initial cats from config and start timers
        self.sync_cats_with_config()
        self._check_day_night_cycle()

        print("[Cat AI] Le jeu est lance !", flush=True)
        print(f"   -> {len(self.cats)} chats actifs sur la barre des taches.", flush=True)

        # Trigger a friendly greeting thought shortly after launch
        QTimer.singleShot(
            1500,
            lambda: self.trigger_random_solo_thought(
                "Je viens d'arriver sur la barre des tâches Windows !"
            ),
        )

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self.app)
        icon_pix = self.sprite_bank.get_frame("Roux Tigré", "sit", 0, scale=3)
        self.tray.setIcon(QIcon(icon_pix))
        self.tray.setToolTip("Cat AI - Chats Pixel Art (Ollama Gemma 3)")

        menu = QMenu()
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #1e202c;
                color: #f5f6fa;
                border: 1px solid #f28c28;
                padding: 4px;
                font-family: 'Segoe UI';
            }
            QMenu::item { padding: 6px 16px; }
            QMenu::item:selected { background-color: #f28c28; color: #14161f; font-weight: bold; }
            """
        )
        act_cfg = menu.addAction("⚙️ Menu de Configuration")
        act_cfg.triggered.connect(self.open_settings)

        todo_menu = menu.addMenu("📋 To-Do Lists des chats")
        for profile in self.config.cats:
            cid = profile["id"]
            cname = profile.get("name", cid)
            act_t = todo_menu.addAction(f"📋 To-Do de {cname}")
            act_t.triggered.connect(lambda _, c=cid: self.open_todo_for_cat(c))

        act_quests = menu.addAction("🎯 Quêtes & Missions félines")
        act_quests.triggered.connect(self._open_quests_from_tray)

        act_gifts = menu.addAction("🎁 Trésors rapportés du PC")
        act_gifts.triggered.connect(self._open_gifts_from_tray)

        acc_menu = menu.addMenu("🛋️ Mobilier & Accessoires")
        act_add_panier = acc_menu.addAction("🧺 Ajouter un Panier Douillet")
        act_add_panier.triggered.connect(lambda: self._spawn_accessory_with_signal("panier"))
        act_add_cabane = acc_menu.addAction("🏠 Ajouter une Petite Cabane")
        act_add_cabane.triggered.connect(lambda: self._spawn_accessory_with_signal("cabane"))
        act_add_arbre = acc_menu.addAction("🌳 Ajouter un Arbre à Chat")
        act_add_arbre.triggered.connect(lambda: self._spawn_accessory_with_signal("arbre"))
        act_add_food = acc_menu.addAction("🥣 Distributeur de Croquettes")
        act_add_food.triggered.connect(lambda: self._spawn_accessory_with_signal("nourriture"))
        act_add_water = acc_menu.addAction("💧 Fontaine à Eau Fraîche")
        act_add_water.triggered.connect(lambda: self._spawn_accessory_with_signal("eau"))
        acc_menu.addSeparator()
        act_clear_acc = acc_menu.addAction("🧹 Ranger tous les accessoires")
        act_clear_acc.triggered.connect(self.accessories.clear_all)

        act_laser = menu.addAction("🔴 Pointeur Laser (Activer / Couper)")
        act_laser.triggered.connect(lambda: self.toggle_laser())

        act_thought = menu.addAction("💭 Faire penser un chat tout bas (IA)")
        act_thought.triggered.connect(lambda: self.trigger_random_solo_thought("", force_spoken=False))

        act_speak = menu.addAction("💬 Faire parler un chat tout haut (IA)")
        act_speak.triggered.connect(lambda: self.trigger_random_solo_thought("", force_spoken=True))

        act_chat = menu.addAction("🗣️ Faire discuter deux chats (IA)")
        act_chat.triggered.connect(lambda: self.trigger_random_multi_chat())

        menu.addSeparator()
        act_quit = menu.addAction("❌ Quitter")
        act_quit.triggered.connect(lambda: (print("[Cat AI] Quitter demande depuis le System Tray", flush=True), self.quit_app()))

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        # Sur macOS, cliquer sur l'icône de statut ouvre déjà nativement le menu contextuel.
        # Déclencher l'activation synchrone d'une fenêtre sur Trigger pendant le tracking Cocoa du menu
        # provoque un crash dans AppKit. On délègue au menu ou au double-clic sécurisé.
        if sys.platform == "darwin":
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                QTimer.singleShot(100, self.open_settings)
            return

        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.open_settings()

    def _open_todo_from_tray(self):
        if self.cats:
            first_cat_id = next(iter(self.cats.keys()))
            self.open_todo_for_cat(first_cat_id)

    def _open_quests_from_tray(self):
        if self.cats:
            first_cat_id = next(iter(self.cats.keys()))
            self.open_quests_for_cat(first_cat_id)

    def _open_gifts_from_tray(self):
        if self.cats:
            first_cat_id = next(iter(self.cats.keys()))
            self.open_gifts_for_cat(first_cat_id)

    def _update_timers(self):
        thought_sec = max(5, int(self.config.get("thought_interval", 20)))
        chat_sec = max(10, int(self.config.get("chat_interval", 40)))
        self.thought_timer.start(thought_sec * 1000)
        self.chat_timer.start(chat_sec * 1000)

    def sync_cats_with_config(self):
        scale = int(self.config.get("cat_scale", 5))
        speed = float(self.config.get("cat_speed", 1.8))
        screen_mode = str(self.config.get("screen_mode", "all"))
        show_name = bool(self.config.get("show_cat_names", True))
        profiles = self.config.cats

        desired_ids = {p["id"] for p in profiles}

        for cid in list(self.cats.keys()):
            if cid not in desired_ids:
                actor = self.cats.pop(cid)
                actor.cleanup()
                if cid in self.chat_bubbles:
                    b = self.chat_bubbles.pop(cid)
                    b.hide()
                    b.deleteLater()

        for idx, p in enumerate(profiles):
            cid = p["id"]
            if cid in self.cats:
                self.cats[cid].apply_settings(p, scale, speed, screen_mode, show_name)
                if cid in self.chat_bubbles:
                    self.chat_bubbles[cid].cat_name = p["name"]
                    self.chat_bubbles[cid].title_lbl.setText(f"🐾 {p['name']}")
            else:
                actor = CatActor(
                    p,
                    self.sprite_bank,
                    scale=scale,
                    speed=speed,
                    screen_mode=screen_mode,
                    show_name=show_name,
                    spawn_index=idx,
                )
                actor.request_config.connect(self.open_settings)
                actor.request_open_chat.connect(self.toggle_chat_for_cat)
                actor.request_open_todo.connect(self.open_todo_for_cat)
                actor.request_open_quests.connect(self.open_quests_for_cat)
                actor.request_open_gifts.connect(self.open_gifts_for_cat)
                actor.request_hunt_treasure.connect(self.hunt_treasure_for_cat)
                actor.request_solo_thought.connect(lambda cid, ctx: self._on_actor_solo_thought_requested(cid, ctx))
                actor.request_speak_thought.connect(lambda cid: self.trigger_solo_thought_for_cat(cid, "", is_spoken=True))
                actor.request_check_todo.connect(self.trigger_todo_check_for_cat)
                actor.request_multi_chat.connect(self.trigger_multi_chat_with_cat)
                actor.request_toggle_laser.connect(self.toggle_laser)
                actor.request_quit.connect(self.quit_app)
                self.cats[cid] = actor

        self._check_day_night_cycle()
        self._update_timers()

    def _tick_all_physics(self):
        if self.laser_enabled:
            cur_pos = QCursor.pos()
            self.laser_dot.update_position(cur_pos.x(), cur_pos.y())
            if not self.laser_dot.isVisible():
                self.laser_dot.show()
                self.laser_dot.raise_()
            for actor in self.cats.values():
                actor.set_laser_target(cur_pos.x(), cur_pos.y())
        else:
            if self.laser_dot.isVisible():
                self.laser_dot.hide()
            for actor in self.cats.values():
                if actor.laser_target is not None:
                    actor.set_laser_target(None, None)

        for cid, actor in self.cats.items():
            actor.tick_physics()
            self.accessories.check_cat_interaction(actor)

        # Anti-Stacking: répulsion mutuelle douce pour empêcher les chats de se superposer
        # MAIS les chats peuvent se croiser et se passer dessus s'ils vont dans des directions différentes !
        actors = list(self.cats.values())
        if len(actors) > 1:
            scale = int(self.config.get("cat_scale", 5))
            min_sep = max(24.0, 6.0 * scale)
            for i in range(len(actors)):
                for j in range(i + 1, len(actors)):
                    c1 = actors[i]
                    c2 = actors[j]
                    if not c1.is_dragging and not c2.is_dragging:
                        # Si les chats vont dans des directions différentes (l'un vers la gauche, l'autre vers la droite),
                        # ils doivent pouvoir se croiser et se passer dessus librement sans être repoussés en arrière !
                        is_opposite = (c1.facing_left != c2.facing_left) and (
                            c1.state in ("walk", "stalk", "jump") or c2.state in ("walk", "stalk", "jump")
                        )
                        if is_opposite:
                            continue  # Ils se croisent librement sans répulsion !

                        if abs(c1.pos_y - c2.pos_y) < 30:
                            c1_center = c1.pos_x + c1.width() / 2.0
                            c2_center = c2.pos_x + c2.width() / 2.0
                            dist_x = c2_center - c1_center
                            abs_dist = abs(dist_x)
                            if abs_dist < min_sep:
                                overlap = min_sep - abs_dist
                                push = min(1.2, max(0.35, overlap * 0.18))
                                if dist_x >= 0:
                                    c1.pos_x -= push
                                    c2.pos_x += push
                                else:
                                    c1.pos_x += push
                                    c2.pos_x -= push
                                c1._clamp_to_ground()
                                c2._clamp_to_ground()
                                c1.move(int(c1.pos_x), int(c1.pos_y))
                                c2.move(int(c2.pos_x), int(c2.pos_y))

        for cid, actor in self.cats.items():
            if cid in self.chat_bubbles and self.chat_bubbles[cid].isVisible():
                self.chat_bubbles[cid].update_anchor(
                    int(actor.pos_x + actor.width() // 2),
                    int(actor.pos_y),
                )

    def toggle_laser(self, force_state: Optional[bool] = None):
        if force_state is not None:
            self.laser_enabled = force_state
        else:
            self.laser_enabled = not self.laser_enabled

        self.config.data["enable_laser"] = self.laser_enabled
        self.config.save()

        if self.laser_enabled:
            self.notify_quest_action("laser_jump", 1)
            if self.cats:
                first_cat = next(iter(self.cats.values()))
                first_cat.show_speech("🔴 Le laser rouge est allumé ! Visez par ici !", duration_ms=2500, bubble_type="speech")
        else:
            self.laser_dot.hide()
            for actor in self.cats.values():
                actor.set_laser_target(None, None)

    def _check_day_night_cycle(self):
        mode = self.config.get("day_night_mode", "auto")
        if mode == "night":
            is_night = True
        elif mode == "day":
            is_night = False
        else:
            now_hour = datetime.now().hour
            is_night = (now_hour >= 21 or now_hour < 7)

        for actor in self.cats.values():
            actor.set_night_mode(is_night)

    def toggle_chat_for_cat(self, cat_id: str):
        actor = self.cats.get(cat_id)
        if not actor:
            return

        if cat_id in self.chat_bubbles and self.chat_bubbles[cat_id].isVisible():
            self.chat_bubbles[cat_id].close_chat()
            return

        self.open_chat_for_cat(cat_id)

    def open_chat_for_cat(self, cat_id: str, page_index: int = 0):
        actor = self.cats.get(cat_id)
        if not actor:
            return

        actor.bubble.hide()
        actor.in_conversation = True
        actor.set_behavior("sit", 30000)

        if cat_id not in self.chat_bubbles:
            profile = {
                "id": actor.cat_id,
                "name": actor.name,
                "coat": actor.coat,
                "personality": actor.personality,
            }
            bubble = CatChatBubble(
                cat_profile=profile,
                memory_manager=self.memory,
                task_manager=self.tasks,
                quest_manager=self.quests,
                gift_manager=self.gifts,
            )
            bubble.send_user_message.connect(self.handle_user_chat_message)
            bubble.closed_bubble.connect(self._on_chat_bubble_closed)
            bubble.task_done_cheer.connect(self.on_task_done_cheer)
            bubble.request_hunt_treasure.connect(self.hunt_treasure_for_cat)
            self.chat_bubbles[cat_id] = bubble

        self.chat_bubbles[cat_id].open_above(
            int(actor.pos_x + actor.width() // 2),
            int(actor.pos_y),
            page_index=page_index,
        )

    def open_todo_for_cat(self, cat_id: str):
        self.open_chat_for_cat(cat_id, page_index=2)

    def open_quests_for_cat(self, cat_id: str):
        self.open_chat_for_cat(cat_id, page_index=3)

    def open_gifts_for_cat(self, cat_id: str):
        self.open_chat_for_cat(cat_id, page_index=4)

    def _spawn_accessory_with_signal(self, acc_type: str):
        self.accessories.spawn_accessory(acc_type)

    def call_cat_to_accessory(self, acc_type: str, target_x: float):
        if not self.cats:
            return
        candidates = [c for c in self.cats.values() if not c.in_conversation and not c.is_thinking]
        if not candidates:
            candidates = list(self.cats.values())
        chosen = min(candidates, key=lambda c: abs((c.pos_x + c.width() / 2.0) - target_x))
        chosen.facing_left = ((chosen.pos_x + chosen.width() / 2.0) > target_x)

        # Chercher l'accessoire cible le plus proche
        target_acc = None
        for acc in self.accessories.accessories.values():
            if acc.acc_type == acc_type and abs((acc.pos_x + acc.width() / 2.0) - target_x) < 50:
                target_acc = acc
                break

        if acc_type == "panier" and target_acc is not None:
            target_acc.occupant = chosen
            chosen.tucked_in_acc = target_acc
            chosen.pos_x = target_x - chosen.width() / 2.0
            chosen.set_behavior("sleep", 15000)
            chosen.show_speech("Je m'installe dans mon panier tout doux... Zzz 🧺💖", duration_ms=4500, bubble_type="speech")
            target_acc.update()
            chosen.update()
        elif acc_type == "cabane" and target_acc is not None:
            chosen.pos_x = target_x - chosen.width() / 2.0
            chosen.set_behavior("sleep", 12000)
            chosen.show_speech("Je rentre me reposer dans ma petite cabane ! 🏠🐾", duration_ms=4000, bubble_type="speech")
            target_acc.update()
            chosen.update()
        elif acc_type == "nourriture" and target_acc is not None:
            chosen.pos_x = target_x - chosen.width() / 2.0
            chosen.facing_left = (chosen.pos_x > target_x)
            chosen.set_behavior("sit", 8000)
            chosen.show_speech("Chouette, des croquettes toutes fraîches ! Crunch crunch... 🥣🐟", duration_ms=4500, bubble_type="speech")
            self.notify_quest_action("feed", 1, chosen.cat_id)
            target_acc.update()
            chosen.update()
        elif acc_type == "eau" and target_acc is not None:
            chosen.pos_x = target_x - chosen.width() / 2.0
            chosen.facing_left = (chosen.pos_x > target_x)
            chosen.set_behavior("sit", 7500)
            chosen.show_speech("Slurp slurp... l'eau de la fontaine est si désaltérante ! 💧🐾", duration_ms=4500, bubble_type="speech")
            self.notify_quest_action("drink", 1, chosen.cat_id)
            target_acc.update()
            chosen.update()
        else:
            chosen.perform_jump(14.0)
            chosen.show_speech("Je bondis vers l'arbre à chat ! 🌳👑", duration_ms=4000, bubble_type="speech")
            chosen.set_behavior("walk", 5000)

    def on_task_done_cheer(self, cat_id: str, task_text: str):
        actor = self.cats.get(cat_id)
        if actor:
            actor.perform_jump(14.0)
        self.notify_quest_action("todo", 1, cat_id)

    def _on_actor_solo_thought_requested(self, cat_id: str, context_hint: str):
        if "caresse" in context_hint.lower() or "friandise" in context_hint.lower():
            self.notify_quest_action("pet", 1, cat_id)
        self.trigger_solo_thought_for_cat(cat_id, context_hint, is_spoken=False)

    def notify_quest_action(self, action_type: str, count: int = 1, cat_id: Optional[str] = None):
        """Advances active matching quests and celebrates completions with XP and virtual gifts!"""
        completed = self.quests.record_action(action_type, count)
        for q in completed:
            actor = self.cats.get(cat_id) if cat_id else (next(iter(self.cats.values())) if self.cats else None)
            if actor:
                actor.perform_jump(14.5)
                # Débloque automatiquement un trésor virtuel pour fêter la quête !
                gift = self.gifts.create_random_gift(actor.name)
                actor.show_speech(
                    f"🎉 Quête accomplie : « {q['title']} » (+{q['reward_xp']} XP) !\n"
                    f"🎁 Trésor débloqué : {gift['icon']} {gift['name']} [{gift['rarity']}] !",
                    duration_ms=7500,
                    bubble_type="speech",
                )
        for bubble in self.chat_bubbles.values():
            if bubble.isVisible():
                bubble.refresh_quests_display()
                bubble.refresh_gifts_display()

    def hunt_treasure_for_cat(self, cat_id: str):
        """Cat goes exploring off to find a virtual treasure on the PC!"""
        actor = self.cats.get(cat_id)
        if not actor or actor.is_thinking:
            return

        actor.in_conversation = False
        actor.facing_left = (random.random() < 0.5)
        actor.set_behavior("walk", 3500)
        actor.show_speech("Je pars fouiller ton PC pour te dégoter un trésor ! 🐾🔍", duration_ms=2500, bubble_type="speech")

        def _on_found():
            gift = self.gifts.create_random_gift(actor.name)
            actor.facing_left = not actor.facing_left
            actor.perform_jump(14.0)
            actor.show_speech(
                f"🎁 Regarde ce que j'ai trouvé : {gift['icon']} {gift['name']} [{gift['rarity']}] !\n« {gift['lore']} »",
                duration_ms=7500,
                bubble_type="speech",
            )
            self.notify_quest_action("pet", 1, cat_id)
            for bubble in self.chat_bubbles.values():
                if bubble.isVisible():
                    bubble.refresh_gifts_display()

        QTimer.singleShot(2800, _on_found)

    def _maybe_trigger_autonomous_treasure(self):
        """Autonomous chance for a cat to bring back a gift."""
        if not self.cats or self.dialogue_busy:
            return
        if random.random() < 0.25:
            available = [c for c in self.cats.values() if not c.in_conversation and not c.is_thinking]
            if available:
                chosen = random.choice(available)
                self.hunt_treasure_for_cat(chosen.cat_id)

    def _on_chat_bubble_closed(self, cat_id: str):
        actor = self.cats.get(cat_id)
        if actor:
            actor.in_conversation = False
            actor.set_behavior("walk")

    def handle_user_chat_message(self, cat_id: str, user_message: str):
        actor = self.cats.get(cat_id)
        if not actor:
            return

        self.notify_quest_action("chat", 1, cat_id)

        # 1. Immediate rule response (instant, 100% reliable)
        matched_rule = self.memory.check_learned_rule(cat_id, user_message) or ""
        if matched_rule:
            if matched_rule.startswith("__RULE_TAUGHT__:"):
                parts = matched_rule.split(":", 2)
                trig = parts[1] if len(parts) > 1 else ""
                resp = parts[2] if len(parts) > 2 else ""
                reply = f"Miaou ! C'est bien noté : quand tu diras « {trig} », je répondrai « {resp} » ! 🐾"
            else:
                reply = matched_rule
            self._on_user_chat_reply(cat_id, "meow", reply, "")
            return

        # 2. General conversation through Ollama Gemma 3
        actor.is_thinking = True
        actor.set_behavior("sit", 15000)
        actor.update()

        cat_tasks = self.tasks.get_tasks(cat_id)
        tasks_summary = ", ".join([f"«{t['text']}» ({'faite' if t['done'] else 'à faire'})" for t in cat_tasks])

        worker = UserChatWorker(
            base_url=self.config.get("ollama_url", "http://localhost:11434"),
            model=self.config.get("ollama_model", "gemma3:1b"),
            cat_id=actor.cat_id,
            cat_name=actor.name,
            coat=actor.coat,
            personality=actor.personality,
            facts=self.memory.get_facts(cat_id),
            rules=self.memory.get_rules(cat_id),
            history=self.memory.get_history(cat_id),
            user_message=user_message,
            matched_rule_result="",
            tasks_summary=tasks_summary,
        )
        worker.finished_reply.connect(self._on_user_chat_reply)
        worker.finished.connect(lambda w=worker: self._cleanup_worker(w))
        self.active_workers.append(worker)
        worker.start()

    def _on_user_chat_reply(self, cat_id: str, state_anim: str, reply_text: str, extra_fact: str):
        self.memory.add_message(cat_id, "assistant", reply_text)
        if extra_fact:
            self.memory.add_fact(cat_id, extra_fact)

        actor = self.cats.get(cat_id)
        bubble = self.chat_bubbles.get(cat_id)

        if actor:
            actor.is_thinking = False
            actor.set_behavior(state_anim, duration_ms=6500)
            # Only show transient speech bubble if the interactive chat bubble was closed
            if not (bubble and bubble.isVisible()):
                actor.show_speech(reply_text, duration_ms=6500, bubble_type="speech")
            actor.update()

        if bubble and bubble.isVisible():
            bubble.on_ai_reply_received()

    def trigger_random_solo_thought(self, context_hint: str = "", force_spoken: Optional[bool] = None):
        if not self.cats:
            return
        available = [c for c in self.cats.values() if not c.in_conversation and not c.is_thinking]
        if not available:
            return
        chosen = random.choice(available)

        # 35% de chance que le chat s'enquière de l'avancement de sa To-Do List !
        if not context_hint and random.random() < 0.35:
            cat_tasks = self.tasks.get_tasks(chosen.cat_id)
            undone = [t for t in cat_tasks if not t.get("done")]
            done = [t for t in cat_tasks if t.get("done")]
            if undone:
                chosen_task = random.choice(undone)["text"]
                context_hint = (
                    f"To-Do List : L'humain a la tâche suivante à accomplir : « {chosen_task} ». "
                    f"Demande-lui avec ton caractère félin où il en est ou si sa to-do avance !"
                )
                if force_spoken is None:
                    force_spoken = True  # Dire tout haut pour que l'humain voie la question
            elif done:
                context_hint = "To-Do List : Toutes les tâches sont terminées et cochées ! Félicite chaleureusement l'humain pour son travail accompli."
                if force_spoken is None:
                    force_spoken = True

        is_spoken = force_spoken if force_spoken is not None else (random.random() < 0.45)
        self.trigger_solo_thought_for_cat(chosen.cat_id, context_hint, is_spoken=is_spoken)

    def trigger_todo_check_for_cat(self, cat_id: str):
        """Cat explicitly asks the user about its To-Do List progress."""
        cat_tasks = self.tasks.get_tasks(cat_id)
        undone = [t for t in cat_tasks if not t.get("done")]
        done = [t for t in cat_tasks if t.get("done")]
        if undone:
            chosen_task = random.choice(undone)["text"]
            hint = f"To-Do List : Demande curieusement à l'humain où en est la tâche : « {chosen_task} »."
        elif done:
            hint = "To-Do List : Toutes les tâches sont finies ! Félicite chaleureusement l'humain pour son travail."
        else:
            hint = "To-Do List : Ta to-do list est vide. Demande gentiment à l'humain de te donner une tâche à faire !"
        self.trigger_solo_thought_for_cat(cat_id, hint, is_spoken=True)

    def trigger_solo_thought_for_cat(self, cat_id: str, context_hint: str = "", is_spoken: bool = False):
        actor = self.cats.get(cat_id)
        if not actor or actor.is_thinking:
            return

        actor.is_thinking = True
        actor.update()

        mem_block = self.memory.format_memory_block(cat_id, max_recent=4)

        worker = SoloThoughtWorker(
            base_url=self.config.get("ollama_url", "http://localhost:11434"),
            model=self.config.get("ollama_model", "gemma3:1b"),
            cat_id=actor.cat_id,
            cat_name=actor.name,
            personality=actor.personality,
            current_state=actor.state,
            memory_block=mem_block,
            context_hint=context_hint,
            is_spoken=is_spoken,
            is_night=actor.is_night,
        )
        worker.finished_thought.connect(self._on_solo_thought_ready)
        worker.finished.connect(lambda w=worker: self._cleanup_worker(w))
        self.active_workers.append(worker)
        worker.start()

    def _on_solo_thought_ready(self, cat_id: str, new_state: str, thought_text: str, is_spoken: bool):
        actor = self.cats.get(cat_id)
        if not actor:
            return
        actor.is_thinking = False
        if not actor.in_conversation:
            actor.set_behavior(new_state, duration_ms=6500)
            bubble_type = "speech" if is_spoken else "thought"
            actor.show_speech(thought_text, duration_ms=6500, bubble_type=bubble_type)
        actor.update()

    def trigger_random_multi_chat(self):
        if not self.config.get("enable_chat_interactions", True):
            return
        available = [c for c in self.cats.values() if not c.in_conversation]
        if len(available) < 2 or self.dialogue_busy:
            return
        cat_a, cat_b = random.sample(available, 2)
        self._start_multi_chat(cat_a, cat_b)

    def trigger_multi_chat_with_cat(self, initiator_id: str):
        if len(self.cats) < 2:
            self.trigger_solo_thought_for_cat(
                initiator_id,
                "Je cherche un autre chat avec qui discuter mais je suis tout seul sur la barre des tâches !",
            )
            return
        if self.dialogue_busy:
            return
        cat_a = self.cats.get(initiator_id)
        others = [c for cid, c in self.cats.items() if cid != initiator_id and not c.in_conversation]
        if not cat_a or not others:
            return
        cat_b = min(others, key=lambda c: abs(c.pos_x - cat_a.pos_x))
        self._start_multi_chat(cat_a, cat_b)

    def _start_multi_chat(self, cat_a: CatActor, cat_b: CatActor):
        self.dialogue_busy = True
        self.notify_quest_action("multi_chat", 1)
        cat_a.in_conversation = True
        cat_b.in_conversation = True
        cat_a.is_thinking = True
        cat_b.is_thinking = True

        if cat_a.pos_x < cat_b.pos_x:
            cat_a.facing_left = False
            cat_b.facing_left = True
        else:
            cat_a.facing_left = True
            cat_b.facing_left = False

        cat_a.set_behavior("sit", 12000)
        cat_b.set_behavior("sit", 12000)

        prof_a = {"id": cat_a.cat_id, "name": cat_a.name, "personality": cat_a.personality}
        prof_b = {"id": cat_b.cat_id, "name": cat_b.name, "personality": cat_b.personality}

        mem_a = "; ".join(self.memory.get_facts(cat_a.cat_id)[-4:])
        mem_b = "; ".join(self.memory.get_facts(cat_b.cat_id)[-4:])

        worker = MultiCatDialogueWorker(
            base_url=self.config.get("ollama_url", "http://localhost:11434"),
            model=self.config.get("ollama_model", "gemma3:1b"),
            cat_a=prof_a,
            cat_b=prof_b,
            mem_a=mem_a,
            mem_b=mem_b,
        )
        worker.finished_dialogue.connect(
            lambda lines, summary, a=cat_a.cat_id, b=cat_b.cat_id: self._play_dialogue_sequence(a, b, lines, summary)
        )
        worker.finished.connect(lambda w=worker: self._cleanup_worker(w))
        self.active_workers.append(worker)
        worker.start()

    def _play_dialogue_sequence(self, id_a: str, id_b: str, lines: list, summary: str):
        for cid in (id_a, id_b):
            if cid in self.cats:
                self.cats[cid].is_thinking = False
                self.cats[cid].update()

        if summary:
            self.memory.add_fact(id_a, summary)

        if not lines:
            self._end_dialogue(id_a, id_b)
            return

        step_ms = 4800
        for idx, (speaker_id, state_anim, text) in enumerate(lines):
            delay = idx * step_ms
            QTimer.singleShot(
                delay,
                lambda sid=speaker_id, st=state_anim, tx=text: self._show_dialogue_turn(sid, st, tx, step_ms - 300),
            )

        total_duration = len(lines) * step_ms + 400
        QTimer.singleShot(total_duration, lambda: self._end_dialogue(id_a, id_b))

    def _show_dialogue_turn(self, speaker_id: str, state_anim: str, text: str, duration_ms: int):
        actor = self.cats.get(speaker_id)
        if actor:
            actor.set_behavior(state_anim, duration_ms=duration_ms)
            actor.show_speech(text, duration_ms=duration_ms, bubble_type="conversation")

    def _end_dialogue(self, id_a: str, id_b: str):
        self.dialogue_busy = False
        for cid in (id_a, id_b):
            actor = self.cats.get(cid)
            if actor:
                actor.in_conversation = False
                actor.set_behavior("walk")

    def _cleanup_worker(self, worker: QObject):
        if worker in self.active_workers:
            self.active_workers.remove(worker)
        worker.deleteLater()

    def open_settings(self):
        try:
            if self.settings_dlg is not None and self.settings_dlg.isVisible():
                self.settings_dlg.raise_()
                self.settings_dlg.activateWindow()
                return

            self.settings_dlg = SettingsDialog(
                self.config, self.sprite_bank, memory_manager=self.memory
            )
            self.settings_dlg.settings_applied.connect(self.sync_cats_with_config)
            self.settings_dlg.trigger_test_thought.connect(
                lambda: self.trigger_random_solo_thought("")
            )
            self.settings_dlg.trigger_test_chat.connect(self.trigger_random_multi_chat)
            self.settings_dlg.request_open_chat_for_cat.connect(self.open_chat_for_cat)
            self.settings_dlg.request_quit_app.connect(self.quit_app)
            self.settings_dlg.show()
            self.settings_dlg.raise_()
            self.settings_dlg.activateWindow()
        except Exception as e:
            print(f"[Cat AI] Erreur lors de l'ouverture des paramètres : {e}", flush=True)

    def quit_app(self):
        print("[Cat AI] Fermeture demandee de l'application.", flush=True)
        for b in list(self.chat_bubbles.values()):
            b.hide()
            b.deleteLater()
        for actor in list(self.cats.values()):
            actor.cleanup()
        self.tray.hide()
        self.app.quit()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cat AI")
    app.setQuitOnLastWindowClosed(False)
    manager = CatManager(app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


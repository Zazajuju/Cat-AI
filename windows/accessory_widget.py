import os
import json
import uuid
import random
from typing import Dict, List, Optional, Tuple, Any

from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import Qt, QPoint, QRectF, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QImage, QPixmap, QColor, QFont, QGuiApplication

ACCESSORIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accessories.json")

# Palettes de couleurs pour chaque accessoire
ACCESSORY_PALETTES = {
    "panier": {
        "O": "#3e2723",  # Bordure osier foncé
        "W": "#a1887f",  # Osier tressé clair
        "D": "#6d4c41",  # Osier ombre
        "C": "#e57373",  # Coussin rouge velours
        "L": "#ffcdd2",  # Reflet coussin moelleux
        "P": "#ffffff",  # Empreinte patte blanche
    },
    "cabane": {
        "O": "#2d1810",  # Contour bois sombre
        "R": "#c62828",  # Toit tuiles rouge brique
        "r": "#ef5350",  # Tuiles claires
        "W": "#d7ccc8",  # Planches de bois chaleureuses
        "w": "#8d6e63",  # Ombre bois
        "D": "#1a100c",  # Intérieur sombre
        "E": "#ffd700",  # Yeux dorés peeking
        "P": "#ff80ab",  # Nez rose peeking
    },
    "arbre": {
        "O": "#261914",  # Contour sombre
        "B": "#d7ccc8",  # Plateformes peluche beige
        "S": "#d4a373",  # Corde de sisal griffoir
        "s": "#8d5b32",  # Corde sisal ombre
        "T": "#ba68c8",  # Coussin violet du perchoir
        "M": "#ff80ab",  # Souris suspendue
    },
    "nourriture": {
        "O": "#1c2833",  # Contour sombre
        "B": "#f2f4f4",  # Plastique blanc moderne
        "b": "#bdc3c7",  # Plastique ombre gris
        "G": "#d5dbdb",  # Bocal transparent
        "P": "#ffffff",  # Reflet lumière bocal
        "K": "#a0522d",  # Croquettes marron dorées
        "k": "#6e2c00",  # Croquettes ombre
        "F": "#e67e22",  # Logo poisson orange
    },
    "eau": {
        "O": "#1a365d",  # Contour bleu foncé
        "B": "#ebf8ff",  # Plastique fontaine blanc/bleuté
        "b": "#bee3f8",  # Plastique ombre
        "W": "#3182ce",  # Eau bleue limpide
        "L": "#ffffff",  # Éclaboussure / reflet blanc
        "Y": "#ecc94b",  # Cœur jaune fleur fontaine
        "F": "#48bb78",  # Tige verte / feuille
    },
}

# 1. Panier Douillet (22 x 18) - 4 lignes d'espace en haut pour que la tête du chat et les Zzz soient bien visibles !
PANIER_SPRITE = [
    "......................",  # 0: Espace libre pour les Zzz animés
    "......................",  # 1: Espace libre pour les Zzz animés
    "......................",  # 2: Espace libre pour les oreilles du chat
    "......................",  # 3: Espace libre pour les oreilles du chat
    "......................",  # 4
    "......................",  # 5
    "....OOOO......OOOO....",  # 6: Anses arrière en osier
    "...OWWWWOOOOOOWWWWO...",  # 7
    "..OWWDDWWWWWWWWDDWWO..",  # 8
    ".OWDCCCCCCCCCCCCCDWO..",  # 9: Grand coussin rouge velours moelleux
    ".OWCCCCCCCCCCCCCCCWO..",  # 10
    ".OWCCCCLLLLLLCCCCCWO..",  # 11: Reflets moelleux coussin
    ".OWWWCCCCCCCCCCCCWWO..",  # 12
    ".ODWWWWWWWWWWWWWWDO...",  # 13: Rebord avant osier tressé
    "..ODWWWWOPPOWWWWDO....",  # 14: Rebord osier avec empreinte patte blanche
    "...ODWWWOPOPOWWDO.....",  # 15
    "....ODDWOOOOOOWDO.....",  # 16
    "......OOOOOOOOOO......",  # 17: Fond du panier
]

# Calque arrière du panier (anses + coussin où dort le chat)
PANIER_BACK = [
    row if y < 13 else "." * len(row)
    for y, row in enumerate(PANIER_SPRITE)
]

# Calque avant du panier (rebord osier tressé qui passe devant le bas du corps du chat)
PANIER_FRONT = [
    row if y >= 13 else "." * len(row)
    for y, row in enumerate(PANIER_SPRITE)
]

# 2. Petite Cabane (24 x 22)
CABANE_SPRITE = [
    "...........OO...........",
    "..........ORRO..........",
    ".........ORrrRO.........",
    "........ORrrrrRO........",
    ".......ORRrrrrRRO.......",
    "......ORRrrrrrrRRO......",
    ".....ORRrrrrrrrrRRO.....",
    "....ORRrrrrrrrrrrRRO....",
    "...ORRrrrrrrrrrrrrRRO...",
    "..OOOOOOOOOOOOOOOOOOOO..",
    "....OWWWWWWWWWWWWWWWO...",
    "....OWWWWWWWWWWWWWWWO...",
    "....OWWWWOOOOOOWWWWWO...",
    "....OWWWOODDDDOOWWWWO...",
    "....OWWODDDDDDDDOOWWO...",
    "....OWWODDDEWDDDOOWWO...",
    "....OWWODDDPDDDDOOWWO...",
    "....OWWODDDDDDDDOOWWO...",
    "....OWWODDDDDDDDOOWWO...",
    "....OWWWOOOOOOOOWWWWO...",
    "....OwwwwwwwwwwwwwwwO...",
    "....OOOOOOOOOOOOOOOOO...",
]

# 3. Arbre à Chat avec Griffoir & Perchoir (24 x 32)
ARBRE_SPRITE = [
    ".........OOOOOO.........",
    "........OTTTTTTO........",
    "........OTTTTTTO........",
    "........OOOOOOOO........",
    "..........OSSSO.OM......",
    "..........Ossso.OM......",
    "..........OSSSO..O......",
    "..........Ossso.........",
    ".....OOOO.OSSSO.........",
    "....OBBBBOOssso.........",
    "...OBBBBBBOOSSSO........",
    "....OOOOOOOssso.........",
    "..........OSSSO.........",
    "..........Ossso.........",
    "..........OSSSO.........",
    "..........Ossso.........",
    "..........OSSSO.........",
    "..........Ossso.........",
    "..........OSSSO.........",
    "..........Ossso.........",
    "..........OSSSO.........",
    "..........Ossso.........",
    "..........OSSSO.........",
    "..........Ossso.........",
    "..........OSSSO.........",
    "..........Ossso.........",
    "..........OSSSO.........",
    "..........Ossso.........",
    "......OOOOOOOOOOOO......",
    ".....OBBBBBBBBBBBBO.....",
    "....OBBBBBBBBBBBBBBBO...",
    "....OOOOOOOOOOOOOOOOO...",
]

# 4. Distributeur de Croquettes (20 x 18)
NOURRITURE_SPRITE = [
    "....................",
    "....................",
    "......OOOOOOOO......",
    ".....OBBBBBBBBO.....",
    ".....OBBBBBBBBO.....",
    ".....OGPPPPPPGO.....",
    ".....OGKkKkKKGO.....",
    ".....OGkKKFFkGO.....",
    ".....OGKkFFFkGO.....",
    ".....OGkKkKkKGO.....",
    ".....OGKKkKKkGO.....",
    ".....ObbbbbbbO......",
    "....OObbbbbbbOO.....",
    "...OBBBBBBBBBBBO....",
    "..OBBKkKKkkKkKBBO...",
    "..OBBKkkKKkKKkBbO...",
    "..ObbKKKKkKKKKbbO...",
    "...OOOOOOOOOOOOO....",
]

# 5. Fontaine à Eau Fraîche (20 x 18)
EAU_SPRITE = [
    "....................",
    "....................",
    "........OOOO........",
    ".......OFYYFO.......",
    "......OLLWWLLO......",
    "......OLWWWWLO......",
    "....OOOOOOOOOOOO....",
    "...OBBBBBBBBBBBBO...",
    "..OBWWWWWWWWWWWWBO..",
    "..OBWWLWWWWWWLWWBO..",
    "..OBbWWWWWWWWWWbBO..",
    "..OBBBBBBBBBBBBBBO..",
    ".OBWWWWWWWWWWWWWWBO.",
    ".OBWWLWWWWWWWWWLWBO.",
    ".OBWWWWWWWWWWWWWWBO.",
    ".OBbbbbbbbbbbbbbbBO.",
    "..OBBBBBBBBBBBBBBO..",
    "...OOOOOOOOOOOOOO...",
]

ACCESSORY_DEFS = {
    "panier": {
        "name": "Panier Douillet 🧺",
        "icon": "🧺",
        "grid": PANIER_SPRITE,
        "width": 22,
        "height": 18,
        "palette": ACCESSORY_PALETTES["panier"],
    },
    "cabane": {
        "name": "Petite Cabane 🏠",
        "icon": "🏠",
        "grid": CABANE_SPRITE,
        "width": 24,
        "height": 22,
        "palette": ACCESSORY_PALETTES["cabane"],
    },
    "arbre": {
        "name": "Arbre à Chat 🌳",
        "icon": "🌳",
        "grid": ARBRE_SPRITE,
        "width": 24,
        "height": 32,
        "palette": ACCESSORY_PALETTES["arbre"],
    },
    "nourriture": {
        "name": "Distributeur de Croquettes 🥣",
        "icon": "🥣",
        "grid": NOURRITURE_SPRITE,
        "width": 20,
        "height": 18,
        "palette": ACCESSORY_PALETTES["nourriture"],
    },
    "eau": {
        "name": "Fontaine à Eau Fraîche 💧",
        "icon": "💧",
        "grid": EAU_SPRITE,
        "width": 20,
        "height": 18,
        "palette": ACCESSORY_PALETTES["eau"],
    },
}


def render_grid_pixmap(grid: List[str], palette: Dict[str, str], scale: int = 5) -> QPixmap:
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0
    img = QImage(w, h, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch != "." and ch in palette:
                img.setPixelColor(x, y, QColor(palette[ch]))
    return QPixmap.fromImage(img).scaled(
        w * scale,
        h * scale,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.FastTransformation,
    )


def render_accessory_pixmap(acc_type: str, scale: int = 5) -> QPixmap:
    item_def = ACCESSORY_DEFS.get(acc_type, ACCESSORY_DEFS["panier"])
    return render_grid_pixmap(item_def["grid"], item_def["palette"], scale)


class AccessoryWidget(QWidget):
    """Draggable interactive pixel-art cat accessory (Basket, Cabin, Cat Tree)."""

    request_delete = pyqtSignal(str)           # (acc_id)
    request_call_cat = pyqtSignal(str, float)  # (acc_type, target_x)
    request_spawn_new = pyqtSignal(str)        # (acc_type)
    position_changed = pyqtSignal()

    def __init__(self, acc_id: str, acc_type: str, pos_x: float, pos_y: float, scale: int = 5, parent=None):
        super().__init__(parent)
        self.acc_id = acc_id
        self.acc_type = acc_type
        self.scale = scale
        self.pos_x = float(pos_x)
        self.pos_y = float(pos_y)

        self.is_dragging = False
        self.drag_offset = QPoint()
        self.occupant: Optional[Any] = None
        self.interaction_cooldown = 0

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.pixmap = render_accessory_pixmap(self.acc_type, self.scale)
        if self.acc_type == "panier":
            self.pixmap_back = render_grid_pixmap(PANIER_BACK, ACCESSORY_PALETTES["panier"], self.scale)
            self.pixmap_front = render_grid_pixmap(PANIER_FRONT, ACCESSORY_PALETTES["panier"], self.scale)
        else:
            self.pixmap_back = self.pixmap
            self.pixmap_front = self.pixmap

        self.setFixedSize(self.pixmap.width(), self.pixmap.height())
        self.move(int(self.pos_x), int(self.pos_y))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_p = event.globalPosition().toPoint() - self.drag_offset
            self.pos_x = float(new_p.x())
            self.pos_y = float(new_p.y())
            self.move(int(self.pos_x), int(self.pos_y))
            if self.occupant is not None:
                self.occupant.pos_x = self.pos_x + (self.width() - self.occupant.width()) / 2.0
                self.occupant.move(int(self.occupant.pos_x), int(self.occupant.pos_y))
                if hasattr(self.occupant, "bubble") and self.occupant.bubble.isVisible():
                    self.occupant.bubble.update_position(
                        int(self.occupant.pos_x + self.occupant.width() // 2),
                        int(self.occupant.pos_y),
                    )
            self.position_changed.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self._snap_to_ground_if_close()
            if self.occupant is not None:
                self.occupant.pos_x = self.pos_x + (self.width() - self.occupant.width()) / 2.0
                self.occupant.move(int(self.occupant.pos_x), int(self.occupant.pos_y))
            self.position_changed.emit()

    def _snap_to_ground_if_close(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            ground_y = avail.bottom() - self.height()
            if abs(self.pos_y - ground_y) < 60:
                self.pos_y = float(ground_y)
                self.move(int(self.pos_x), int(self.pos_y))

    def _show_context_menu(self, global_pos: QPoint):
        menu = QMenu()
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #1e202c;
                color: #f5f6fa;
                border: 1px solid #ffd54f;
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI';
                font-size: 9pt;
            }
            QMenu::item { padding: 6px 16px; border-radius: 4px; }
            QMenu::item:selected { background-color: #ffd54f; color: #15161e; font-weight: bold; }
            """
        )

        acc_info = ACCESSORY_DEFS.get(self.acc_type, ACCESSORY_DEFS["panier"])
        title = menu.addAction(f"{acc_info['icon']} {acc_info['name']}")
        title.setEnabled(False)
        menu.addSeparator()

        call_labels = {
            "panier": "🐾 Appeler un chat dans le panier",
            "cabane": "🏠 Appeler un chat dans la cabane",
            "arbre": "🌳 Appeler un chat vers l'arbre à chat",
            "nourriture": "🥣 Appeler un chat pour manger des croquettes",
            "eau": "💧 Appeler un chat pour boire de l'eau fraîche",
        }
        act_call = menu.addAction(call_labels.get(self.acc_type, f"🐾 Appeler un chat vers {acc_info['name']}"))

        act_refill = None
        if self.acc_type == "nourriture":
            act_refill = menu.addAction("✨ Remplir le réservoir de croquettes")
        elif self.acc_type == "eau":
            act_refill = menu.addAction("✨ Renouveler l'eau fraîche")

        menu.addSeparator()

        sub_add = menu.addMenu("➕ Ajouter un autre meuble...")
        act_add_panier = sub_add.addAction("🧺 Panier Douillet")
        act_add_cabane = sub_add.addAction("🏠 Petite Cabane")
        act_add_arbre = sub_add.addAction("🌳 Arbre à Chat")
        act_add_food = sub_add.addAction("🥣 Distributeur de Croquettes")
        act_add_water = sub_add.addAction("💧 Fontaine à Eau Fraîche")

        menu.addSeparator()
        act_del = menu.addAction("❌ Ranger cet accessoire")

        chosen = menu.exec(global_pos)
        if chosen == act_call:
            center_x = self.pos_x + self.width() / 2.0
            self.request_call_cat.emit(self.acc_type, center_x)
        elif chosen == act_del:
            self.request_delete.emit(self.acc_id)
        elif chosen == act_refill:
            self.interaction_cooldown = 0
            if self.acc_type == "nourriture":
                center_x = self.pos_x + self.width() / 2.0
                self.request_call_cat.emit(self.acc_type, center_x)
            elif self.acc_type == "eau":
                center_x = self.pos_x + self.width() / 2.0
                self.request_call_cat.emit(self.acc_type, center_x)
        elif chosen == act_add_panier:
            self.request_spawn_new.emit("panier")
        elif chosen == act_add_cabane:
            self.request_spawn_new.emit("cabane")
        elif chosen == act_add_arbre:
            self.request_spawn_new.emit("arbre")
        elif chosen == act_add_food:
            self.request_spawn_new.emit("nourriture")
        elif chosen == act_add_water:
            self.request_spawn_new.emit("eau")

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.acc_type == "panier" and self.occupant is not None:
            # 1. Calque arrière : anses et grand coussin rouge moelleux
            painter.drawPixmap(0, 0, self.pixmap_back)

            # 2. Le chat confortablement pelotonné dans le coussin
            cat = self.occupant
            cat_pix = cat.sprite_bank.get_frame(
                cat.coat,
                cat.state,
                cat.frame_idx,
                scale=self.scale,
            )
            if cat_pix and not cat_pix.isNull():
                cat_w = cat_pix.width()
                cat_x = (self.width() - cat_w) // 2
                cat_y = int(1.2 * self.scale) if cat.state == "sleep" else int(1.8 * self.scale)

                if cat.facing_left:
                    painter.save()
                    painter.translate(cat_x + cat_w, cat_y)
                    painter.scale(-1, 1)
                    painter.drawPixmap(0, 0, cat_pix)
                    painter.restore()
                else:
                    painter.drawPixmap(cat_x, cat_y, cat_pix)

            # 3. Calque avant : rebord avant en osier tressé avec patte de chat blanche
            painter.drawPixmap(0, 0, self.pixmap_front)
        else:
            painter.drawPixmap(0, 0, self.pixmap)


class AccessoryManager(QObject):
    """Manages spawning, persistent saving, and cat interactions with accessories."""

    request_call_cat = pyqtSignal(str, float)        # (acc_type, target_x)
    quest_action_triggered = pyqtSignal(str, int, str)  # (action_type, count, cat_id)

    def __init__(self, scale: int = 5, parent=None):
        super().__init__(parent)
        self.scale = scale
        self.accessories: Dict[str, AccessoryWidget] = {}
        self.load()

    def load(self):
        saved = []
        if os.path.exists(ACCESSORIES_FILE):
            try:
                with open(ACCESSORIES_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
            except Exception as e:
                print(f"[Cat AI] Erreur chargement accessoires: {e}")

        if not saved:
            # Starter furniture set nicely spaced across primary taskbar
            screen = QGuiApplication.primaryScreen()
            w_scr = screen.availableGeometry().width() if screen else 1920
            g_y = (screen.availableGeometry().bottom() - 80) if screen else 940

            saved = [
                {"id": "acc_panier_1", "type": "panier", "x": w_scr * 0.15, "y": g_y + 10},
                {"id": "acc_food_1", "type": "nourriture", "x": w_scr * 0.35, "y": g_y + 10},
                {"id": "acc_water_1", "type": "eau", "x": w_scr * 0.50, "y": g_y + 10},
                {"id": "acc_cabane_1", "type": "cabane", "x": w_scr * 0.68, "y": g_y - 25},
                {"id": "acc_arbre_1", "type": "arbre", "x": w_scr * 0.85, "y": g_y - 75},
            ]

        for item in saved:
            self.spawn_accessory(
                acc_type=item.get("type", "panier"),
                pos_x=item.get("x", 200),
                pos_y=item.get("y", 900),
                acc_id=item.get("id"),
                save_after=False,
            )
        self.save()

    def save(self):
        data = []
        for acc in self.accessories.values():
            data.append({
                "id": acc.acc_id,
                "type": acc.acc_type,
                "x": acc.pos_x,
                "y": acc.pos_y,
            })
        try:
            with open(ACCESSORIES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Cat AI] Erreur sauvegarde accessoires: {e}")

    def spawn_accessory(
        self,
        acc_type: str,
        pos_x: Optional[float] = None,
        pos_y: Optional[float] = None,
        acc_id: Optional[str] = None,
        save_after: bool = True,
    ) -> AccessoryWidget:
        aid = acc_id or f"acc_{acc_type}_{uuid.uuid4().hex[:6]}"
        if pos_x is None or pos_y is None:
            screen = QGuiApplication.primaryScreen()
            avail = screen.availableGeometry() if screen else None
            h_acc = ACCESSORY_DEFS.get(acc_type, {}).get("height", 18) * self.scale
            pos_x = float(random.randint(150, avail.width() - 250)) if avail else 300.0
            pos_y = float(avail.bottom() - h_acc) if avail else 900.0

        widget = AccessoryWidget(aid, acc_type, pos_x, pos_y, scale=self.scale)
        widget.request_delete.connect(self.remove_accessory)
        widget.request_spawn_new.connect(lambda t: self.spawn_accessory(t))
        widget.request_call_cat.connect(self.request_call_cat.emit)
        widget.position_changed.connect(self.save)
        widget.show()

        self.accessories[aid] = widget
        if save_after:
            self.save()
        return widget

    def remove_accessory(self, acc_id: str):
        if acc_id in self.accessories:
            w = self.accessories.pop(acc_id)
            if hasattr(w, "occupant") and w.occupant:
                w.occupant.tucked_in_acc = None
                w.occupant.set_behavior("walk")
            w.hide()
            w.deleteLater()
            self.save()

    def clear_all(self):
        for w in list(self.accessories.values()):
            if hasattr(w, "occupant") and w.occupant:
                w.occupant.tucked_in_acc = None
                w.occupant.set_behavior("walk")
            w.hide()
            w.deleteLater()
        self.accessories.clear()
        self.save()

    def check_cat_interaction(self, cat):
        """Allows a cat to discover and enjoy a nearby cozy accessory!"""
        if cat.is_dragging or cat.in_conversation or cat.laser_target is not None:
            return

        cat_center_x = cat.pos_x + cat.width() / 2.0

        for acc in self.accessories.values():
            acc_center_x = acc.pos_x + acc.width() / 2.0
            dist_x = abs(cat_center_x - acc_center_x)

            if dist_x < 36:
                if acc.interaction_cooldown > 0:
                    acc.interaction_cooldown -= 1
                    continue

                # 1. Panier douillet : s'installer pour dormir ou faire le pain
                if acc.acc_type == "panier":
                    if cat.state in ("walk", "sit") and random.random() < 0.14:
                        acc.interaction_cooldown = 450
                        acc.occupant = cat
                        cat.tucked_in_acc = acc
                        cat.pos_x = acc_center_x - cat.width() / 2.0
                        cat.set_behavior("sleep" if random.random() < 0.7 else "loaf", 14000)
                        phrases = [
                            "Ce panier est tellement douillet... Zzz 🧺",
                            "Mode sieste activé dans mon panier préféré !",
                            "Ronron... le coussin est tout chaud 💖",
                        ]
                        cat.show_speech(random.choice(phrases), duration_ms=4500, bubble_type="speech")
                        acc.update()
                        cat.update()
                        return

                # 2. Petite Cabane : entrer se reposer au calme
                elif acc.acc_type == "cabane":
                    if cat.state in ("walk", "sit") and random.random() < 0.10:
                        acc.interaction_cooldown = 450
                        cat.pos_x = acc_center_x - cat.width() / 2.0
                        cat.set_behavior("sleep", 12000)
                        phrases = [
                            "Bienvenue dans ma petite cabane secrète ! 🏠",
                            "Je suis bien caché au chaud dans ma maisonnette 🐾",
                        ]
                        cat.show_speech(random.choice(phrases), duration_ms=4500, bubble_type="speech")
                        return

                # 3. Arbre à Chat : faire ses griffes ou percher
                elif acc.acc_type == "arbre":
                    if cat.state in ("walk", "sit") and random.random() < 0.12:
                        acc.interaction_cooldown = 400
                        if random.random() < 0.5:
                            cat.set_behavior("stretch", 7000)
                            cat.show_speech("Je fais mes griffes sur la corde de l'arbre à chat ! 🐾", duration_ms=4500, bubble_type="speech")
                        else:
                            cat.perform_jump(15.0)
                            cat.show_speech("Je bondis au sommet de l'arbre à chat ! 🌳👑", duration_ms=4500, bubble_type="speech")
                        return

                # 4. Distributeur de Croquettes : manger un bon repas
                elif acc.acc_type == "nourriture":
                    if cat.state in ("walk", "sit") and random.random() < 0.14:
                        acc.interaction_cooldown = 450
                        cat.facing_left = (cat_center_x > acc_center_x)
                        cat.set_behavior("sit", 8000)
                        phrases = [
                            "Crunch crunch... ces croquettes au saumon sont délicieuses ! 🐟",
                            "Miam miam ! Rien de tel qu'une bonne gamelle pleine ! 🥣",
                            "Croustillant et savoureux ! Merci pour le festin ! 🐾",
                        ]
                        cat.show_speech(random.choice(phrases), duration_ms=4500, bubble_type="speech")
                        self.quest_action_triggered.emit("feed", 1, cat.cat_id)
                        return

                # 5. Fontaine à Eau : boire de l'eau fraîche
                elif acc.acc_type == "eau":
                    if cat.state in ("walk", "sit") and random.random() < 0.14:
                        acc.interaction_cooldown = 450
                        cat.facing_left = (cat_center_x > acc_center_x)
                        cat.set_behavior("sit", 7500)
                        phrases = [
                            "Slurp slurp... l'eau de la fontaine est si fraîche et limpide ! 💧",
                            "Glou glou... rien de tel pour bien s'hydrater ! 🐾",
                            "J'adore observer les vaguelettes de la fontaine avant de boire ! 🌊",
                        ]
                        cat.show_speech(random.choice(phrases), duration_ms=4500, bubble_type="speech")
                        self.quest_action_triggered.emit("drink", 1, cat.cat_id)
                        return

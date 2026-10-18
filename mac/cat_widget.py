import random
from typing import Dict, Optional, Tuple, Any
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QPen,
    QPainterPath,
    QFontMetrics,
    QGuiApplication,
    QRadialGradient,
    QBrush,
)

from sprites import SpriteBank


def compute_taskbar_bounds(screen_mode: str, widget_w: int, widget_h: int, scale: int) -> Tuple[int, int, int]:
    """Returns (min_x, max_x, ground_y) across either all screens or a selected screen."""
    screens = QGuiApplication.screens()
    if not screens:
        return 0, 1920 - widget_w, 1000 - widget_h

    if screen_mode != "all":
        try:
            idx = int(screen_mode)
            if 0 <= idx < len(screens):
                avail = screens[idx].availableGeometry()
                min_x = avail.left() + 12
                max_x = avail.right() - widget_w - 12
                ground_y = avail.bottom() - widget_h + (1 * scale)
                return min_x, max_x, ground_y
        except ValueError:
            pass

    # Combine horizontal bounds of all screens
    min_x = min(s.availableGeometry().left() for s in screens) + 12
    max_x = max(s.availableGeometry().right() for s in screens) - widget_w - 12
    primary = QGuiApplication.primaryScreen() or screens[0]
    ground_y = primary.availableGeometry().bottom() - widget_h + (1 * scale)
    return min_x, max_x, ground_y


class LaserDot(QWidget):
    """Pulsing red laser pointer dot that follows the mouse cursor."""

    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(36, 36)
        self.pulse = 0
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._step_pulse)
        self.pulse_timer.start(50)

    def _step_pulse(self):
        self.pulse = (self.pulse + 1) % 20
        self.update()

    def update_position(self, global_x: int, global_y: int):
        self.move(global_x - self.width() // 2, global_y - self.height() // 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        cx = self.width() / 2.0
        cy = self.height() / 2.0

        glow_r = 10.0 + (self.pulse % 10) * 0.4
        grad = QRadialGradient(cx, cy, glow_r)
        grad.setColorAt(0.0, QColor(255, 40, 40, 230))
        grad.setColorAt(0.4, QColor(255, 20, 20, 150))
        grad.setColorAt(0.8, QColor(255, 0, 0, 50))
        grad.setColorAt(1.0, QColor(255, 0, 0, 0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(cx - glow_r, cy - glow_r, glow_r * 2, glow_r * 2))

        # Bright center dot
        painter.setBrush(QColor(255, 240, 240))
        painter.drawEllipse(QRectF(cx - 2.5, cy - 2.5, 5, 5))


class SpeechBubble(QWidget):
    """Floating pixel-cozy speech/thought bubble above a cat."""

    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.cat_name = ""
        self.text = ""
        self.bubble_type = "thought"  # "thought", "speech", "conversation"
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

        self.font_name = QFont("Segoe UI", 8, QFont.Weight.Bold)
        self.font_text = QFont("Segoe UI", 9, QFont.Weight.Medium)

    def show_message(
        self,
        cat_name: str,
        text: str,
        anchor_x: int,
        anchor_top_y: int,
        duration_ms: int = 6000,
        bubble_type: str = "thought",
    ):
        self.cat_name = cat_name
        self.text = text
        self.bubble_type = bubble_type

        fm_text = QFontMetrics(self.font_text)
        max_w = 250
        rect = fm_text.boundingRect(
            0, 0, max_w, 200, Qt.TextFlag.TextWordWrap, self.text
        )

        fm_name = QFontMetrics(self.font_name)
        name_w = fm_name.horizontalAdvance(self.cat_name) + 40

        bubble_w = max(rect.width() + 26, name_w + 20, 110)
        bubble_h = rect.height() + 42

        self.resize(bubble_w, bubble_h)
        self.update_position(anchor_x, anchor_top_y)
        self.show()
        self.raise_()
        self.update()
        self.hide_timer.start(duration_ms)

    def update_position(self, anchor_x: int, anchor_top_y: int):
        screens = QGuiApplication.screens()
        if screens:
            min_left = min(s.availableGeometry().left() for s in screens)
            max_right = max(s.availableGeometry().right() for s in screens)
            x = int(anchor_x - self.width() // 2)
            x = max(min_left + 6, min(x, max_right - self.width() - 6))
            y = int(anchor_top_y - self.height() + 4)
            self.move(x, y)

    def paintEvent(self, event):
        if not self.text:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height() - 10

        if self.bubble_type == "thought":
            bg_color = QColor(20, 22, 34, 245)
            border_color = QColor(255, 179, 92, 245)
        elif self.bubble_type == "conversation":
            bg_color = QColor(36, 26, 54, 245)
            border_color = QColor(175, 130, 255, 250)
        else:  # "speech"
            bg_color = QColor(24, 28, 44, 248)
            border_color = QColor(92, 170, 255, 250)

        path = QPainterPath()
        path.addRoundedRect(QRectF(2, 2, w - 4, h - 2), 10, 10)

        cx = w / 2.0
        if self.bubble_type == "thought":
            # Draw thought circles descending to the cat's head
            painter.setPen(QPen(border_color, 1.8))
            painter.setBrush(bg_color)
            painter.drawPath(path)
            painter.drawEllipse(QRectF(cx - 3, h + 1, 6, 6))
            painter.drawEllipse(QRectF(cx - 6, h + 8, 4, 4))
        else:
            # Pointer triangle
            path.moveTo(cx - 6, h)
            path.lineTo(cx, h + 8)
            path.lineTo(cx + 6, h)
            painter.setPen(QPen(border_color, 2))
            painter.setBrush(bg_color)
            painter.drawPath(path)

        # Badge text
        painter.setFont(self.font_name)
        if self.bubble_type == "thought":
            badge_color = QColor("#ffb866")
            prefix = "💭 "
            title_text = f"{prefix}{self.cat_name} (pense)"
        elif self.bubble_type == "conversation":
            badge_color = QColor("#d4b3ff")
            prefix = "🗣️ "
            title_text = f"{prefix}{self.cat_name}"
        else:
            badge_color = QColor("#7ec8ff")
            prefix = "💬 "
            title_text = f"{prefix}{self.cat_name} (dit tout haut)"

        painter.setPen(badge_color)
        painter.drawText(
            QRectF(12, 6, w - 24, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            title_text,
        )

        painter.setFont(self.font_text)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(
            QRectF(12, 25, w - 24, h - 28),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,
            self.text,
        )


class CatActor(QWidget):
    """Individual pixel-art cat living on the Windows taskbar."""

    request_config = pyqtSignal()
    request_open_chat = pyqtSignal(str)          # (cat_id)
    request_open_todo = pyqtSignal(str)          # (cat_id)
    request_solo_thought = pyqtSignal(str, str)  # (cat_id, context_hint)
    request_speak_thought = pyqtSignal(str)      # (cat_id)
    request_check_todo = pyqtSignal(str)         # (cat_id)
    request_open_quests = pyqtSignal(str)        # (cat_id)
    request_open_gifts = pyqtSignal(str)         # (cat_id)
    request_hunt_treasure = pyqtSignal(str)      # (cat_id)
    request_multi_chat = pyqtSignal(str)         # (cat_id)
    request_toggle_laser = pyqtSignal()
    request_quit = pyqtSignal()

    NAME_HEADER_H = 20  # Extra top space for the floating name tag / "..." indicator

    def __init__(
        self,
        cat_profile: Dict[str, str],
        sprite_bank: SpriteBank,
        scale: int = 5,
        speed: float = 1.8,
        screen_mode: str = "all",
        show_name: bool = True,
        spawn_index: int = 0,
    ):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SubWindow
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self.sprite_bank = sprite_bank
        self.cat_id = cat_profile["id"]
        self.name = cat_profile["name"]
        self.coat = cat_profile["coat"]
        self.personality = cat_profile["personality"]

        self.scale = scale
        self.base_speed = speed
        self.screen_mode = screen_mode
        self.show_name = show_name

        # Animation & Physics State
        self.state = "walk"
        self.frame_idx = 0
        self.facing_left = random.choice([True, False])
        self.is_dragging = False
        self.drag_offset = QPoint()
        self.drag_moved = False
        self.in_conversation = False
        self.is_thinking = False
        self.is_night = False
        self.laser_target: Optional[Tuple[float, float]] = None
        self.laser_pounce_cooldown = 0
        self.tucked_in_acc: Optional[Any] = None

        # Unique agility & horizontal attack offset (prevents speed stacking and identical positions)
        pers_low = self.personality.lower()
        if any(w in pers_low for w in ("hyperactif", "chaotique", "chasser", "pixel")):
            self.agility = 1.30
        elif any(w in pers_low for w in ("gourmand", "paresseux", "sommeil", "croquette")):
            self.agility = 0.88
        elif any(w in pers_low for w in ("philosophe", "médite", "calme")):
            self.agility = 1.05
        else:
            self.agility = 0.95 + (spawn_index % 3) * 0.15

        offsets = [0.0, -42.0, 42.0, -78.0, 78.0]
        self.laser_offset_x = offsets[spawn_index % len(offsets)]

        # Position & Gravity
        self.pos_x = 200.0
        self.pos_y = 200.0
        self.vel_y = 0.0
        self.is_falling = False

        # Timers
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._advance_frame)
        self.anim_timer.start(180)

        self.state_timer = QTimer(self)
        self.state_timer.setSingleShot(True)
        self.state_timer.timeout.connect(self._pick_random_local_behavior)

        self.bubble = SpeechBubble()

        self._update_dimensions()
        self._place_on_taskbar_initial(spawn_index)
        self._schedule_next_local_state()
        self.show()
        self.raise_()

    def _update_dimensions(self):
        w = max(20 * self.scale, 84)
        h = 16 * self.scale + self.NAME_HEADER_H
        self.setFixedSize(w, h)
        self.setToolTip(
            f"🐾 {self.name} ({self.coat})\nClic gauche : Caresser / Déplacer\nClic droit : Menu de configuration"
        )

    def apply_settings(
        self,
        profile: Dict[str, str],
        scale: int,
        speed: float,
        screen_mode: str = "all",
        show_name: bool = True,
    ):
        self.name = profile["name"]
        self.coat = profile["coat"]
        self.personality = profile["personality"]
        self.scale = scale
        self.base_speed = speed
        self.screen_mode = screen_mode
        self.show_name = show_name
        self._update_dimensions()
        self._clamp_to_ground()
        self.show()
        self.raise_()
        self.update()

    def set_night_mode(self, is_night: bool):
        if self.is_night != is_night:
            self.is_night = is_night
            if is_night and not self.in_conversation:
                # Direct switch to calm sleep or loaf when night begins
                chosen = "sleep" if random.random() < 0.65 else "loaf"
                self.set_behavior(chosen, random.randint(15000, 30000))

    def set_laser_target(self, target_x: Optional[float], target_y: Optional[float]):
        if target_x is None or target_y is None:
            self.laser_target = None
        else:
            self.laser_target = (float(target_x), float(target_y))

    def get_ground_bounds(self) -> Tuple[int, int, int]:
        return compute_taskbar_bounds(
            self.screen_mode, self.width(), self.height(), self.scale
        )

    def _place_on_taskbar_initial(self, spawn_index: int = 0):
        screens = QGuiApplication.screens()
        min_x, max_x, ground_y = self.get_ground_bounds()

        # If using "all" screens and multiple monitors exist, spread initial cats across each monitor!
        if self.screen_mode == "all" and len(screens) > 1:
            scr = screens[spawn_index % len(screens)]
            avail = scr.availableGeometry()
            s_min = avail.left() + 80
            s_max = max(s_min + 20, avail.right() - self.width() - 80)
            self.pos_x = float(random.randint(s_min, s_max))
        else:
            self.pos_x = float(random.randint(min_x, max(min_x + 20, max_x)))

        self.pos_y = float(ground_y)
        self.move(int(self.pos_x), int(self.pos_y))

    def _clamp_to_ground(self):
        min_x, max_x, ground_y = self.get_ground_bounds()
        self.pos_x = max(float(min_x), min(self.pos_x, float(max_x)))
        if not self.is_dragging and not self.is_falling:
            self.pos_y = float(ground_y)
        self.move(int(self.pos_x), int(self.pos_y))

    def set_behavior(self, new_state: str, duration_ms: Optional[int] = None):
        valid_states = (
            "walk", "sit", "sleep", "meow", "groom", "jump",
            "loaf", "stretch", "purr", "stand", "stalk"
        )
        if new_state not in valid_states:
            new_state = "sit"

        if self.tucked_in_acc is not None and new_state not in ("sleep", "loaf"):
            acc = self.tucked_in_acc
            self.tucked_in_acc = None
            if hasattr(acc, "occupant") and acc.occupant == self:
                acc.occupant = None
                acc.update()

        self.state = new_state
        self.frame_idx = 0

        interval_map = {
            "walk": max(90, int(200 - self.base_speed * 22)),
            "sit": 600,
            "sleep": 850,
            "meow": 240,
            "groom": 320,
            "jump": 170,
            "loaf": 750,
            "stretch": 600,
            "purr": 350,
            "stand": 600,
            "stalk": 220,
        }
        self.anim_timer.setInterval(interval_map.get(new_state, 240))

        if duration_ms is not None:
            self.state_timer.start(duration_ms)
        else:
            self._schedule_next_local_state()
        self.update()

    def perform_jump(self, jump_power: float = 14.5):
        """Triggers an active jump high into the air with the dynamic 4-frame animation."""
        self.vel_y = -jump_power
        self.pos_y += self.vel_y
        self.is_falling = True
        self.frame_idx = 1
        self.set_behavior("jump", 1800)

    def _schedule_next_local_state(self):
        if self.in_conversation:
            return
        if self.is_night:
            dur = random.randint(14000, 32000) if self.state in ("sleep", "loaf") else random.randint(7000, 14000)
        else:
            dur = random.randint(4500, 9500)
        self.state_timer.start(dur)

    def _pick_random_local_behavior(self):
        if self.is_dragging or self.is_falling or self.in_conversation:
            self._schedule_next_local_state()
            return

        if self.is_night:
            weights = [
                ("sleep", 46),
                ("loaf", 24),
                ("sit", 15),
                ("purr", 8),
                ("stretch", 4),
                ("walk", 3),
            ]
        else:
            weights = [
                ("walk", 38),
                ("sit", 16),
                ("loaf", 12),
                ("stretch", 8),
                ("purr", 8),
                ("groom", 8),
                ("sleep", 5),
                ("stalk", 3),
                ("jump", 2),
            ]
        choices, probs = zip(*weights)
        next_state = random.choices(choices, weights=probs, k=1)[0]
        if next_state == "walk" and random.random() < 0.45:
            self.facing_left = not self.facing_left
        self.set_behavior(next_state)

    def _advance_frame(self):
        count = self.sprite_bank.frame_count(self.state)
        self.frame_idx = (self.frame_idx + 1) % count
        self.update()
        if self.tucked_in_acc is not None:
            self.tucked_in_acc.update()

    def tick_physics(self):
        if self.is_dragging:
            if self.bubble.isVisible():
                self.bubble.update_position(
                    int(self.pos_x + self.width() // 2), int(self.pos_y)
                )
            return

        min_x, max_x, ground_y = self.get_ground_bounds()

        if self.vel_y < 0.0 or self.pos_y < ground_y:
            self.is_falling = True
            self.pos_y += self.vel_y
            self.vel_y += 0.70  # gravité
            if self.pos_y >= ground_y:
                self.pos_y = float(ground_y)
                self.vel_y = 0.0
                self.is_falling = False
                if self.state == "jump":
                    self.set_behavior("sit", 1000)
            elif self.state == "jump":
                # Choix dynamique de la frame d'animation selon la vélocité verticale
                if self.vel_y < -4.0:
                    self.frame_idx = 1  # Élan ascendant / bond
                elif self.vel_y <= 4.0:
                    self.frame_idx = 2  # Plein vol / extension
                else:
                    self.frame_idx = 3  # Descente / réception
        else:
            self.pos_y = float(ground_y)
            self.vel_y = 0.0
            self.is_falling = False

        # Mouvement d'arc horizontal en plein vol pendant le saut
        if self.is_falling and not self.in_conversation:
            if self.laser_target is not None:
                tx, ty = self.laser_target
                target_x = tx + self.laser_offset_x
                center_x = self.pos_x + self.width() / 2.0
                dx = target_x - center_x
                if abs(dx) > 6:
                    air_step = (self.base_speed * self.agility * 2.2) * (-1.0 if dx < 0 else 1.0)
                    self.pos_x = max(float(min_x), min(self.pos_x + air_step, float(max_x)))
            elif self.state == "jump":
                air_step = (self.base_speed * self.agility * 1.8) * (-1.0 if self.facing_left else 1.0)
                self.pos_x = max(float(min_x), min(self.pos_x + air_step, float(max_x)))

        if not self.is_falling and not self.in_conversation:
            if self.laser_target is not None:
                tx, ty = self.laser_target
                target_x = tx + self.laser_offset_x
                center_x = self.pos_x + self.width() / 2.0
                dx = target_x - center_x
                abs_dx = abs(dx)
                height_above_ground = ground_y - ty  # Hauteur du laser au-dessus du sol

                if self.laser_pounce_cooldown > 0:
                    self.laser_pounce_cooldown -= 1

                cat_speed = self.base_speed * self.agility

                # Conditions de saut vers le laser :
                should_leap_high = (height_above_ground > 35 and abs_dx < 160 and self.laser_pounce_cooldown <= 0)
                should_pounce_ground = (abs_dx <= 35 and self.laser_pounce_cooldown <= 0)

                if should_leap_high or should_pounce_ground:
                    self.laser_pounce_cooldown = random.randint(32, 50)
                    clamped_h = max(35.0, min(float(height_above_ground), 480.0))
                    # Puissance de saut proportionnelle à la hauteur du point rouge :
                    jump_strength = -min(20.0, max(12.0, (2.0 * 0.70 * clamped_h) ** 0.5 * 1.05))
                    self.vel_y = jump_strength
                    self.pos_y += self.vel_y  # Décolle immédiatement dans les airs !
                    self.is_falling = True
                    self.facing_left = (dx < 0)
                    self.set_behavior("jump", 1800)
                    if random.random() < 0.4:
                        phrases = [
                            "Hop ! J'attrape le laser ! 🐾",
                            "Vers le point rouge !",
                            "Presque eu !",
                            "Miaouh ! 🔴",
                        ]
                        self.show_speech(random.choice(phrases), duration_ms=2200, bubble_type="speech")
                elif abs_dx <= 14:
                    # Arrivé tout près du curseur : AUCUN tremblement ou flip gauche/droite !
                    # Le chat reste stable et observe calmement
                    if self.state not in ("sit", "loaf", "groom"):
                        self.set_behavior("sit", 1500)
                elif abs_dx > 160:
                    # Traque furtive vers le laser
                    self.facing_left = (dx < 0)
                    if self.state not in ("stalk", "walk"):
                        self.set_behavior("stalk", 2200)
                    max_step = cat_speed * 1.5
                    step = min(abs_dx, max_step) * (-1.0 if self.facing_left else 1.0)
                    self.pos_x = max(float(min_x), min(self.pos_x + step, float(max_x)))
                else:
                    # Sprint rapide vers le laser
                    self.facing_left = (dx < 0)
                    if self.state != "walk":
                        self.set_behavior("walk", 1800)
                    max_step = cat_speed * 2.7
                    # Clamper à abs_dx pour ne jamais dépasser la cible d'un coup (évite toute oscillation)
                    step = min(abs_dx, max_step) * (-1.0 if self.facing_left else 1.0)
                    self.pos_x = max(float(min_x), min(self.pos_x + step, float(max_x)))
            else:
                # Comportement de déplacement standard avec vitesse individuelle
                cat_speed = self.base_speed * self.agility
                if self.state == "walk":
                    step = cat_speed * (-1.0 if self.facing_left else 1.0)
                    self.pos_x += step
                    if self.pos_x <= min_x:
                        self.pos_x = float(min_x)
                        self.facing_left = False
                    elif self.pos_x >= max_x:
                        self.pos_x = float(max_x)
                        self.facing_left = True
                elif self.state == "jump":
                    step = (cat_speed * 1.35) * (-1.0 if self.facing_left else 1.0)
                    self.pos_x = max(float(min_x), min(self.pos_x + step, float(max_x)))

        self.move(int(self.pos_x), int(self.pos_y))
        if self.bubble.isVisible():
            self.bubble.update_position(
                int(self.pos_x + self.width() // 2), int(self.pos_y)
            )

    def show_speech(
        self,
        text: str,
        duration_ms: int = 6000,
        bubble_type: str = "thought",
        is_conversation: Optional[bool] = None,
        **kwargs,
    ):
        if is_conversation is not None:
            bubble_type = "conversation" if is_conversation else "speech"
        self.bubble.show_message(
            self.name,
            text,
            int(self.pos_x + self.width() // 2),
            int(self.pos_y),
            duration_ms=duration_ms,
            bubble_type=bubble_type,
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.tucked_in_acc is None:
            pixmap = self.sprite_bank.get_frame(
                self.coat,
                self.state,
                self.frame_idx,
                scale=self.scale,
                facing_left=self.facing_left,
            )
            sprite_x = (self.width() - pixmap.width()) // 2
            sprite_y = self.NAME_HEADER_H
            painter.drawPixmap(sprite_x, sprite_y, pixmap)

        # Draw name tag or thinking indicator in top header area
        if self.is_thinking or self.show_name:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            label_text = f"💭 {self.name}..." if self.is_thinking else self.name
            font = QFont("Segoe UI", 8, QFont.Weight.Bold)
            painter.setFont(font)
            fm = QFontMetrics(font)
            tw = min(self.width() - 4, fm.horizontalAdvance(label_text) + 12)
            tx = (self.width() - tw) / 2.0

            painter.setBrush(QColor(20, 22, 32, 200))
            border_c = QColor("#f28c28") if self.is_thinking else QColor(90, 100, 130, 180)
            painter.setPen(QPen(border_c, 1.2))
            painter.drawRoundedRect(QRectF(tx, 1, tw, 16), 6, 6)

            painter.setPen(QColor("#ffd299") if self.is_thinking else QColor("#f0f2f8"))
            painter.drawText(
                QRectF(tx, 1, tw, 16),
                Qt.AlignmentFlag.AlignCenter,
                label_text,
            )

        # Draw floating z Z sleeping indicator when cat is asleep (only when on ground, basket has its own pixel Zzz)
        if self.state == "sleep" and self.tucked_in_acc is None:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            z_offset = (self.frame_idx * 3) % 8
            font_z = QFont("Segoe UI", 9, QFont.Weight.Bold)
            painter.setFont(font_z)
            painter.setPen(QColor(170, 215, 255, 235))
            painter.drawText(
                QRectF(self.width() - 34, 1 - z_offset, 30, 20),
                Qt.AlignmentFlag.AlignRight,
                "z Z Z",
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tucked_in_acc is not None:
                acc = self.tucked_in_acc
                self.tucked_in_acc = None
                if hasattr(acc, "occupant") and acc.occupant == self:
                    acc.occupant = None
                    acc.update()
            self.is_dragging = True
            self.drag_moved = False
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.state = "jump"
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self._open_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            if (new_pos - QPoint(int(self.pos_x), int(self.pos_y))).manhattanLength() > 5:
                self.drag_moved = True
            self.pos_x = float(new_pos.x())
            self.pos_y = float(new_pos.y())
            self.move(int(self.pos_x), int(self.pos_y))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.vel_y = 0.0
            if not self.drag_moved:
                self.set_behavior("sit", 8000)
                self.request_open_chat.emit(self.cat_id)

    def _open_context_menu(self, global_pos: QPoint):
        menu = QMenu()
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #1e202c;
                color: #f5f6fa;
                border: 1px solid #f28c28;
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
            QMenu::item {
                padding: 6px 18px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f28c28;
                color: #15161e;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background: #34384b;
                margin: 4px 8px;
            }
            """
        )

        title_act = menu.addAction(f"🐾 {self.name} ({self.coat})")
        title_act.setEnabled(False)
        menu.addSeparator()

        act_open_chat = menu.addAction(f"💬 Chatter avec {self.name} (Mémoire)")
        act_todo = menu.addAction(f"📋 To-Do List de {self.name} (Tâches à cocher)")
        act_quests = menu.addAction("🎯 Quêtes & Missions félines")
        act_gifts = menu.addAction("🎁 Trésors rapportés du PC")
        act_hunt = menu.addAction("🔍 Partir chercher un trésor sur le PC (IA)")
        act_laser = menu.addAction("🔴 Pointeur Laser (Activer / Éteindre)")
        act_pet = menu.addAction("✨ Caresser / Faire réagir (IA)")
        menu.addSeparator()

        act_think = menu.addAction("💭 Penser tout bas (IA)")
        act_speak = menu.addAction("💬 Dire sa pensée tout haut (IA)")
        act_check_todo = menu.addAction("📋 Demander l'avancement de la To-Do (IA)")
        act_chat = menu.addAction("🗣️ Discuter avec un autre chat")
        menu.addSeparator()

        act_jump = menu.addAction("🦘 Faire bondir / sauter")
        act_loaf = menu.addAction("🥖 Faire le pain (Loaf)")
        act_stretch = menu.addAction("🐾 S'étirer")
        act_purr = menu.addAction("💖 Ronronner")
        act_sleep = menu.addAction("💤 Faire dormir")
        act_walk = menu.addAction("🐾 Faire marcher")
        menu.addSeparator()

        act_cfg = menu.addAction("⚙️ Menu de configuration...")
        act_quit = menu.addAction("❌ Quitter Cat AI")

        chosen = menu.exec(global_pos)
        if chosen == act_open_chat:
            self.request_open_chat.emit(self.cat_id)
        elif chosen == act_todo:
            self.request_open_todo.emit(self.cat_id)
        elif chosen == act_quests:
            self.request_open_quests.emit(self.cat_id)
        elif chosen == act_gifts:
            self.request_open_gifts.emit(self.cat_id)
        elif chosen == act_hunt:
            self.request_hunt_treasure.emit(self.cat_id)
        elif chosen == act_laser:
            self.request_toggle_laser.emit()
        elif chosen == act_pet:
            self.set_behavior("purr", 4000)
            self.request_solo_thought.emit(
                self.cat_id, "L'humain me caresse et me donne une friandise !"
            )
        elif chosen == act_think:
            self.request_solo_thought.emit(self.cat_id, "")
        elif chosen == act_speak:
            self.request_speak_thought.emit(self.cat_id)
        elif chosen == act_check_todo:
            self.request_check_todo.emit(self.cat_id)
        elif chosen == act_chat:
            self.request_multi_chat.emit(self.cat_id)
        elif chosen == act_jump:
            self.perform_jump(random.uniform(11.5, 14.5))
        elif chosen == act_loaf:
            self.set_behavior("loaf", 15000)
        elif chosen == act_stretch:
            self.set_behavior("stretch", 6000)
        elif chosen == act_purr:
            self.set_behavior("purr", 10000)
        elif chosen == act_sleep:
            self.set_behavior("sleep", 15000)
        elif chosen == act_walk:
            self.set_behavior("walk", 8000)
        elif chosen == act_cfg:
            self.request_config.emit()
        elif chosen == act_quit:
            print(f"[Cat AI] Quitter demande depuis le menu contextuel du chat {self.name}", flush=True)
            self.request_quit.emit()

    def cleanup(self):
        self.anim_timer.stop()
        self.state_timer.stop()
        self.bubble.hide()
        self.bubble.deleteLater()
        self.hide()
        self.deleteLater()

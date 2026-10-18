from typing import Dict, Optional, Any, List
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextBrowser,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QPainterPath,
    QFont,
    QGuiApplication,
)

from memory_manager import MemoryManager
from task_manager import TaskManager
from quest_manager import QuestManager
from gift_manager import GiftManager


class CatChatBubble(QWidget):
    """Frameless custom-drawn mini chat, rules, to-do list, quests & treasures window floating directly above a cat's head."""

    send_user_message = pyqtSignal(str, str)  # (cat_id, message_text)
    closed_bubble = pyqtSignal(str)           # (cat_id)
    task_done_cheer = pyqtSignal(str, str)    # (cat_id, task_text)
    request_hunt_treasure = pyqtSignal(str)   # (cat_id)

    BUBBLE_W = 345
    BUBBLE_H = 310

    def __init__(
        self,
        cat_profile: Dict[str, str],
        memory_manager: MemoryManager,
        task_manager: TaskManager,
        quest_manager: Optional[QuestManager] = None,
        gift_manager: Optional[GiftManager] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.cat_id = cat_profile["id"]
        self.cat_name = cat_profile["name"]
        self.coat = cat_profile["coat"]
        self.personality = cat_profile["personality"]
        self.memory = memory_manager
        self.task_mgr = task_manager
        self.quest_mgr = quest_manager or QuestManager()
        self.gift_mgr = gift_manager or GiftManager()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(self.BUBBLE_W, self.BUBBLE_H)

        self._build_ui()
        self.refresh_chat_display()
        self.refresh_rules_list()
        self.refresh_todo_list()
        self.refresh_quests_display()
        self.refresh_gifts_display()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(11, 10, 11, 18)
        main_layout.setSpacing(4)

        self.stack = QStackedWidget(self)
        main_layout.addWidget(self.stack)

        # ================= PAGE 0: CHAT VIEW =================
        page_chat = QWidget()
        chat_layout = QVBoxLayout(page_chat)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(5)

        # Header Chat Navigation
        top_chat = QHBoxLayout()
        top_chat.setContentsMargins(0, 0, 0, 0)
        top_chat.setSpacing(3)

        self.title_lbl = QLabel(f"🐾 {self.cat_name}")
        self.title_lbl.setStyleSheet(
            "color: #ffb866; font-family: 'Segoe UI'; font-size: 8.5pt; font-weight: bold; background: transparent;"
        )

        self.btn_todo_tab = QPushButton("📋 To-Do")
        self.btn_todo_tab.setToolTip("Ouvrir la liste de tâches de ce chat")
        self.btn_todo_tab.setStyleSheet(
            """
            QPushButton {
                background: rgba(76, 175, 80, 0.2);
                color: #81c784;
                border: 1px solid rgba(76, 175, 80, 0.45);
                border-radius: 4px;
                padding: 1px 4px;
                font-family: 'Segoe UI';
                font-size: 7.5pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(76, 175, 80, 0.4);
                color: #ffffff;
            }
            """
        )
        self.btn_todo_tab.clicked.connect(self.switch_to_todo_page)

        self.btn_quests_tab = QPushButton("🎯 Quêtes")
        self.btn_quests_tab.setToolTip("Voir mes missions du jour & progression")
        self.btn_quests_tab.setStyleSheet(
            """
            QPushButton {
                background: rgba(156, 39, 176, 0.2);
                color: #ce93d8;
                border: 1px solid rgba(156, 39, 176, 0.5);
                border-radius: 4px;
                padding: 1px 4px;
                font-family: 'Segoe UI';
                font-size: 7.5pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(156, 39, 176, 0.4);
                color: #ffffff;
            }
            """
        )
        self.btn_quests_tab.clicked.connect(self.switch_to_quests_page)

        self.btn_gifts_tab = QPushButton("🎁 Trésors")
        self.btn_gifts_tab.setToolTip("Voir les trésors rapportés du PC")
        self.btn_gifts_tab.setStyleSheet(
            """
            QPushButton {
                background: rgba(255, 193, 7, 0.2);
                color: #ffd54f;
                border: 1px solid rgba(255, 193, 7, 0.5);
                border-radius: 4px;
                padding: 1px 4px;
                font-family: 'Segoe UI';
                font-size: 7.5pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 193, 7, 0.4);
                color: #ffffff;
            }
            """
        )
        self.btn_gifts_tab.clicked.connect(self.switch_to_gifts_page)

        self.btn_rules_tab = QPushButton("⚙️")
        self.btn_rules_tab.setToolTip("Configurer les répliques mémorisées")
        self.btn_rules_tab.setStyleSheet(
            """
            QPushButton {
                background: rgba(242, 140, 40, 0.18);
                color: #ffb866;
                border: 1px solid rgba(242, 140, 40, 0.5);
                border-radius: 4px;
                padding: 1px 4px;
                font-family: 'Segoe UI';
                font-size: 8pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(242, 140, 40, 0.35);
                color: #ffffff;
            }
            """
        )
        self.btn_rules_tab.clicked.connect(self._switch_to_rules_page)

        btn_close_chat = QPushButton("✕")
        btn_close_chat.setFixedSize(18, 18)
        btn_close_chat.setToolTip("Fermer la bulle")
        btn_close_chat.setStyleSheet(
            "QPushButton { background: transparent; color: #a9b4d4; border: none; font-weight: bold; font-size: 9pt; }"
            "QPushButton:hover { color: #ffb866; }"
        )
        btn_close_chat.clicked.connect(self.close_chat)

        top_chat.addWidget(self.title_lbl)
        top_chat.addStretch()
        top_chat.addWidget(self.btn_todo_tab)
        top_chat.addWidget(self.btn_quests_tab)
        top_chat.addWidget(self.btn_gifts_tab)
        top_chat.addWidget(self.btn_rules_tab)
        top_chat.addWidget(btn_close_chat)
        chat_layout.addLayout(top_chat)

        # Messages View
        self.chat_view = QTextBrowser()
        self.chat_view.setOpenExternalLinks(False)
        self.chat_view.setStyleSheet(
            """
            QTextBrowser {
                background-color: rgba(14, 16, 24, 195);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: #f0f2f8;
                font-family: 'Segoe UI', sans-serif;
                font-size: 8pt;
                padding: 4px;
            }
            """
        )
        chat_layout.addWidget(self.chat_view, 1)

        # Input Row
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(4)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText(f"Parle à {self.cat_name}... (Entrée)")
        self.input_edit.returnPressed.connect(self._on_send)
        self.input_edit.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(12, 14, 22, 220);
                border: 1px solid #f28c28;
                border-radius: 4px;
                padding: 3px 6px;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 8pt;
            }
            QLineEdit:focus {
                border: 1px solid #ffb866;
            }
            """
        )

        btn_send = QPushButton("🐾")
        btn_send.setFixedSize(26, 26)
        btn_send.setToolTip("Envoyer le message")
        btn_send.setStyleSheet(
            """
            QPushButton {
                background-color: #f28c28;
                border: none;
                border-radius: 4px;
                color: #14161f;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #ffa347;
            }
            """
        )
        btn_send.clicked.connect(self._on_send)

        bottom_row.addWidget(self.input_edit, 1)
        bottom_row.addWidget(btn_send)
        chat_layout.addLayout(bottom_row)

        self.stack.addWidget(page_chat)

        # ================= PAGE 1: RULES / REPLIQUES =================
        page_rules = QWidget()
        rules_layout = QVBoxLayout(page_rules)
        rules_layout.setContentsMargins(0, 0, 0, 0)
        rules_layout.setSpacing(4)

        top_rules = QHBoxLayout()
        top_rules.setContentsMargins(0, 0, 0, 0)
        top_rules.setSpacing(4)

        btn_back = QPushButton("← Chat")
        btn_back.setStyleSheet(
            """
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: #ffb866;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 3px;
                font-size: 8pt;
                padding: 1px 6px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
            """
        )
        btn_back.clicked.connect(self._switch_to_chat_page)

        rules_title = QLabel(f"⚙️ Répliques de {self.cat_name}")
        rules_title.setStyleSheet("color: #ffb866; font-weight: bold; font-size: 8.5pt;")

        btn_close_rules = QPushButton("✕")
        btn_close_rules.setFixedSize(18, 18)
        btn_close_rules.setStyleSheet(
            "QPushButton { background: transparent; color: #a9b4d4; border: none; font-weight: bold; font-size: 9pt; }"
            "QPushButton:hover { color: #ffb866; }"
        )
        btn_close_rules.clicked.connect(self.close_chat)

        top_rules.addWidget(btn_back)
        top_rules.addWidget(rules_title)
        top_rules.addStretch()
        top_rules.addWidget(btn_close_rules)
        rules_layout.addLayout(top_rules)

        self.rules_list_widget = QListWidget()
        self.rules_list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(14, 16, 24, 195);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                padding: 2px;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 8pt;
            }
            """
        )
        rules_layout.addWidget(self.rules_list_widget, 1)

        # Form add rule
        form_layout = QVBoxLayout()
        form_layout.setSpacing(2)

        row_trig = QHBoxLayout()
        lbl_trig = QLabel("Si je dis :")
        lbl_trig.setStyleSheet("color: #a9b4d4; font-size: 7.5pt;")
        self.rule_trig_edit = QLineEdit()
        self.rule_trig_edit.setPlaceholderText("Ex: 123")
        self.rule_trig_edit.setStyleSheet(
            "background: rgba(12,14,22,220); border: 1px solid #555; color: white; padding: 2px 4px; font-size: 8pt;"
        )
        row_trig.addWidget(lbl_trig)
        row_trig.addWidget(self.rule_trig_edit, 1)

        row_resp = QHBoxLayout()
        lbl_resp = QLabel("Tu dis :")
        lbl_resp.setStyleSheet("color: #a9b4d4; font-size: 7.5pt;")
        self.rule_resp_edit = QLineEdit()
        self.rule_resp_edit.setPlaceholderText("Ex: YUIOHN")
        self.rule_resp_edit.setStyleSheet(
            "background: rgba(12,14,22,220); border: 1px solid #555; color: white; padding: 2px 4px; font-size: 8pt;"
        )
        self.rule_resp_edit.returnPressed.connect(self._add_rule_clicked)
        row_resp.addWidget(lbl_resp)
        row_resp.addWidget(self.rule_resp_edit, 1)

        btn_add_rule = QPushButton("➕ Ajouter la réplique")
        btn_add_rule.setStyleSheet(
            """
            QPushButton {
                background-color: #f28c28;
                border: none;
                border-radius: 3px;
                color: #14161f;
                font-weight: bold;
                font-size: 8pt;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #ffa347;
            }
            """
        )
        btn_add_rule.clicked.connect(self._add_rule_clicked)

        form_layout.addLayout(row_trig)
        form_layout.addLayout(row_resp)
        form_layout.addWidget(btn_add_rule)
        rules_layout.addLayout(form_layout)

        self.stack.addWidget(page_rules)

        # ================= PAGE 2: TO-DO VIEW =================
        page_todo = QWidget()
        todo_layout = QVBoxLayout(page_todo)
        todo_layout.setContentsMargins(0, 0, 0, 0)
        todo_layout.setSpacing(4)

        top_todo = QHBoxLayout()
        top_todo.setContentsMargins(0, 0, 0, 0)
        top_todo.setSpacing(4)

        btn_back_todo = QPushButton("← Chat")
        btn_back_todo.setStyleSheet(
            """
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: #81c784;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 3px;
                font-size: 8pt;
                padding: 1px 6px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
            """
        )
        btn_back_todo.clicked.connect(self._switch_to_chat_page)

        self.todo_title = QLabel(f"📋 To-Do de {self.cat_name}")
        self.todo_title.setStyleSheet("color: #81c784; font-weight: bold; font-size: 8.5pt;")

        btn_clear_done = QPushButton("🧹 Nettoyer")
        btn_clear_done.setToolTip("Effacer les tâches déjà cochées")
        btn_clear_done.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                color: #a9b4d4;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 3px;
                font-size: 7.5pt;
                padding: 1px 4px;
            }
            QPushButton:hover {
                color: #ffadb5;
                border-color: #ffadb5;
            }
            """
        )
        btn_clear_done.clicked.connect(self._clear_done_tasks)

        btn_close_todo = QPushButton("✕")
        btn_close_todo.setFixedSize(18, 18)
        btn_close_todo.setStyleSheet(
            "QPushButton { background: transparent; color: #a9b4d4; border: none; font-weight: bold; font-size: 9pt; }"
            "QPushButton:hover { color: #ffb866; }"
        )
        btn_close_todo.clicked.connect(self.close_chat)

        top_todo.addWidget(btn_back_todo)
        top_todo.addWidget(self.todo_title)
        top_todo.addStretch()
        top_todo.addWidget(btn_clear_done)
        top_todo.addWidget(btn_close_todo)
        todo_layout.addLayout(top_todo)

        self.todo_list_widget = QListWidget()
        self.todo_list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(14, 16, 24, 195);
                border: 1px solid #2e4d35;
                border-radius: 5px;
                padding: 2px;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 8pt;
            }
            """
        )
        todo_layout.addWidget(self.todo_list_widget, 1)

        add_task_row = QHBoxLayout()
        add_task_row.setContentsMargins(0, 0, 0, 0)
        add_task_row.setSpacing(4)

        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText(f"Tâche pour {self.cat_name}... (Entrée)")
        self.todo_input.returnPressed.connect(self._add_task_clicked)
        self.todo_input.setStyleSheet(
            """
            QLineEdit {
                background-color: rgba(12, 14, 22, 220);
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 3px 6px;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 8pt;
            }
            QLineEdit:focus {
                border: 1px solid #81c784;
            }
            """
        )

        btn_add_task = QPushButton("➕")
        btn_add_task.setFixedSize(26, 26)
        btn_add_task.setStyleSheet(
            """
            QPushButton {
                background-color: #4caf50;
                border: none;
                border-radius: 4px;
                color: #14161f;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #66bb6a;
            }
            """
        )
        btn_add_task.clicked.connect(self._add_task_clicked)

        add_task_row.addWidget(self.todo_input, 1)
        add_task_row.addWidget(btn_add_task)
        todo_layout.addLayout(add_task_row)

        self.stack.addWidget(page_todo)

        # ================= PAGE 3: QUESTS VIEW =================
        page_quests = QWidget()
        quests_layout = QVBoxLayout(page_quests)
        quests_layout.setContentsMargins(0, 0, 0, 0)
        quests_layout.setSpacing(3)

        top_quests = QHBoxLayout()
        top_quests.setContentsMargins(0, 0, 0, 0)
        top_quests.setSpacing(4)

        btn_back_quests = QPushButton("← Chat")
        btn_back_quests.setStyleSheet(
            """
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: #ce93d8;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 3px;
                font-size: 8pt;
                padding: 1px 6px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.2); }
            """
        )
        btn_back_quests.clicked.connect(self._switch_to_chat_page)

        self.quests_title_lbl = QLabel("🎯 Missions & Quêtes")
        self.quests_title_lbl.setStyleSheet("color: #ce93d8; font-weight: bold; font-size: 8.5pt;")

        self.quests_level_badge = QLabel("Niv. 1")
        self.quests_level_badge.setStyleSheet(
            "color: #ffd54f; font-weight: bold; font-size: 7.5pt; "
            "background: rgba(255, 193, 7, 0.2); border-radius: 3px; padding: 1px 4px;"
        )

        btn_close_quests = QPushButton("✕")
        btn_close_quests.setFixedSize(18, 18)
        btn_close_quests.setStyleSheet(
            "QPushButton { background: transparent; color: #a9b4d4; border: none; font-weight: bold; font-size: 9pt; }"
            "QPushButton:hover { color: #ffb866; }"
        )
        btn_close_quests.clicked.connect(self.close_chat)

        top_quests.addWidget(btn_back_quests)
        top_quests.addWidget(self.quests_title_lbl)
        top_quests.addWidget(self.quests_level_badge)
        top_quests.addStretch()
        top_quests.addWidget(btn_close_quests)
        quests_layout.addLayout(top_quests)

        # XP Bar
        xp_row = QHBoxLayout()
        xp_row.setSpacing(4)
        self.xp_bar = QProgressBar()
        self.xp_bar.setFixedHeight(8)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: rgba(20, 22, 34, 180);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ba68c8, stop:1 #ffd54f);
                border-radius: 3px;
            }
            """
        )
        self.xp_lbl = QLabel("0/150 XP")
        self.xp_lbl.setStyleSheet("color: #b0bec5; font-size: 7pt;")
        xp_row.addWidget(self.xp_bar, 1)
        xp_row.addWidget(self.xp_lbl)
        quests_layout.addLayout(xp_row)

        self.quests_list_widget = QListWidget()
        self.quests_list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(14, 16, 24, 195);
                border: 1px solid #4a148c;
                border-radius: 5px;
                padding: 2px;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 8pt;
            }
            """
        )
        quests_layout.addWidget(self.quests_list_widget, 1)

        bottom_q_row = QHBoxLayout()
        btn_refresh_q = QPushButton("🔄 Nouvelles quêtes")
        btn_refresh_q.setStyleSheet(
            """
            QPushButton {
                background: rgba(156, 39, 176, 0.25);
                color: #e1bee7;
                border: 1px solid rgba(156, 39, 176, 0.5);
                border-radius: 3px;
                font-size: 7.5pt;
                padding: 2px 6px;
            }
            QPushButton:hover { background: rgba(156, 39, 176, 0.45); color: #fff; }
            """
        )
        btn_refresh_q.clicked.connect(self._refresh_quests_clicked)
        bottom_q_row.addStretch()
        bottom_q_row.addWidget(btn_refresh_q)
        quests_layout.addLayout(bottom_q_row)

        self.stack.addWidget(page_quests)

        # ================= PAGE 4: GIFTS VIEW =================
        page_gifts = QWidget()
        gifts_layout = QVBoxLayout(page_gifts)
        gifts_layout.setContentsMargins(0, 0, 0, 0)
        gifts_layout.setSpacing(4)

        top_gifts = QHBoxLayout()
        top_gifts.setContentsMargins(0, 0, 0, 0)
        top_gifts.setSpacing(4)

        btn_back_gifts = QPushButton("← Chat")
        btn_back_gifts.setStyleSheet(
            """
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: #ffd54f;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 3px;
                font-size: 8pt;
                padding: 1px 6px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.2); }
            """
        )
        btn_back_gifts.clicked.connect(self._switch_to_chat_page)

        gifts_title = QLabel("🎁 Trésors rapportés du PC")
        gifts_title.setStyleSheet("color: #ffd54f; font-weight: bold; font-size: 8.5pt;")

        btn_hunt = QPushButton("🔍 Fouiller le PC")
        btn_hunt.setToolTip("Envoyer le chat explorer le PC pour chercher un trésor")
        btn_hunt.setStyleSheet(
            """
            QPushButton {
                background: rgba(255, 193, 7, 0.25);
                color: #ffe082;
                border: 1px solid rgba(255, 193, 7, 0.5);
                border-radius: 3px;
                font-size: 7.5pt;
                padding: 1px 5px;
            }
            QPushButton:hover { background: rgba(255, 193, 7, 0.45); color: #fff; }
            """
        )
        btn_hunt.clicked.connect(self._hunt_treasure_clicked)

        btn_close_gifts = QPushButton("✕")
        btn_close_gifts.setFixedSize(18, 18)
        btn_close_gifts.setStyleSheet(
            "QPushButton { background: transparent; color: #a9b4d4; border: none; font-weight: bold; font-size: 9pt; }"
            "QPushButton:hover { color: #ffb866; }"
        )
        btn_close_gifts.clicked.connect(self.close_chat)

        top_gifts.addWidget(btn_back_gifts)
        top_gifts.addWidget(gifts_title)
        top_gifts.addStretch()
        top_gifts.addWidget(btn_hunt)
        top_gifts.addWidget(btn_close_gifts)
        gifts_layout.addLayout(top_gifts)

        self.gifts_list_widget = QListWidget()
        self.gifts_list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(14, 16, 24, 195);
                border: 1px solid #ff8f00;
                border-radius: 5px;
                padding: 2px;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 8pt;
            }
            """
        )
        gifts_layout.addWidget(self.gifts_list_widget, 1)

        self.stack.addWidget(page_gifts)

    # --- PAGE NAVIGATION ---
    def _switch_to_rules_page(self):
        self.refresh_rules_list()
        self.stack.setCurrentIndex(1)
        self.rule_trig_edit.setFocus()

    def switch_to_todo_page(self):
        self.refresh_todo_list()
        self.stack.setCurrentIndex(2)
        self.todo_input.setFocus()

    def switch_to_quests_page(self):
        self.refresh_quests_display()
        self.stack.setCurrentIndex(3)

    def switch_to_gifts_page(self):
        self.refresh_gifts_display()
        self.stack.setCurrentIndex(4)

    def _switch_to_chat_page(self):
        self.stack.setCurrentIndex(0)
        self.input_edit.setFocus()

    # --- TO-DO METHODS ---
    def refresh_todo_list(self):
        tasks = self.task_mgr.get_tasks(self.cat_id)
        undone = sum(1 for t in tasks if not t["done"])
        self.btn_todo_tab.setText(f"📋 To-Do ({undone})")

        self.todo_list_widget.clear()
        if not tasks:
            item = QListWidgetItem("Toutes les tâches sont terminées ! 🎉")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(QColor("#81c784"))
            self.todo_list_widget.addItem(item)
            return

        for task in tasks:
            item = QListWidgetItem()
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(3, 2, 3, 2)
            row_layout.setSpacing(6)

            chk = QCheckBox(task["text"])
            chk.setChecked(task["done"])
            if task["done"]:
                chk.setStyleSheet(
                    "QCheckBox { color: #727e99; text-decoration: line-through; font-size: 8pt; }"
                    "QCheckBox::indicator { width: 14px; height: 14px; }"
                )
            else:
                chk.setStyleSheet(
                    "QCheckBox { color: #f2f4fa; font-size: 8pt; }"
                    "QCheckBox::indicator { width: 14px; height: 14px; }"
                )

            tid = task["id"]
            ttext = task["text"]
            chk.toggled.connect(lambda checked, tid=tid, txt=ttext: self._on_task_toggled(tid, txt, checked))

            btn_del = QPushButton("✕")
            btn_del.setFixedSize(16, 16)
            btn_del.setStyleSheet(
                "QPushButton { background: transparent; color: #667085; border: none; font-size: 7pt; }"
                "QPushButton:hover { color: #ff8a96; font-weight: bold; }"
            )
            btn_del.clicked.connect(lambda _, tid=tid: self._delete_task(tid))

            row_layout.addWidget(chk, 1)
            row_layout.addWidget(btn_del)

            item.setSizeHint(row_widget.sizeHint())
            self.todo_list_widget.addItem(item)
            self.todo_list_widget.setItemWidget(item, row_widget)

    def _on_task_toggled(self, task_id: str, task_text: str, checked: bool):
        self.task_mgr.set_task_done(self.cat_id, task_id, checked)
        if checked:
            self.task_done_cheer.emit(self.cat_id, task_text)
        self.refresh_todo_list()

    def _add_task_clicked(self):
        text = self.todo_input.text().strip()
        if text:
            self.task_mgr.add_task(self.cat_id, text)
            self.todo_input.clear()
            self.refresh_todo_list()

    def _delete_task(self, task_id: str):
        self.task_mgr.remove_task(self.cat_id, task_id)
        self.refresh_todo_list()

    def _clear_done_tasks(self):
        self.task_mgr.clear_completed(self.cat_id)
        self.refresh_todo_list()

    # --- QUESTS METHODS ---
    def refresh_quests_display(self):
        stats = self.quest_mgr.get_player_stats()
        self.quests_level_badge.setText(f"Niv. {stats['level']}")
        self.xp_bar.setMaximum(stats["xp_for_next"])
        self.xp_bar.setValue(stats["xp_in_level"])
        self.xp_lbl.setText(f"{stats['xp_in_level']}/{stats['xp_for_next']} XP (Total : {stats['xp']} XP)")

        quests = self.quest_mgr.get_active_quests()
        self.quests_list_widget.clear()

        for q in quests:
            item = QListWidgetItem()
            w = QWidget()
            layout = QVBoxLayout(w)
            layout.setContentsMargins(4, 3, 4, 3)
            layout.setSpacing(1)

            top_row = QHBoxLayout()
            top_row.setSpacing(4)

            icon_lbl = QLabel(q.get("icon", "🎯"))
            icon_lbl.setStyleSheet("font-size: 9pt;")

            title_lbl = QLabel(q["title"])
            if q["completed"]:
                title_lbl.setStyleSheet("color: #81c784; font-weight: bold; font-size: 8pt; text-decoration: line-through;")
                status_lbl = QLabel(f"✅ Terminé ! (+{q['reward_xp']} XP)")
                status_lbl.setStyleSheet("color: #81c784; font-weight: bold; font-size: 7.5pt;")
            else:
                title_lbl.setStyleSheet("color: #f3e5f5; font-weight: bold; font-size: 8pt;")
                status_lbl = QLabel(f"{q['current_count']}/{q['target_count']} (+{q['reward_xp']} XP)")
                status_lbl.setStyleSheet("color: #ce93d8; font-weight: bold; font-size: 7.5pt;")

            top_row.addWidget(icon_lbl)
            top_row.addWidget(title_lbl, 1)
            top_row.addWidget(status_lbl)
            layout.addLayout(top_row)

            desc_lbl = QLabel(q["description"])
            desc_lbl.setStyleSheet("color: #b0bec5; font-size: 7pt; margin-left: 14px;")
            layout.addWidget(desc_lbl)

            item.setSizeHint(w.sizeHint())
            self.quests_list_widget.addItem(item)
            self.quests_list_widget.setItemWidget(item, w)

    def _refresh_quests_clicked(self):
        self.quest_mgr.refresh_quests_manual()
        self.refresh_quests_display()

    # --- GIFTS METHODS ---
    def refresh_gifts_display(self):
        gifts = self.gift_mgr.get_all_gifts()
        self.gifts_list_widget.clear()

        if not gifts:
            item = QListWidgetItem("Aucun trésor trouvé pour l'instant. Clique sur 'Fouiller le PC' !")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(QColor("#ffd54f"))
            self.gifts_list_widget.addItem(item)
            return

        for g in gifts:
            item = QListWidgetItem()
            w = QWidget()
            layout = QVBoxLayout(w)
            layout.setContentsMargins(4, 3, 4, 3)
            layout.setSpacing(1)

            top_row = QHBoxLayout()
            top_row.setSpacing(4)

            icon_lbl = QLabel(g.get("icon", "🎁"))
            icon_lbl.setStyleSheet("font-size: 10pt;")

            name_lbl = QLabel(g["name"])
            name_color = g.get("color", "#ffd700")
            name_lbl.setStyleSheet(f"color: {name_color}; font-weight: bold; font-size: 8pt;")

            rarity_lbl = QLabel(f"[{g.get('rarity', 'Rare')}]")
            rarity_lbl.setStyleSheet(f"color: {name_color}; font-size: 7pt; font-weight: bold;")

            top_row.addWidget(icon_lbl)
            top_row.addWidget(name_lbl, 1)
            top_row.addWidget(rarity_lbl)
            layout.addLayout(top_row)

            info_lbl = QLabel(f"Par {g.get('found_by', 'Chat')} le {g.get('found_at', '')}")
            info_lbl.setStyleSheet("color: #90a4ae; font-size: 6.8pt; margin-left: 16px;")
            layout.addWidget(info_lbl)

            lore_lbl = QLabel(f"« {g.get('lore', '')} »")
            lore_lbl.setWordWrap(True)
            lore_lbl.setStyleSheet("color: #eceff1; font-style: italic; font-size: 7pt; margin-left: 16px;")
            layout.addWidget(lore_lbl)

            item.setSizeHint(w.sizeHint())
            self.gifts_list_widget.addItem(item)
            self.gifts_list_widget.setItemWidget(item, w)

    def _hunt_treasure_clicked(self):
        self.request_hunt_treasure.emit(self.cat_id)
        self.close_chat()

    # --- RULES METHODS ---
    def refresh_rules_list(self):
        rules = self.memory.get_rules(self.cat_id)
        self.btn_rules_tab.setText("⚙️" if not rules else f"⚙️ ({len(rules)})")
        self.rules_list_widget.clear()

        if not rules:
            item = QListWidgetItem("Aucune réplique mémorisée pour l'instant.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(QColor("#7e8a9b"))
            self.rules_list_widget.addItem(item)
            return

        for trig, resp in rules.items():
            item = QListWidgetItem()
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(2, 2, 2, 2)
            row_layout.setSpacing(4)

            lbl = QLabel(f"<b>« {trig} »</b> ➔ <i>« {resp} »</i>")
            lbl.setStyleSheet("color: #f2f4fa; font-size: 7.8pt;")

            btn_del = QPushButton("✕")
            btn_del.setFixedSize(16, 16)
            btn_del.setStyleSheet(
                "QPushButton { background: transparent; color: #a9b4d4; border: none; font-size: 7pt; }"
                "QPushButton:hover { color: #ff8a96; font-weight: bold; }"
            )
            btn_del.clicked.connect(lambda _, t=trig: self._delete_rule(t))

            row_layout.addWidget(lbl, 1)
            row_layout.addWidget(btn_del)

            item.setSizeHint(row_widget.sizeHint())
            self.rules_list_widget.addItem(item)
            self.rules_list_widget.setItemWidget(item, row_widget)

    def _add_rule_clicked(self):
        trig = self.rule_trig_edit.text().strip()
        resp = self.rule_resp_edit.text().strip()
        if trig and resp:
            self.memory.add_rule(self.cat_id, trig, resp)
            self.rule_trig_edit.clear()
            self.rule_resp_edit.clear()
            self.refresh_rules_list()

    def _delete_rule(self, trigger: str):
        self.memory.delete_rule(self.cat_id, trigger)
        self.refresh_rules_list()

    def open_above(self, center_x: int, top_y: int, page_index: int = 0):
        w = self.width()
        h = self.height()
        target_x = center_x - w // 2
        target_y = top_y - h - 14

        screens = QGuiApplication.screens()
        for scr in screens:
            geom = scr.availableGeometry()
            if geom.contains(center_x, top_y):
                target_x = max(geom.left() + 10, min(target_x, geom.right() - w - 10))
                if target_y < geom.top() + 10:
                    target_y = top_y + 90
                break

        self.move(int(target_x), int(target_y))
        if page_index == 1:
            self._switch_to_rules_page()
        elif page_index == 2:
            self.switch_to_todo_page()
        elif page_index == 3:
            self.switch_to_quests_page()
        elif page_index == 4:
            self.switch_to_gifts_page()
        else:
            self._switch_to_chat_page()

        self.show()
        self.raise_()
        self.activateWindow()

    def update_anchor(self, center_x: int, top_y: int):
        if not self.isVisible():
            return
        w = self.width()
        h = self.height()
        target_x = center_x - w // 2
        target_y = top_y - h - 14

        screens = QGuiApplication.screens()
        for scr in screens:
            geom = scr.availableGeometry()
            if geom.contains(center_x, top_y):
                target_x = max(geom.left() + 10, min(target_x, geom.right() - w - 10))
                if target_y < geom.top() + 10:
                    target_y = top_y + 90
                break
        self.move(int(target_x), int(target_y))

    def close_chat(self):
        self.hide()
        self.closed_bubble.emit(self.cat_id)

    def refresh_chat_display(self, waiting_ai: bool = False):
        history = self.memory.get_history(self.cat_id)
        html_lines = []

        if not history:
            html_lines.append(
                f"<div style='color:#a9b4d4; font-style:italic; padding:4px;'>"
                f"Miaou ! Dis-moi quelque chose, ou ouvre la To-Do List avec 📋 ci-dessus 🐾</div>"
            )
        else:
            for msg in history[-14:]:
                role = msg.get("role", "user")
                text = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;")
                if role == "user":
                    html_lines.append(
                        f"<div style='margin-bottom:3px;'>"
                        f"<b style='color:#7ec8ff;'>Toi :</b> <span style='color:#e8ecf7;'>{text}</span></div>"
                    )
                else:
                    html_lines.append(
                        f"<div style='margin-bottom:4px;'>"
                        f"<b style='color:#ffb866;'>{self.cat_name} :</b> <span style='color:#fff2d6;'>{text}</span></div>"
                    )

        if waiting_ai:
            html_lines.append(
                f"<div style='color:#ffb866; font-style:italic;'>💭 {self.cat_name} écrit...</div>"
            )

        self.chat_view.setHtml("".join(html_lines))
        sb = self.chat_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_send(self):
        text = self.input_edit.text().strip()
        if not text:
            return
        self.input_edit.clear()
        self.memory.add_message(self.cat_id, "user", text)
        self.refresh_chat_display(waiting_ai=True)
        self.send_user_message.emit(self.cat_id, text)

    def on_ai_reply_received(self):
        self.refresh_chat_display(waiting_ai=False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height() - 10

        bg_color = QColor(22, 24, 36, 246)
        border_color = QColor(242, 140, 40, 248)

        path = QPainterPath()
        path.addRoundedRect(QRectF(2, 2, w - 4, h - 2), 10, 10)

        cx = w / 2.0
        path.moveTo(cx - 8, h)
        path.lineTo(cx, h + 9)
        path.lineTo(cx + 8, h)

        painter.setPen(QPen(border_color, 2))
        painter.setBrush(bg_color)
        painter.drawPath(path)

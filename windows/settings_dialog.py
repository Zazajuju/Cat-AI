import uuid
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QSlider,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QCheckBox,
    QFormLayout,
    QMessageBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QGuiApplication, QCursor

from config import ConfigManager, COAT_STYLES, PERSONALITY_PRESETS
from sprites import SpriteBank
from ollama_worker import fetch_ollama_models


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()
    trigger_test_thought = pyqtSignal()
    trigger_test_chat = pyqtSignal()
    request_open_chat_for_cat = pyqtSignal(str)
    request_quit_app = pyqtSignal()

    def __init__(self, config: ConfigManager, sprite_bank: SpriteBank, memory_manager=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.sprite_bank = sprite_bank
        self.memory = memory_manager
        self.setWindowTitle("🐾 Cat AI - Menu de Configuration & Répliques")
        self.setMinimumSize(820, 680)
        self.resize(860, 710)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        self.cats_list: List[Dict[str, str]] = [
            dict(c) for c in self.config.get("cats", [])
        ]
        self.current_cat_idx: int = -1
        self.preview_frame = 0

        self._apply_theme()
        self._build_ui()
        self._load_from_config()
        self._center_on_cursor_screen()

        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self._animate_preview)
        self.preview_timer.start(240)

    def _center_on_cursor_screen(self):
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.center().x() - self.width() // 2
            y = geo.center().y() - self.height() // 2
            self.move(x, y)

    def _apply_theme(self):
        self.setStyleSheet(
            """
            QDialog {
                background-color: #161822;
                color: #f0f2f8;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
            QGroupBox {
                background-color: #1f2230;
                border: 1px solid #32374d;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
                font-weight: bold;
                color: #ffb35c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QLabel {
                color: #e4e7f2;
            }
            QLineEdit, QComboBox {
                background-color: #12141c;
                border: 1px solid #3a405a;
                border-radius: 5px;
                padding: 5px 8px;
                color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #f28c28;
            }
            QListWidget {
                background-color: #12141c;
                border: 1px solid #3a405a;
                border-radius: 6px;
                padding: 4px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #f28c28;
                color: #14161f;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2b3044;
                border: 1px solid #434a66;
                border-radius: 6px;
                padding: 6px 14px;
                color: #f5f6fa;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #383f58;
                border-color: #f28c28;
            }
            QPushButton#primaryBtn {
                background-color: #f28c28;
                border-color: #ffa64d;
                color: #14161f;
                font-weight: bold;
            }
            QPushButton#primaryBtn:hover {
                background-color: #ffa347;
            }
            QPushButton#dangerBtn {
                background-color: #4a2328;
                border-color: #80343d;
                color: #ffadb5;
            }
            QPushButton#dangerBtn:hover {
                background-color: #692c34;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #12141c;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #f28c28;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffd099;
                border: 2px solid #f28c28;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QTabWidget::pane {
                border: 1px solid #32374d;
                background-color: #171924;
                border-radius: 6px;
                padding: 6px;
            }
            QTabBar::tab {
                background-color: #1a1c29;
                color: #a3adc9;
                padding: 6px 14px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 600;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #262a3d;
                color: #ffb866;
                border-bottom: 2px solid #f28c28;
            }
            QTableWidget {
                background-color: #12141c;
                border: 1px solid #32374d;
                border-radius: 6px;
                color: #ffffff;
                gridline-color: #242838;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #342845;
                color: #ffb866;
            }
            QHeaderView::section {
                background-color: #1a1d2b;
                color: #ffb35c;
                padding: 5px;
                font-weight: bold;
                border: 1px solid #2e3347;
            }
            """
        )

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        top_row = QHBoxLayout()

        # 1. Ollama Group
        ollama_group = QGroupBox("🤖 Connexion IA (Ollama)")
        ollama_form = QFormLayout(ollama_group)

        model_row = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems(["gemma3:1b", "gemma3:270m"])
        btn_refresh = QPushButton("🔄")
        btn_refresh.setToolTip("Détecter les modèles Ollama installés")
        btn_refresh.setFixedWidth(36)
        btn_refresh.clicked.connect(lambda: self._refresh_ollama_status())
        model_row.addWidget(self.model_combo, 1)
        model_row.addWidget(btn_refresh)

        self.url_edit = QLineEdit()
        self.status_label = QLabel("Vérification...")

        ollama_form.addRow("Modèle Gemma :", model_row)
        ollama_form.addRow("URL Ollama :", self.url_edit)
        ollama_form.addRow("Statut :", self.status_label)

        test_btns = QHBoxLayout()
        btn_test_thought = QPushButton("💭 Tester une pensée")
        btn_test_thought.clicked.connect(self.trigger_test_thought.emit)
        btn_test_chat = QPushButton("🗣️ Tester un dialogue")
        btn_test_chat.clicked.connect(self.trigger_test_chat.emit)
        test_btns.addWidget(btn_test_thought)
        test_btns.addWidget(btn_test_chat)
        ollama_form.addRow(test_btns)

        # 2. General Settings Group
        general_group = QGroupBox("⚙️ Affichage & Comportement")
        gen_form = QFormLayout(general_group)

        # Screen selector
        self.screen_combo = QComboBox()
        self.screen_combo.addItem("🖥️ Tous les écrans (Multi-écran)", "all")
        for idx, scr in enumerate(QGuiApplication.screens()):
            geo = scr.geometry()
            self.screen_combo.addItem(
                f"Écran {idx + 1} - {scr.name()} ({geo.width()}x{geo.height()})",
                str(idx),
            )

        # Size slider
        size_row = QHBoxLayout()
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(2, 8)
        self.scale_val_lbl = QLabel("5x")
        self.scale_val_lbl.setFixedWidth(36)
        self.scale_slider.valueChanged.connect(
            lambda v: self.scale_val_lbl.setText(f"{v}x")
        )
        size_row.addWidget(self.scale_slider)
        size_row.addWidget(self.scale_val_lbl)

        # Speed slider
        speed_row = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 45)
        self.speed_val_lbl = QLabel("1.8")
        self.speed_val_lbl.setFixedWidth(36)
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_val_lbl.setText(f"{v / 10.0:.1f}")
        )
        speed_row.addWidget(self.speed_slider)
        speed_row.addWidget(self.speed_val_lbl)

        # Thought frequency slider
        thought_row = QHBoxLayout()
        self.thought_slider = QSlider(Qt.Orientation.Horizontal)
        self.thought_slider.setRange(8, 120)
        self.thought_val_lbl = QLabel("20s")
        self.thought_val_lbl.setFixedWidth(36)
        self.thought_slider.valueChanged.connect(
            lambda v: self.thought_val_lbl.setText(f"{v}s")
        )
        thought_row.addWidget(self.thought_slider)
        thought_row.addWidget(self.thought_val_lbl)

        # Multi-cat chat frequency slider
        chat_row = QHBoxLayout()
        self.chat_slider = QSlider(Qt.Orientation.Horizontal)
        self.chat_slider.setRange(15, 180)
        self.chat_val_lbl = QLabel("40s")
        self.chat_val_lbl.setFixedWidth(36)
        self.chat_slider.valueChanged.connect(
            lambda v: self.chat_val_lbl.setText(f"{v}s")
        )
        chat_row.addWidget(self.chat_slider)
        chat_row.addWidget(self.chat_val_lbl)

        self.day_night_combo = QComboBox()
        self.day_night_combo.addItem("🌙 Automatique (selon l'heure réelle)", "auto")
        self.day_night_combo.addItem("☀️ Toujours Jour (chats actifs)", "day")
        self.day_night_combo.addItem("🌙 Toujours Nuit (siestes & calme)", "night")

        self.chk_interactions = QCheckBox("Activer les discussions entre chats")
        self.chk_show_names = QCheckBox("Afficher le nom au-dessus des chats")
        self.chk_laser = QCheckBox("🔴 Activer le pointeur laser rouge (souris)")

        gen_form.addRow("Écran :", self.screen_combo)
        gen_form.addRow("Cycle Jour / Nuit :", self.day_night_combo)
        gen_form.addRow("Taille (Pixels) :", size_row)
        gen_form.addRow("Vitesse marche :", speed_row)
        gen_form.addRow("Fréquence pensées :", thought_row)
        gen_form.addRow("Fréquence dialogues :", chat_row)
        gen_form.addRow("", self.chk_interactions)
        gen_form.addRow("", self.chk_show_names)
        gen_form.addRow("", self.chk_laser)

        top_row.addWidget(ollama_group, 1)
        top_row.addWidget(general_group, 1)
        main_layout.addLayout(top_row)

        # --- CATS MANAGER ---
        cats_group = QGroupBox("🐱 Gestion de vos Chats sur la Barre des Tâches")
        cats_layout = QHBoxLayout(cats_group)

        left_col = QVBoxLayout()
        self.cat_list_widget = QListWidget()
        self.cat_list_widget.setIconSize(QSize(40, 32))
        self.cat_list_widget.currentRowChanged.connect(self._on_cat_selected)
        left_col.addWidget(self.cat_list_widget)

        list_btns = QHBoxLayout()
        btn_add_cat = QPushButton("➕ Ajouter un chat")
        btn_add_cat.clicked.connect(self._add_cat)
        self.btn_remove_cat = QPushButton("🗑️ Supprimer")
        self.btn_remove_cat.setObjectName("dangerBtn")
        self.btn_remove_cat.clicked.connect(self._remove_cat)
        list_btns.addWidget(btn_add_cat)
        list_btns.addWidget(self.btn_remove_cat)
        left_col.addLayout(list_btns)

        right_col = QVBoxLayout()
        preview_box = QHBoxLayout()
        self.preview_lbl = QLabel()
        self.preview_lbl.setFixedSize(110, 90)
        self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_lbl.setStyleSheet(
            "background-color: #12141c; border: 1px solid #3a405a; border-radius: 8px;"
        )

        editor_form = QFormLayout()
        self.cat_name_edit = QLineEdit()
        self.cat_name_edit.textEdited.connect(self._on_cat_field_edited)

        self.cat_coat_combo = QComboBox()
        self.cat_coat_combo.addItems(COAT_STYLES)
        self.cat_coat_combo.currentTextChanged.connect(self._on_cat_field_edited)

        editor_form.addRow("Nom du chat :", self.cat_name_edit)
        editor_form.addRow("Pelage / Couleur :", self.cat_coat_combo)

        preview_box.addWidget(self.preview_lbl)
        preview_box.addLayout(editor_form, 1)
        right_col.addLayout(preview_box)

        self.cat_detail_tabs = QTabWidget()

        # Tab 1: Personnalité IA
        tab_pers = QWidget()
        pers_layout = QVBoxLayout(tab_pers)
        pers_layout.setSpacing(8)

        pers_form = QFormLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("✨ Choisir un modèle de personnalité...")
        self.preset_combo.addItems(PERSONALITY_PRESETS)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_chosen)

        self.cat_pers_edit = QLineEdit()
        self.cat_pers_edit.setPlaceholderText(
            "Décrivez le caractère du chat pour Gemma 3..."
        )
        self.cat_pers_edit.textEdited.connect(self._on_cat_field_edited)

        pers_form.addRow("Idée rapide :", self.preset_combo)
        pers_form.addRow("Personnalité IA :", self.cat_pers_edit)
        pers_layout.addLayout(pers_form)

        mem_info_row = QHBoxLayout()
        self.cat_memory_info_lbl = QLabel("🧠 Mémoire : 0 fait(s) mémorisé(s)")
        self.cat_memory_info_lbl.setStyleSheet("color: #a4adc6; font-size: 8.5pt;")
        btn_clean_mem = QPushButton("🧹 Nettoyer souvenirs")
        btn_clean_mem.setToolTip("Élimine les phrases parasites ou placeholders")
        btn_clean_mem.clicked.connect(self._clean_current_cat_memory)
        btn_reset_mem = QPushButton("🗑️ Tout effacer")
        btn_reset_mem.setObjectName("dangerBtn")
        btn_reset_mem.setToolTip("Réinitialise la mémoire et l'historique de ce chat")
        btn_reset_mem.clicked.connect(self._reset_current_cat_memory)

        mem_info_row.addWidget(self.cat_memory_info_lbl, 1)
        mem_info_row.addWidget(btn_clean_mem)
        mem_info_row.addWidget(btn_reset_mem)
        pers_layout.addLayout(mem_info_row)
        pers_layout.addStretch()

        # Tab 2: Réponses & Répliques programmées (Quand je dis X -> Le chat dit Y)
        tab_rules = QWidget()
        rules_layout = QVBoxLayout(tab_rules)
        rules_layout.setSpacing(6)

        rules_tip = QLabel("✨ Définissez des répliques exactes : Quand vous dites ça -> Le chat répond obligatoirement ça !")
        rules_tip.setStyleSheet("color: #ffb866; font-size: 8.5pt; font-weight: bold;")
        rules_layout.addWidget(rules_tip)

        self.rules_table = QTableWidget(0, 2)
        self.rules_table.setHorizontalHeaderLabels(["🗣️ Quand je dis...", "🐱 Le chat répond..."])
        self.rules_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.rules_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.rules_table.itemSelectionChanged.connect(self._on_rule_row_selected)
        rules_layout.addWidget(self.rules_table, 1)

        # Inputs to add/modify rule
        rule_input_row = QHBoxLayout()
        self.rule_trig_input = QLineEdit()
        self.rule_trig_input.setPlaceholderText("Quand vous dites (ex: 1234, croquette)...")
        self.rule_resp_input = QLineEdit()
        self.rule_resp_input.setPlaceholderText("Le chat répond (ex: 56789, Miam miam !)...")
        rule_input_row.addWidget(self.rule_trig_input, 2)
        rule_input_row.addWidget(self.rule_resp_input, 3)

        btn_save_rule = QPushButton("➕ Ajouter / Modifier")
        btn_save_rule.setObjectName("primaryBtn")
        btn_save_rule.clicked.connect(self._add_or_update_rule)
        self.btn_del_rule = QPushButton("🗑️ Retirer")
        self.btn_del_rule.setObjectName("dangerBtn")
        self.btn_del_rule.clicked.connect(self._delete_selected_rule)
        rule_input_row.addWidget(btn_save_rule)
        rule_input_row.addWidget(self.btn_del_rule)
        rules_layout.addLayout(rule_input_row)

        # Quick preset packs
        packs_row = QHBoxLayout()
        pack_lbl = QLabel("Packs rapides :")
        pack_lbl.setStyleSheet("color: #a4adc6; font-size: 8pt;")
        packs_row.addWidget(pack_lbl)

        btn_pack_food = QPushButton("🐟 Thon & Croquette")
        btn_pack_food.setToolTip("Ajoute les règles : 'croquette' -> 'Miam !' et 'poisson' -> 'Donne le saumon !'")
        btn_pack_food.clicked.connect(lambda: self._apply_rule_pack("food"))

        btn_pack_love = QPushButton("❤️ Câlins")
        btn_pack_love.setToolTip("Ajoute les règles : 'bon chat' -> '*ronronne*' et 'je t'aime' -> 'Miaou ❤️'")
        btn_pack_love.clicked.connect(lambda: self._apply_rule_pack("love"))

        btn_pack_code = QPushButton("🔢 Code 1234")
        btn_pack_code.setToolTip("Ajoute la règle : '1234' -> '56789'")
        btn_pack_code.clicked.connect(lambda: self._apply_rule_pack("code"))

        packs_row.addWidget(btn_pack_food)
        packs_row.addWidget(btn_pack_love)
        packs_row.addWidget(btn_pack_code)
        packs_row.addStretch()
        rules_layout.addLayout(packs_row)

        self.cat_detail_tabs.addTab(tab_pers, "🎭 Personnalité IA")
        self.cat_detail_tabs.addTab(tab_rules, "💬 Répliques programmées")
        right_col.addWidget(self.cat_detail_tabs, 1)

        btn_chat_cat = QPushButton("💬 Chatter en direct avec ce chat (Bulle sur l'écran) 🐾")
        btn_chat_cat.setObjectName("primaryBtn")
        btn_chat_cat.clicked.connect(self._open_selected_cat_chat)
        right_col.addWidget(btn_chat_cat)

        cats_layout.addLayout(left_col, 2)
        cats_layout.addLayout(right_col, 3)
        main_layout.addWidget(cats_group, 1)

        # --- BOTTOM BUTTONS ---
        bottom_row = QHBoxLayout()
        btn_quit_game = QPushButton("❌ Quitter le jeu")
        btn_quit_game.setObjectName("dangerBtn")
        btn_quit_game.clicked.connect(self.request_quit_app.emit)
        bottom_row.addWidget(btn_quit_game)

        tip_lbl = QLabel(
            "💡 Fermer cette fenêtre laisse les chats se balader en bas de l'écran (Clic droit sur un chat pour rouvrir)"
        )
        tip_lbl.setStyleSheet("color: #9aa2bf; font-size: 9pt;")
        bottom_row.addWidget(tip_lbl)
        bottom_row.addStretch()

        btn_apply = QPushButton("💾 Appliquer && Enregistrer")
        btn_apply.setObjectName("primaryBtn")
        btn_apply.clicked.connect(self._save_and_apply)

        btn_close = QPushButton("Masquer le menu")
        btn_close.clicked.connect(self.accept)

        bottom_row.addWidget(btn_apply)
        bottom_row.addWidget(btn_close)
        main_layout.addLayout(bottom_row)

    def _load_from_config(self):
        self.url_edit.setText(self.config.get("ollama_url", "http://localhost:11434"))
        saved_model = self.config.get("ollama_model", "gemma3:1b")
        self._refresh_ollama_status(prefer_model=saved_model)

        saved_screen = str(self.config.get("screen_mode", "all"))
        idx_scr = self.screen_combo.findData(saved_screen)
        if idx_scr >= 0:
            self.screen_combo.setCurrentIndex(idx_scr)

        saved_dn = str(self.config.get("day_night_mode", "auto"))
        idx_dn = self.day_night_combo.findData(saved_dn)
        if idx_dn >= 0:
            self.day_night_combo.setCurrentIndex(idx_dn)

        self.scale_slider.setValue(int(self.config.get("cat_scale", 5)))
        self.speed_slider.setValue(int(float(self.config.get("cat_speed", 1.8)) * 10))
        self.thought_slider.setValue(int(self.config.get("thought_interval", 20)))
        self.chat_slider.setValue(int(self.config.get("chat_interval", 40)))
        self.chk_interactions.setChecked(
            bool(self.config.get("enable_chat_interactions", True))
        )
        self.chk_show_names.setChecked(
            bool(self.config.get("show_cat_names", True))
        )
        self.chk_laser.setChecked(
            bool(self.config.get("enable_laser", False))
        )

        self._rebuild_cat_list_widget()
        if self.cats_list:
            self.cat_list_widget.setCurrentRow(0)

    def _refresh_ollama_status(self, prefer_model: str = None):
        current_text = prefer_model or self.model_combo.currentText().strip()
        url = self.url_edit.text().strip() or "http://localhost:11434"
        ok, models = fetch_ollama_models(url)

        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        default_choices = ["gemma3:1b", "gemma3:270m"]
        merged = list(dict.fromkeys(default_choices + models))
        self.model_combo.addItems(merged)
        if current_text:
            self.model_combo.setCurrentText(current_text)
        self.model_combo.blockSignals(False)

        if ok:
            self.status_label.setText(
                f"✅ Connecté ({len(models)} modèle(s) détecté(s))"
            )
            self.status_label.setStyleSheet("color: #5cd65c; font-weight: bold;")
        else:
            self.status_label.setText(
                "⚠️ Ollama non détecté (mode hors-ligne actif)"
            )
            self.status_label.setStyleSheet("color: #ff9966; font-weight: bold;")

    def _rebuild_cat_list_widget(self):
        self.cat_list_widget.blockSignals(True)
        self.cat_list_widget.clear()
        for cat in self.cats_list:
            pix = self.sprite_bank.get_frame(cat["coat"], "sit", 0, scale=2)
            item = QListWidgetItem(QIcon(pix), f"{cat['name']} ({cat['coat']})")
            self.cat_list_widget.addItem(item)
        self.cat_list_widget.blockSignals(False)
        self.btn_remove_cat.setEnabled(len(self.cats_list) > 1)

    def _on_cat_selected(self, row: int):
        self.current_cat_idx = row
        if 0 <= row < len(self.cats_list):
            cat = self.cats_list[row]
            self.cat_name_edit.blockSignals(True)
            self.cat_coat_combo.blockSignals(True)
            self.cat_pers_edit.blockSignals(True)

            self.cat_name_edit.setText(cat["name"])
            self.cat_coat_combo.setCurrentText(cat["coat"])
            self.cat_pers_edit.setText(cat["personality"])
            self.preset_combo.setCurrentIndex(0)

            self.cat_name_edit.blockSignals(False)
            self.cat_coat_combo.blockSignals(False)
            self.cat_pers_edit.blockSignals(False)
            self._animate_preview()
            self._refresh_rules_for_current_cat()

    def _refresh_rules_for_current_cat(self):
        self.rules_table.setRowCount(0)
        self.btn_del_rule.setEnabled(False)
        self.rule_trig_input.clear()
        self.rule_resp_input.clear()

        if self.current_cat_idx < 0 or self.current_cat_idx >= len(self.cats_list):
            self.cat_memory_info_lbl.setText("🧠 Mémoire : aucun chat sélectionné")
            return

        cat_id = self.cats_list[self.current_cat_idx]["id"]
        if not self.memory:
            self.cat_memory_info_lbl.setText("🧠 Gestionnaire de mémoire non connecté")
            return

        # Facts count
        facts = self.memory.get_facts(cat_id)
        self.cat_memory_info_lbl.setText(f"🧠 Mémoire : {len(facts)} fait(s) et souvenir(s) mémorisé(s)")

        # Populate rules
        rules = self.memory.get_rules(cat_id)
        self.rules_table.setRowCount(len(rules))
        for row, (trig, resp) in enumerate(rules.items()):
            item_trig = QTableWidgetItem(f"« {trig} »")
            item_trig.setFlags(item_trig.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_resp = QTableWidgetItem(resp)
            item_resp.setFlags(item_resp.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.rules_table.setItem(row, 0, item_trig)
            self.rules_table.setItem(row, 1, item_resp)

    def _on_rule_row_selected(self):
        selected_rows = self.rules_table.selectionModel().selectedRows()
        if selected_rows:
            self.btn_del_rule.setEnabled(True)
            r = selected_rows[0].row()
            trig_item = self.rules_table.item(r, 0)
            resp_item = self.rules_table.item(r, 1)
            if trig_item and resp_item:
                raw_trig = trig_item.text().strip("«» ")
                self.rule_trig_input.setText(raw_trig)
                self.rule_resp_input.setText(resp_item.text())
        else:
            self.btn_del_rule.setEnabled(False)

    def _add_or_update_rule(self):
        if self.current_cat_idx < 0 or self.current_cat_idx >= len(self.cats_list):
            return
        cat_id = self.cats_list[self.current_cat_idx]["id"]
        trig = self.rule_trig_input.text().strip()
        resp = self.rule_resp_input.text().strip()
        if not trig or not resp:
            QMessageBox.warning(self, "Champs requis", "Veuillez renseigner ce que vous dites et ce que le chat répond !")
            return
        if self.memory:
            self.memory.add_rule(cat_id, trig, resp)
            self._refresh_rules_for_current_cat()
            self.rule_trig_input.clear()
            self.rule_resp_input.clear()

    def _delete_selected_rule(self):
        if self.current_cat_idx < 0 or self.current_cat_idx >= len(self.cats_list):
            return
        cat_id = self.cats_list[self.current_cat_idx]["id"]
        selected_rows = self.rules_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        r = selected_rows[0].row()
        trig_item = self.rules_table.item(r, 0)
        if trig_item and self.memory:
            raw_trig = trig_item.text().strip("«» ")
            self.memory.remove_rule(cat_id, raw_trig)
            self._refresh_rules_for_current_cat()

    def _apply_rule_pack(self, pack_type: str):
        if self.current_cat_idx < 0 or self.current_cat_idx >= len(self.cats_list):
            return
        cat_id = self.cats_list[self.current_cat_idx]["id"]
        if not self.memory:
            return

        if pack_type == "food":
            self.memory.add_rule(cat_id, "croquette", "Miam miam ! J'adore mes petites croquettes ! 🐾")
            self.memory.add_rule(cat_id, "thon", "DU THON ?! OÙ ÇA ?! Donne-le tout de suite ! 🐟")
            self.memory.add_rule(cat_id, "lait", "Une petite soucoupe bien fraîche, quel bonheur ~")
        elif pack_type == "love":
            self.memory.add_rule(cat_id, "bon chat", "*Ferme les yeux et ronronne très fort contre ta main* ❤️")
            self.memory.add_rule(cat_id, "je t'aime", "Moi aussi je t'aime, mon humain préféré ! 🐾")
            self.memory.add_rule(cat_id, "caresse", "*Fait des petits pas avec ses pattes avant en ronronnant*")
        elif pack_type == "code":
            self.memory.add_rule(cat_id, "1234", "56789")
            self.memory.add_rule(cat_id, "123", "YUIOHN")

        self._refresh_rules_for_current_cat()

    def _clean_current_cat_memory(self):
        if self.current_cat_idx < 0 or self.current_cat_idx >= len(self.cats_list):
            return
        cat_id = self.cats_list[self.current_cat_idx]["id"]
        if self.memory:
            self.memory.clean_corrupted_facts(cat_id)
            self._refresh_rules_for_current_cat()
            QMessageBox.information(self, "Mémoire nettoyée", "Les souvenirs parasites de ce chat ont été nettoyés avec succès !")

    def _reset_current_cat_memory(self):
        if self.current_cat_idx < 0 or self.current_cat_idx >= len(self.cats_list):
            return
        cat = self.cats_list[self.current_cat_idx]
        reply = QMessageBox.question(
            self,
            "Confirmer",
            f"Voulez-vous réinitialiser complètement la mémoire et l'historique de {cat['name']} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes and self.memory:
            self.memory.data[cat["id"]] = {"facts": [], "rules": {}, "history": []}
            self.memory.save()
            self._refresh_rules_for_current_cat()

    def _on_preset_chosen(self, index: int):
        if index > 0:
            preset_text = self.preset_combo.currentText()
            self.cat_pers_edit.setText(preset_text)
            self._on_cat_field_edited()

    def _on_cat_field_edited(self):
        idx = self.current_cat_idx
        if 0 <= idx < len(self.cats_list):
            name = self.cat_name_edit.text().strip() or "Minou"
            coat = self.cat_coat_combo.currentText()
            pers = self.cat_pers_edit.text().strip()
            self.cats_list[idx]["name"] = name
            self.cats_list[idx]["coat"] = coat
            self.cats_list[idx]["personality"] = pers

            item = self.cat_list_widget.item(idx)
            if item:
                pix = self.sprite_bank.get_frame(coat, "sit", 0, scale=2)
                item.setIcon(QIcon(pix))
                item.setText(f"{name} ({coat})")
            self._animate_preview()

    def _animate_preview(self):
        self.preview_frame = (self.preview_frame + 1) % 4
        if 0 <= self.current_cat_idx < len(self.cats_list):
            coat = self.cats_list[self.current_cat_idx]["coat"]
        else:
            coat = "Roux Tigré"
        pix = self.sprite_bank.get_frame(
            coat, "walk", self.preview_frame, scale=4
        )
        self.preview_lbl.setPixmap(pix)

    def _add_cat(self):
        new_Index = len(self.cats_list) + 1
        default_names = ["Plume", "Biscuit", "Luna", "Gribouille", "Sora", "Chaussette", "Nyx"]
        chosen_name = default_names[(new_Index - 1) % len(default_names)]
        chosen_coat = COAT_STYLES[(new_Index - 1) % len(COAT_STYLES)]
        chosen_pers = PERSONALITY_PRESETS[(new_Index - 1) % len(PERSONALITY_PRESETS)]

        new_cat = {
            "id": f"cat_{uuid.uuid4().hex[:6]}",
            "name": chosen_name,
            "coat": chosen_coat,
            "personality": chosen_pers,
        }
        self.cats_list.append(new_cat)
        self._rebuild_cat_list_widget()
        self.cat_list_widget.setCurrentRow(len(self.cats_list) - 1)

    def _remove_cat(self):
        if len(self.cats_list) <= 1:
            QMessageBox.information(
                self,
                "Information",
                "Vous devez garder au moins un chat sur la barre des tâches !",
            )
            return
        idx = self.current_cat_idx
        if 0 <= idx < len(self.cats_list):
            self.cats_list.pop(idx)
            self._rebuild_cat_list_widget()
            self.cat_list_widget.setCurrentRow(max(0, idx - 1))

    def _save_and_apply(self):
        self.config.data["ollama_url"] = (
            self.url_edit.text().strip() or "http://localhost:11434"
        )
        self.config.data["ollama_model"] = (
            self.model_combo.currentText().strip() or "gemma3:1b"
        )
        self.config.data["screen_mode"] = self.screen_combo.currentData() or "all"
        self.config.data["cat_scale"] = int(self.scale_slider.value())
        self.config.data["cat_speed"] = round(self.speed_slider.value() / 10.0, 1)
        self.config.data["thought_interval"] = int(self.thought_slider.value())
        self.config.data["chat_interval"] = int(self.chat_slider.value())
        self.config.data["enable_chat_interactions"] = bool(
            self.chk_interactions.isChecked()
        )
        self.config.data["show_cat_names"] = bool(
            self.chk_show_names.isChecked()
        )
        self.config.data["day_night_mode"] = self.day_night_combo.currentData() or "auto"
        self.config.data["enable_laser"] = bool(self.chk_laser.isChecked())
        self.config.data["cats"] = [dict(c) for c in self.cats_list]
        self.config.save()
        self.settings_applied.emit()

    def _open_selected_cat_chat(self):
        self._save_and_apply()
        if 0 <= self.current_cat_idx < len(self.cats_list):
            cid = self.cats_list[self.current_cat_idx]["id"]
            self.request_open_chat_for_cat.emit(cid)

import re
import random
import requests
from typing import Dict, List, Tuple
from PyQt6.QtCore import QThread, pyqtSignal

VALID_ACTIONS = [
    "MARCHER", "ASSIS", "DORMIR", "MIAULER", "TOILETTE", "JOUER",
    "PAIN", "ETIREMENT", "RONRONNER", "DEBOUT", "CHASSER"
]

ACTION_TO_STATE = {
    "MARCHER": "walk",
    "ASSIS": "sit",
    "DORMIR": "sleep",
    "MIAULER": "meow",
    "TOILETTE": "groom",
    "JOUER": "jump",
    "PAIN": "loaf",
    "LOAF": "loaf",
    "ETIREMENT": "stretch",
    "ETIRER": "stretch",
    "RONRONNER": "purr",
    "PURR": "purr",
    "DEBOUT": "stand",
    "CHASSER": "stalk",
    "AFFUT": "stalk",
}

FALLBACK_THOUGHTS = [
    ("MIAULER", "Miaou ! C'est l'heure des croquettes ? 🐾"),
    ("DORMIR", "Zzz... une petite sieste sur la barre des tâches..."),
    ("JOUER", "Ce curseur de souris bouge beaucoup trop vite !"),
    ("TOILETTE", "Il faut toujours garder ses moustaches impeccables."),
    ("ASSIS", "Je t'observe travailler, humain... fascinant."),
    ("MARCHER", "En patrouille le long de l'écran Windows !"),
    ("PAIN", "Mode pain de mie activé... pattes bien au chaud."),
    ("ETIREMENT", "Un grand étirement pour être au top de ma forme !"),
    ("RONRONNER", "Ronron... je suis tellement bien ici avec toi."),
    ("CHASSER", "Cible verrouillée... attention les pixels !"),
    ("DEBOUT", "Mais qu'est-ce qui se passe tout là-haut sur l'écran ?"),
]


def fetch_ollama_models(base_url: str = "http://localhost:11434") -> Tuple[bool, List[str]]:
    """Checks connection to Ollama and returns (is_connected, list_of_model_names)."""
    try:
        url = f"{base_url.rstrip('/')}/api/tags"
        resp = requests.get(url, timeout=2.5)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
            return True, models
    except Exception:
        pass
    return False, []


def _is_garbage_or_placeholder(text: str) -> bool:
    t_low = text.lower().strip()
    bad_tokens = [
        "sa réplique", "ta réplique", "votre réplique", "sa reponse", "sa réponse",
        "ta pensée", "ta pensee", "sa pensée", "sa pensee", "[sa", "[ta",
        "action", "exemple", "voici un mini-dialogue", "voici un dialogue",
        "mini-dialogue", "dialogue amusant", "en français :"
    ]
    for b in bad_tokens:
        if b in t_low:
            return True
    return len(t_low) < 2


def parse_action_and_text(raw: str, max_len: int = 160) -> Tuple[str, str]:
    raw = raw.strip().replace("*", "")
    chosen_state = "sit"
    for act_key, anim_val in ACTION_TO_STATE.items():
        if act_key in raw.upper():
            chosen_state = anim_val
            raw = re.sub(rf"\[?\s*{act_key}\s*\]?\s*:?\s*-?\s*", "", raw, flags=re.IGNORECASE)
            break

    lines = [line.strip().strip('"«»') for line in raw.splitlines() if line.strip()]
    text = " ".join(lines) if lines else "Miaou ! 🐾"
    text = re.sub(r"^\[.*?\]\s*", "", text).strip()
    
    if _is_garbage_or_placeholder(text):
        fallback_texts = [
            "Miaou ! J'observe l'écran avec attention.",
            "Une petite sieste sur la barre des tâches me ferait du bien.",
            "Où est passé le curseur de la souris ?",
            "Ronronne doucement en regardant l'humain.",
            "Je me demande s'il y a du thon dans les parages...",
        ]
        text = random.choice(fallback_texts)
        
    if len(text) > max_len:
        text = text[: max_len - 3].rsplit(" ", 1)[0] + "..."
    return chosen_state, text


class SoloThoughtWorker(QThread):
    """Generates an autonomous thought (internal or spoken out loud) + action decision using Ollama."""
    finished_thought = pyqtSignal(str, str, str, bool)  # (cat_id, state_anim, text, is_spoken)

    def __init__(
        self,
        base_url: str,
        model: str,
        cat_id: str,
        cat_name: str,
        personality: str,
        current_state: str,
        memory_block: str = "",
        context_hint: str = "",
        is_spoken: bool = False,
        is_night: bool = False,
    ):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.cat_id = cat_id
        self.cat_name = cat_name
        self.personality = personality
        self.current_state = current_state
        self.memory_block = memory_block
        self.context_hint = context_hint
        self.is_spoken = is_spoken
        self.is_night = is_night

    def run(self):
        mem_section = f"\n{self.memory_block}" if self.memory_block else ""
        extra = f"\nÉvénement : {self.context_hint}" if self.context_hint else ""

        if self.is_night:
            night_note = " C'est la nuit, l'ambiance est feutrée et propice au sommeil, aux rêves et aux ronronnements."
            if self.is_spoken:
                mode_desc = f"Tu chuchotes doucement ou bailles à l'humain.{night_note}"
                action_choices = "RONRONNER, MIAULER, PAIN, DORMIR, ETIREMENT"
            else:
                mode_desc = f"Tu es dans tes songes et tes rêves nocturnes de chat.{night_note}"
                action_choices = "DORMIR, PAIN, ASSIS, RONRONNER, ETIREMENT"
        elif self.is_spoken:
            mode_desc = "Tu décides de t'exprimer tout haut et de dire ce que tu penses à l'humain devant l'écran."
            action_choices = "MIAULER, JOUER, RONRONNER, DEBOUT, ETIREMENT, MARCHER"
        else:
            mode_desc = "Tu es dans tes pensées intérieures secrètes de chat, perdu dans tes réflexions."
            action_choices = "ASSIS, PAIN, DORMIR, ETIREMENT, RONRONNER, TOILETTE, CHASSER"

        prompt = (
            f"Tu incarnes {self.cat_name}, un petit chat en pixel art qui vit sur la barre des tâches Windows.\n"
            f"Ta personnalité : {self.personality}.{mem_section}{extra}\n"
            f"{mode_desc}\n"
            f"Choisis ta prochaine action parmi : {action_choices}.\n"
            f"Réponds UNIQUEMENT en français sur une seule ligne sous ce format exact :\n"
            f"[ACTION] Une phrase féline courte et vivante (maximum 12 mots).\n"
            f"Exemple : [PAIN] Je me mets en boule bien au chaud pendant que mon humain travaille."
        )

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "3m",
                    "options": {
                        "temperature": 0.88,
                        "num_predict": 60,
                        "num_ctx": 256,
                        "stop": ["\n\n"],
                    },
                },
                timeout=12,
            )
            if resp.status_code == 200:
                raw = resp.json().get("response", "").strip()
                state, thought = parse_action_and_text(raw, max_len=115)
                self.finished_thought.emit(self.cat_id, state, thought, self.is_spoken)
                return
        except Exception:
            pass

        if "to-do" in self.context_hint.lower() or "tâche" in self.context_hint.lower():
            todo_fallbacks = [
                ("MIAULER", "Dis, humain, comment avance ta to-do list ? 📋🐾"),
                ("ASSIS", "Je surveille ta to-do list... n'oublie pas de cocher ! ✨"),
                ("DEBOUT", "Miaou ! Tu as avancé sur tes tâches aujourd'hui ? 📋"),
                ("RONRONNER", "Courage pour tes tâches, je ronronne pour t'encourager ! 💖"),
            ]
            act, thought = random.choice(todo_fallbacks)
            self.finished_thought.emit(self.cat_id, ACTION_TO_STATE[act], thought, self.is_spoken)
            return

        act, thought = random.choice(FALLBACK_THOUGHTS)
        self.finished_thought.emit(self.cat_id, ACTION_TO_STATE[act], thought, self.is_spoken)


class UserChatWorker(QThread):
    """Handles a direct interactive chat message from the user to a cat, using persistent history, rules & facts."""
    # Emits (cat_id, state_anim, reply_text, extracted_memory_or_empty)
    finished_reply = pyqtSignal(str, str, str, str)

    def __init__(
        self,
        base_url: str,
        model: str,
        cat_id: str,
        cat_name: str,
        coat: str,
        personality: str,
        facts: List[str],
        rules: Dict[str, str],
        history: List[Dict[str, str]],
        user_message: str,
        matched_rule_result: str = "",
        tasks_summary: str = "",
    ):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.cat_id = cat_id
        self.cat_name = cat_name
        self.coat = coat
        self.personality = personality
        self.facts = list(facts)
        self.rules = dict(rules)
        self.history = list(history)
        self.user_message = user_message
        self.matched_rule_result = matched_rule_result or ""
        self.tasks_summary = tasks_summary

    def run(self):
        # 1. If the user just taught an explicit trigger->response rule
        if self.matched_rule_result.startswith("__RULE_TAUGHT__:"):
            parts = self.matched_rule_result.split(":", 2)
            trig = parts[1] if len(parts) > 1 else ""
            resp = parts[2] if len(parts) > 2 else ""
            reply = f"Miaou ! C'est bien retenu : quand tu diras « {trig} », je dirai « {resp} » ! 🐾"
            self.finished_reply.emit(self.cat_id, "meow", reply, "")
            return

        # 2. If the user's message directly matches a learned rule trigger (e.g. "123" -> "YUIOHN")
        if self.matched_rule_result:
            self.finished_reply.emit(self.cat_id, "meow", self.matched_rule_result, "")
            return

        # 3. Build focused memory context
        mem_lines = []
        if self.rules:
            for k, v in self.rules.items():
                mem_lines.append(f"- RÈGLE : Si l'humain dit '{k}', réponds exactement '{v}'.")
        # Only retain true facts, omit internal cat-to-cat smalltalk
        clean_facts = [f for f in self.facts if not f.startswith("J'ai discuté avec") and not f.startswith("J'ai salué")]
        for f in clean_facts[-10:]:
            mem_lines.append(f"- {f}")

        if self.tasks_summary:
            mem_lines.append(f"- Ta To-Do List actuelle : {self.tasks_summary}")

        facts_block = (
            "Règles et mémoire :\n" + "\n".join(mem_lines)
            if mem_lines
            else ""
        )

        system_prompt = (
            f"Tu es {self.cat_name}, un chat au pelage {self.coat} sur la barre des tâches Windows.\n"
            f"Caractère : {self.personality}.\n"
            f"{facts_block}\n"
            f"Consignes : Réponds en français de manière expressive, créative et naturelle à la demande de l'humain."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.history[-6:-1]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": self.user_message})

        # 1. Try standard /api/chat
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": "3m",
                    "options": {
                        "temperature": 0.75,
                        "num_predict": 160,
                        "num_ctx": 512,
                    },
                },
                timeout=18,
            )
            if resp.status_code == 200:
                raw = resp.json().get("message", {}).get("content", "").strip()
                if raw and len(raw) > 2:
                    state, reply_text = parse_action_and_text(raw, max_len=260)
                    self.finished_reply.emit(self.cat_id, state, reply_text, "")
                    return
        except Exception:
            pass

        # 2. Robust fallback via /api/generate for models that struggle with system messages
        try:
            gen_prompt = (
                f"Tu es {self.cat_name}, un chat mignon en pixel art ({self.personality}).\n"
                f"{facts_block}\n"
                f"Demande de l'humain : {self.user_message}\n"
                f"Réponds en français comme un vrai chat :"
            )
            resp_gen = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": gen_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.78,
                        "num_predict": 160,
                    },
                },
                timeout=18,
            )
            if resp_gen.status_code == 200:
                raw_gen = resp_gen.json().get("response", "").strip()
                if raw_gen and len(raw_gen) > 2:
                    state, reply_text = parse_action_and_text(raw_gen, max_len=260)
                    self.finished_reply.emit(self.cat_id, state, reply_text, "")
                    return
        except Exception:
            pass

        self.finished_reply.emit(
            self.cat_id,
            "meow",
            f"Miaou ! Je t'entends bien, mais mon cerveau Ollama ({self.model}) n'a pas pu formuler de réponse ! 🐾",
            "",
        )


class MultiCatDialogueWorker(QThread):
    """Generates a short 2-line conversation between two cats, taking their memories into account."""
    # Emits (list_of_turns, summary_fact_for_memory)
    finished_dialogue = pyqtSignal(list, str)

    def __init__(
        self,
        base_url: str,
        model: str,
        cat_a: Dict[str, str],
        cat_b: Dict[str, str],
        mem_a: str = "",
        mem_b: str = "",
    ):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.cat_a = cat_a
        self.cat_b = cat_b
        self.mem_a = mem_a
        self.mem_b = mem_b

    def run(self):
        name_a = self.cat_a["name"]
        name_b = self.cat_b["name"]
        pers_a = self.cat_a["personality"]
        pers_b = self.cat_b["personality"]

        mem_info = ""
        if self.mem_a:
            mem_info += f"\nMémoire de {name_a}: {self.mem_a}"
        if self.mem_b:
            mem_info += f"\nMémoire de {name_b}: {self.mem_b}"

        prompt = (
            f"Deux petits chats en pixel art se croisent sur la barre des tâches Windows.\n"
            f"Chat 1 : {name_a} ({pers_a}).\n"
            f"Chat 2 : {name_b} ({pers_b}).{mem_info}\n"
            f"Invente un mini-dialogue félin mignon et drôle en français de 2 répliques courtes (1 phrase chacun, maximum 10 mots) :\n"
            f"{name_a}: Coucou {name_b}, tu as vu la souris ?\n"
            f"{name_b}: Oui, elle bouge vite aujourd'hui !"
        )

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "3m",
                    "options": {
                        "temperature": 0.85,
                        "num_predict": 90,
                        "num_ctx": 384,
                    },
                },
                timeout=15,
            )
            if resp.status_code == 200:
                raw = resp.json().get("response", "").strip()
                parsed = self._parse_dialogue(raw, name_a, name_b)
                if parsed and len(parsed) >= 2:
                    summary = f"J'ai discuté avec {name_b} ({parsed[0][2]})"
                    self.finished_dialogue.emit(parsed, summary)
                    return
        except Exception:
            pass

        fallback = [
            (self.cat_a["id"], "meow", f"Salut {name_b}, tu as vu où est passé le curseur ?"),
            (self.cat_b["id"], "sit", f"Non {name_a}, je préfère faire la sieste ici ! 🐾"),
        ]
        self.finished_dialogue.emit(fallback, f"J'ai salué {name_b} sur la barre des tâches")

    def _parse_dialogue(self, raw: str, name_a: str, name_b: str) -> List[Tuple[str, str, str]]:
        lines = [l.strip().replace("*", "") for l in raw.splitlines() if l.strip()]
        result: List[Tuple[str, str, str]] = []

        for line in lines:
            if ":" in line:
                speaker, text = line.split(":", 1)
                speaker_clean = speaker.strip().lower()
                text_clean = text.strip().strip('"«»')
                if not text_clean or _is_garbage_or_placeholder(text_clean):
                    continue
                if len(text_clean) > 100:
                    text_clean = text_clean[:97].rsplit(" ", 1)[0] + "..."
                if name_a.lower() in speaker_clean or "chat 1" in speaker_clean:
                    result.append((self.cat_a["id"], "meow", text_clean))
                elif name_b.lower() in speaker_clean or "chat 2" in speaker_clean:
                    result.append((self.cat_b["id"], "meow", text_clean))

        if len(result) < 2 and len(lines) >= 2:
            l1 = re.sub(rf"^{re.escape(name_a)}\s*:?\s*", "", lines[0], flags=re.IGNORECASE).strip(' "«»')
            l2 = re.sub(rf"^{re.escape(name_b)}\s*:?\s*", "", lines[1], flags=re.IGNORECASE).strip(' "«»')
            if l1 and not _is_garbage_or_placeholder(l1) and l2 and not _is_garbage_or_placeholder(l2):
                result = [
                    (self.cat_a["id"], "meow", l1[:100]),
                    (self.cat_b["id"], "meow", l2[:100]),
                ]

        return result[:3]

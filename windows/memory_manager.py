import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memories.json")


class MemoryManager:
    """Manages persistent conversation history, learned rules, and long-term facts for each cat."""

    def __init__(self):
        # Structure per cat_id:
        # {
        #   "facts": ["Règle apprise : Quand l'humain dit '123', je dois répondre 'YUIOHN'", ...],
        #   "rules": {"123": "YUIOHN"},
        #   "history": [{"role": "user"|"assistant", "content": "...", "time": "19:42"}, ...]
        # }
        self.data: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.clean_corrupted_facts()
                return
            except Exception as e:
                print(f"[Cat AI] Erreur chargement memoire: {e}")
        self.data = {}

    def clean_corrupted_facts(self, cat_id: Optional[str] = None):
        """Cleans out placeholder texts like '[sa réplique]' from memories."""
        bad_substrings = [
            "sa réplique", "sa replique", "ta réplique", "ta replique",
            "sa réponse", "sa reponse", "[sa", "[ta", "mini-dialogue",
            "en français :", "dialogue drôle", "dialogue amusant"
        ]
        target_cats = [cat_id] if cat_id and cat_id in self.data else list(self.data.keys())
        modified = False
        for cid in target_cats:
            facts = self.data.get(cid, {}).get("facts", [])
            new_facts = []
            for fact in facts:
                f_low = fact.lower()
                if not any(bad in f_low for bad in bad_substrings):
                    new_facts.append(fact)
                else:
                    modified = True
            if cid in self.data:
                self.data[cid]["facts"] = new_facts
        if modified:
            self.save()

    def save(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Cat AI] Erreur sauvegarde memoire: {e}")

    def _ensure_cat(self, cat_id: str):
        if cat_id not in self.data:
            self.data[cat_id] = {
                "facts": [],
                "rules": {},
                "history": [],
            }
        else:
            if "facts" not in self.data[cat_id]:
                self.data[cat_id]["facts"] = []
            if "rules" not in self.data[cat_id]:
                self.data[cat_id]["rules"] = {}
            if "history" not in self.data[cat_id]:
                self.data[cat_id]["history"] = []

    def get_history(self, cat_id: str) -> List[Dict[str, str]]:
        self._ensure_cat(cat_id)
        return self.data[cat_id]["history"]

    def get_facts(self, cat_id: str) -> List[str]:
        self._ensure_cat(cat_id)
        return self.data[cat_id]["facts"]

    def get_rules(self, cat_id: str) -> Dict[str, str]:
        self._ensure_cat(cat_id)
        return self.data[cat_id]["rules"]

    def add_fact(self, cat_id: str, fact: str):
        self._ensure_cat(cat_id)
        fact = fact.strip()
        if not fact:
            return
        facts = self.data[cat_id]["facts"]
        if fact not in facts:
            facts.append(fact)
            if len(facts) > 40:
                self.data[cat_id]["facts"] = facts[-40:]
            self.save()

    def add_rule(self, cat_id: str, trigger: str, response: str):
        self._ensure_cat(cat_id)
        trig_clean = self._clean_quotes(trigger).strip()
        resp_clean = self._clean_quotes(response).strip()
        if not trig_clean or not resp_clean:
            return
        self.data[cat_id]["rules"][trig_clean.lower()] = resp_clean
        self.add_fact(
            cat_id,
            f"Règle impérative : Quand l'humain dit « {trig_clean} », tu dois répondre exactement « {resp_clean} »",
        )
        self.save()

    def remove_rule(self, cat_id: str, trigger: str):
        self._ensure_cat(cat_id)
        trig_clean = self._clean_quotes(trigger).strip().lower()
        if trig_clean in self.data[cat_id]["rules"]:
            del self.data[cat_id]["rules"][trig_clean]
            self.data[cat_id]["facts"] = [
                f for f in self.data[cat_id]["facts"]
                if f"« {trig_clean} »" not in f.lower() and f"'{trig_clean}'" not in f.lower()
            ]
            self.save()

    def check_learned_rule(self, cat_id: str, user_text: str) -> Optional[str]:
        """Checks if user_text matches an existing learned rule trigger.
        Returns the forced reply if a rule is triggered, or None."""
        self._ensure_cat(cat_id)
        clean_input = self._clean_quotes(user_text).strip()
        rules = self.data[cat_id].get("rules", {})
        if not rules:
            return None

        lower_in = clean_input.lower()

        # 1. Exact match (case insensitive)
        if lower_in in rules:
            return rules[lower_in]

        # 2. Match without trailing punctuation
        stripped_punct = re.sub(r"[\.!\?]+$", "", lower_in).strip()
        if stripped_punct in rules:
            return rules[stripped_punct]

        # 3. Check stripped quotes on both
        for trig, resp in rules.items():
            if self._clean_quotes(trig).lower() == lower_in or self._clean_quotes(trig).lower() == stripped_punct:
                return resp

        # 4. Check if user is teaching via chat sentence
        taught = self._try_parse_rule_teaching(user_text)
        if taught:
            trig, resp = taught
            self.add_rule(cat_id, trig, resp)
            return f"__RULE_TAUGHT__:{trig}:{resp}"

        return None

    def _clean_quotes(self, s: str) -> str:
        s = s.strip()
        # Strip matching or repeated single/double/French quotes
        s = re.sub(r"^['\"«»“”‘’\s]+|['\"«»“”‘’\s]+$", "", s)
        return s

    def _try_parse_rule_teaching(self, text: str) -> Optional[Tuple[str, str]]:
        """Parses patterns like:
        - Quand je dis ''123'' tu dis ''YUIOHN''
        - Si je dis X réponds Y
        - Quand j'écris X tu réponds Y
        """
        t = text.strip()
        patterns = [
            r"(?:quand|si|lorsque)\s+(?:je\s+|on\s+te\s+)?(?:dis|dit|écris|ecris|tape)\s+(.+?)\s*(?:,\s*)?(?:tu\s+dois\s+dire|tu\s+dois\s+répondre|tu\s+dis|tu\s+réponds|tu\s+reponds|dis|réponds|reponds)\s+(.+)$",
            r"à\s+chaque\s+fois\s+que\s+je\s+(?:dis|écris)\s+(.+?)\s*(?:,\s*)?(?:tu\s+dis|tu\s+réponds|dis|réponds)\s+(.+)$",
        ]
        for pat in patterns:
            m = re.search(pat, t, flags=re.IGNORECASE)
            if m:
                trig = self._clean_quotes(m.group(1))
                resp = self._clean_quotes(m.group(2))
                # Remove trailing period if not part of quotes
                resp = re.sub(r"\.$", "", resp).strip()
                if trig and resp:
                    return trig, resp
        return None

    def add_message(self, cat_id: str, role: str, content: str):
        self._ensure_cat(cat_id)
        now_str = datetime.now().strftime("%H:%M")
        self.data[cat_id]["history"].append(
            {
                "role": role,
                "content": content.strip(),
                "time": now_str,
            }
        )
        if len(self.data[cat_id]["history"]) > 40:
            self.data[cat_id]["history"] = self.data[cat_id]["history"][-40:]

        if role == "user":
            self._auto_extract_facts(cat_id, content)

        self.save()

    def _auto_extract_facts(self, cat_id: str, user_text: str):
        """Extracts rules, personal facts, and general information taught by the user."""
        text = user_text.strip()
        if not text:
            return

        # 1. Check rule teaching
        taught = self._try_parse_rule_teaching(text)
        if taught:
            trig, resp = taught
            self.add_rule(cat_id, trig, resp)
            return

        # 2. Specific French patterns
        patterns = [
            (r"je m'appelle\s+([^\.,!?\n]+)", "L'humain s'appelle {0}"),
            (r"mon nom est\s+([^\.,!?\n]+)", "L'humain s'appelle {0}"),
            (r"mon prénom est\s+([^\.,!?\n]+)", "L'humain s'appelle {0}"),
            (r"j'aime\s+([^\.,!?\n]+)", "L'humain aime {0}"),
            (r"j'adore\s+([^\.,!?\n]+)", "L'humain adore {0}"),
            (r"je déteste\s+([^\.,!?\n]+)", "L'humain déteste {0}"),
            (r"je travaille sur\s+([^\.,!?\n]+)", "L'humain travaille sur {0}"),
            (r"mon(?:eb)?\s+([a-zA-Zéèêàùç\s]{2,25})\s+(?:est|c'est)\s+([^\.,!?\n]+)", "Le/la {0} de l'humain est {1}"),
            (r"(?:le|la)\s+([a-zA-Zéèêàùç\s]{2,25})\s+(?:est|c'est)\s+([^\.,!?\n]+)", "Info retenue : {0} est {1}"),
            (r"retiens\s+(?:bien\s+)?(?:que\s+)?(.+)", "Info à retenir : {0}"),
            (r"souviens[\s-]toi\s+(?:bien\s+)?(?:que\s+)?(.+)", "Info à retenir : {0}"),
            (r"n'oublie\s+pas\s+(?:que\s+)?(.+)", "Info à retenir : {0}"),
            (r"sache\s+que\s+(.+)", "Info à retenir : {0}"),
        ]

        matched_specific = False
        for pat, template in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                groups = [g.strip() for g in m.groups()]
                fact_str = template.format(*groups)
                if len(fact_str) <= 140:
                    self.add_fact(cat_id, fact_str)
                    matched_specific = True

        # 3. Also store any declarative statement (> 3 words, not a question, not a greeting)
        if not matched_specific and "?" not in text:
            words = text.split()
            greetings = {"salut", "bonjour", "coucou", "hello", "hey", "miaou", "ok", "oui", "non", "merci"}
            first_word = re.sub(r"[^\w]", "", words[0].lower()) if words else ""
            if len(words) >= 4 and len(text) <= 130 and first_word not in greetings:
                # Check it's not a trigger
                if text.lower().strip() not in self.data[cat_id]["rules"]:
                    self.add_fact(cat_id, f"L'humain a dit : « {text} »")

    def format_memory_block(self, cat_id: str, max_recent: int = 8) -> str:
        """Builds a clear memory summary string to inject into Ollama prompts."""
        self._ensure_cat(cat_id)
        facts = self.data[cat_id]["facts"]
        rules = self.data[cat_id]["rules"]
        history = self.data[cat_id]["history"]

        parts = []
        if rules:
            r_list = [f"Si l'humain dit '{k}' -> répondre '{v}'" for k, v in rules.items()]
            parts.append("RÈGLES APPRISES :\n- " + "\n- ".join(r_list))

        if facts:
            parts.append("INFORMATIONS RETENUES EN MÉMOIRE :\n- " + "\n- ".join(facts[-15:]))

        if history:
            recent = history[-max_recent:]
            lines = []
            for msg in recent:
                speaker = "Humain" if msg["role"] == "user" else "Moi"
                lines.append(f"{speaker}: {msg['content']}")
            parts.append("DERNIERS ÉCHANGES :\n" + "\n".join(lines))

        return "\n\n".join(parts)

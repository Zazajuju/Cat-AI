from typing import Dict, List, Tuple
from PyQt6.QtGui import QImage, QPixmap, QColor
from PyQt6.QtCore import Qt

# Palette keys used in pixel grids:
# '.' : Transparent
# 'O' : Outline (dark border)
# 'B' : Base coat color
# 'S' : Secondary / Stripe / Patch color
# 'T' : Tertiary / Belly / Chest / Paws color
# 'E' : Eye color
# 'P' : Pink (inner ears / nose / tongue)
# 'W' : White shine / Zzz / Sparkle / Heart

COAT_PALETTES: Dict[str, Dict[str, str]] = {
    "Roux Tigré": {
        "O": "#2b160c",
        "B": "#f28c28",
        "S": "#c85a17",
        "T": "#ffe5b4",
        "E": "#2e8b57",
        "P": "#ff8da1",
        "W": "#ffffff",
    },
    "Gingembre Caramel": {
        "O": "#381c0d",
        "B": "#ffaa44",
        "S": "#cc6611",
        "T": "#fff2cc",
        "E": "#e68a00",
        "P": "#ffaab5",
        "W": "#ffffff",
    },
    "Noir": {
        "O": "#0d0d12",
        "B": "#23232e",
        "S": "#181820",
        "T": "#2f2f3d",
        "E": "#ffd700",
        "P": "#d96b82",
        "W": "#ffffff",
    },
    "Blanc": {
        "O": "#4a525d",
        "B": "#f7f9fc",
        "S": "#dce3ec",
        "T": "#ffffff",
        "E": "#3b9eff",
        "P": "#ffa6b8",
        "W": "#ffffff",
    },
    "Gris Chartreux": {
        "O": "#222730",
        "B": "#738091",
        "S": "#556070",
        "T": "#9aa6b5",
        "E": "#e69b00",
        "P": "#e8899c",
        "W": "#ffffff",
    },
    "Bleu Russe": {
        "O": "#1c222b",
        "B": "#5d6d7e",
        "S": "#475564",
        "T": "#85929e",
        "E": "#2ecc71",
        "P": "#f1948a",
        "W": "#ffffff",
    },
    "Siamois": {
        "O": "#2b1d16",
        "B": "#f3e5d0",
        "S": "#4a3225",
        "T": "#fff6e8",
        "E": "#3388ff",
        "P": "#e08294",
        "W": "#ffffff",
    },
    "Chocolat Point": {
        "O": "#26150f",
        "B": "#faeedd",
        "S": "#3d2015",
        "T": "#fff9f2",
        "E": "#4d94ff",
        "P": "#f092a4",
        "W": "#ffffff",
    },
    "Calico": {
        "O": "#261a15",
        "B": "#fafafa",
        "S": "#e87825",
        "T": "#332c29",
        "E": "#4ca64c",
        "P": "#ff94a8",
        "W": "#ffffff",
    },
    "Écaille de tortue": {
        "O": "#140e0b",
        "B": "#241d1a",
        "S": "#d96a1a",
        "T": "#8c4f2b",
        "E": "#f39c12",
        "P": "#e74c3c",
        "W": "#ffffff",
    },
    "Tuxedo": {
        "O": "#101016",
        "B": "#22222b",
        "S": "#17171f",
        "T": "#f7f7fa",
        "E": "#5cd65c",
        "P": "#ff8fa3",
        "W": "#ffffff",
    },
    "Tigré Argenté": {
        "O": "#1e2229",
        "B": "#b0b8c4",
        "S": "#4a5361",
        "T": "#e2e6ed",
        "E": "#00bcd4",
        "P": "#f48fb1",
        "W": "#ffffff",
    },
    "Chat Magique Violet": {
        "O": "#120826",
        "B": "#5e35b1",
        "S": "#311b92",
        "T": "#b39ddb",
        "E": "#00e5ff",
        "P": "#ff4081",
        "W": "#ffff00",
    },
}

# All grids are 20 columns x 16 rows (facing RIGHT by default)
SPRITE_FRAMES: Dict[str, List[List[str]]] = {
    # 1. Marche animée (4 frames)
    "walk": [
        [
            "....................",
            "..OO................",
            ".OBO.......OO...OO..",
            ".OBO......OBOO.OBOO.",
            "..OBO.....OBPOOOOOO.",
            "..OBO....OSSSSSSSSO.",
            "...OBO...OBBBBBBBBO.",
            "...OBOOOOOBEWBBBEWBO",
            "....OBSSSOBBBBBPBBBO",
            "....OBBBBBBBTTTTBBBO",
            "....OBSSSSSSSSSSSSO.",
            "....OBBBBBBBBBBBBBO.",
            "....OBBO..OBBO.OBBO.",
            "....OTTO..OTTO.OTTO.",
            "....OOOO..OOOO.OOOO.",
            "....................",
        ],
        [
            "....................",
            "....................",
            ".OO........OO...OO..",
            "OBO.......OBOO.OBOO.",
            "OBO.......OBPOOOOOO.",
            ".OBO.....OSSSSSSSSO.",
            "..OBO....OBBBBBBBBO.",
            "...OBOOOOOBEWBBBEWBO",
            "....OBSSSOBBBBBPBBBO",
            "....OBBBBBBBTTTTBBBO",
            "....OBSSSSSSSSSSSSO.",
            "....OBBBBBBBBBBBBBO.",
            ".....OBBO..OBBOOBBO.",
            ".....OTTO..OTTOOTTO.",
            ".....OOOO..OOOOOOOO.",
            "....................",
        ],
        [
            "....................",
            "....................",
            "...........OO...OO..",
            "..OO......OBOO.OBOO.",
            ".OBO......OBPOOOOOO.",
            ".OBO.....OSSSSSSSSO.",
            "..OBO....OBBBBBBBBO.",
            "...OBOOOOOBEWBBBEWBO",
            "....OBSSSOBBBBBPBBBO",
            "....OBBBBBBBTTTTBBBO",
            "....OBSSSSSSSSSSSSO.",
            "....OBBBBBBBBBBBBBO.",
            "...OBBO...OBBO..OBBO",
            "...OTTO...OTTO..OTTO",
            "...OOOO...OOOO..OOOO",
            "....................",
        ],
        [
            "....................",
            "....................",
            ".OO........OO...OO..",
            "OBO.......OBOO.OBOO.",
            "OBO.......OBPOOOOOO.",
            ".OBO.....OSSSSSSSSO.",
            "..OBO....OBBBBBBBBO.",
            "...OBOOOOOBEWBBBEWBO",
            "....OBSSSOBBBBBPBBBO",
            "....OBBBBBBBTTTTBBBO",
            "....OBSSSSSSSSSSSSO.",
            "....OBBBBBBBBBBBBBO.",
            ".....OBBO.OBBO.OBBO.",
            ".....OTTO.OTTO.OTTO.",
            ".....OOOO.OOOO.OOOO.",
            "....................",
        ],
    ],

    # 2. Assis alerte / observation
    "sit": [
        [
            "....................",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBEWBBBEWBO..",
            ".......OBBBBBPBBBO..",
            "......OOBBTTTTTBBOO.",
            ".....OBSSSSSSSSSSBO.",
            "....OBBBBBBBBBBBBBO.",
            "...OOBBBBBBTTTTBBBO.",
            "..OBOBBBBBOTTTTOBBO.",
            "..OBOOOOOOOTTTTOBBO.",
            "...OOOO...OOOOOOOO..",
            "....................",
        ],
        [
            "....................",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBOOBBBOOBO..",
            ".......OBBBBBPBBBO..",
            "......OOBBTTTTTBBOO.",
            ".....OBSSSSSSSSSSBO.",
            "...OOBBBBBBBBBBBBBO.",
            "..OBOBBBBBBTTTTBBBO.",
            "..OB.OOOOOOTTTTOBBO.",
            "...OO.....OTTTTOBBO.",
            "..........OOOOOOOO..",
            "....................",
        ],
    ],

    # 3. Cat Loaf (pain de mie, pattes repliées)
    "loaf": [
        [
            "....................",
            "........OO...OO.....",
            ".......OBOO.OBOO....",
            ".......OBPOOOOOO....",
            "......OSSSSSSSSO....",
            "......OBBBBBBBBO....",
            "......OBOOBBBOOBO...",
            "......OBBBBBPBBBO...",
            "...OOOOOBBBBBBBBBOO.",
            "..OBSSSSSSSSSSSSSSBO",
            ".OBBBBBBBBBBBBBBBBBO",
            ".OBBTTTTTTTTTTTTTBBO",
            "..OOOOOOOOOOOOOOOOO.",
            "....................",
            "....................",
            "....................",
        ],
        [
            "....................",
            "........OO...OO.....",
            ".......OBOO.OBOO....",
            ".......OBPOOOOOO....",
            "......OSSSSSSSSO....",
            "......OBBBBBBBBO....",
            "......OBEWBBBEWBO...",
            "......OBBBBBPBBBO...",
            "...OOOOOBBBBBBBBBOO.",
            "..OBSSSSSSSSSSSSSSBO",
            ".OBBBBBBBBBBBBBBBBBO",
            ".OBBTTTTTTTTTTTTTBBO",
            "..OOOOOOOOOOOOOOOOO.",
            "....................",
            "....................",
            "....................",
        ],
    ],

    # 4. Étirement du chat (stretch)
    "stretch": [
        [
            "....................",
            "....OO..............",
            "...OBOO.............",
            "...OBPOO............",
            "....OBSSO...........",
            "....OBBBO...........",
            ".....OBBO....OO..OO.",
            ".....OBBO...OBOOOBOO",
            "....OBSSSO..OBBBBPBO",
            "...OBBBBBBOOBEWBEWBO",
            "..OBBO...OBBOBBBPBBO",
            "..OTTO...OTTTTTTTTTO",
            "..OOOO....OOOOOOOOO.",
            "....................",
            "....................",
            "....................",
        ],
        [
            "....................",
            "...OO...............",
            "..OBOO..............",
            "..OBPOO.............",
            "...OBSSO............",
            "...OBBBO............",
            "....OBBO.....OO..OO.",
            "....OBBO....OBOOOBOO",
            "...OBSSSO...OBBBBPBO",
            "..OBBBBBBO.OBEWBEWBO",
            "..OBBO...OBBOBBBPBBO",
            "..OTTO...OTTTTTTTTTO",
            "..OOOO....OOOOOOOOO.",
            "....................",
            "....................",
            "....................",
        ],
    ],

    # 5. Ronronnement / Bonheur avec petit cœur / note de musique
    "purr": [
        [
            ".............WW.WW..",
            "............WWWWWWW.",
            ".............WWWWW..",
            "..............WWW...",
            ".........OO...OO.W..",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBOOBBBOOBO..",
            ".......OBBBBBPBBBO..",
            "......OOBBTTTTTBBOO.",
            ".....OBSSSSSSSSSSBO.",
            "...OOBBBBBBBBBBBBBO.",
            "..OBOOOOOOOTTTTOBBO.",
            "...OO.....OOOOOOOO..",
        ],
        [
            "............WW.WW...",
            "...........WWWWWWW..",
            "............WWWWW...",
            ".............WWW....",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBEWBBBEWBO..",
            ".......OBBBBBPBBBO..",
            "......OOBBTTTTTBBOO.",
            ".....OBSSSSSSSSSSBO.",
            "...OOBBBBBBBBBBBBBO.",
            "..OBOOOOOOOTTTTOBBO.",
            "...OO.....OOOOOOOO..",
        ],
    ],

    # 6. Chat curieux debout sur ses pattes arrière
    "stand": [
        [
            "....................",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBEWBBBEWBO..",
            ".......OBBBBBPBBBO..",
            "......OOBBTTTTTBBOO.",
            "......OBBTTTTTTTBBO.",
            "......OBSSSSSSSSSSO.",
            "......OBBBBBBBBBBBO.",
            ".......OBBTTTTTBBO..",
            "..OO...OBBO...OBBO..",
            ".OBO...OTTO...OTTO..",
            ".OO....OOOO...OOOO..",
        ],
        [
            "....................",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBOOBBBOOBO..",
            ".......OBBBBBPBBBO..",
            "......OOBBTTTTTBBOO.",
            "......OBBTTTTTTTBBO.",
            "......OBSSSSSSSSSSO.",
            "......OBBBBBBBBBBBO.",
            ".......OBBTTTTTBBO..",
            "..OO...OBBO...OBBO..",
            ".OBO...OTTO...OTTO..",
            ".OO....OOOO...OOOO..",
        ],
    ],

    # 7. Affût / Prêt à bondir (stalk)
    "stalk": [
        [
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            "...OO...............",
            "..OBOO.......OO...OO",
            "..OBPOOOOO..OBOO.OBO",
            "..OBSSSSSSOOOBPOOOOO",
            ".OBBBBBBBBBBBBEWWBEW",
            "OBSSSSSSSSSSSBBPBBBO",
            "OBBBBBBBBBBBBTTTTBBO",
            ".OOOOOOOOOOOOOOOOOO.",
            "....................",
        ],
        [
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            "....OO..............",
            "...OBOO......OO...OO",
            "...OBPOOOOO.OBOO.OBO",
            "...OBSSSSSSOOBPOOOOO",
            "..OBBBBBBBBBBBEWWBEW",
            ".OBSSSSSSSSSSBBPBBBO",
            ".OBBBBBBBBBBBTTTTBBO",
            "..OOOOOOOOOOOOOOOOO.",
            "....................",
        ],
    ],

    # 8. Sommeil (sleep)
    "sleep": [
        [
            "....................",
            "..............WW....",
            "...............W....",
            "..............WW....",
            "....................",
            "....................",
            "....................",
            "....................",
            "......OOOOOOO.......",
            "....OOBSSSSSBOO.....",
            "...OBBBBBBBBBBOOO...",
            "..OBBBOOBBBOOBPBBO..",
            "..OBBBBBBBBBBBBBBO..",
            "..OBSSSSSSSSSSSSBO..",
            "...OOOOOOOOOOOOOO...",
            "....................",
        ],
        [
            "................WW..",
            ".................W..",
            "................WW..",
            "............WW......",
            "....................",
            "....................",
            "....................",
            ".....OOOOOOOOO......",
            "....OBSSSSSSSBO.....",
            "...OBBBBBBBBBBBOO...",
            "..OBBBOOBBBOOBPBBO..",
            "..OBBBBBBBBBBBBBBO..",
            "..OBSSSSSSSSSSSSBO..",
            "...OOOOOOOOOOOOOO...",
            "....................",
            "....................",
        ],
    ],

    # 9. Miaou / Parler
    "meow": [
        [
            "....................",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBEWBBBEWBO..",
            ".......OBBBBOPOBBO..",
            "......OOBBTTPOPBBOO.",
            ".....OBSSSSSTTTSSBO.",
            "....OBBBBBBBBBBBBBO.",
            "...OOBBBBBBTTTTBBBO.",
            "..OBOBBBBBOTTTTOBBO.",
            "..OBOOOOOOOTTTTOBBO.",
            "...OOOO...OOOOOOOO..",
            "....................",
        ],
        [
            "....................",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBOOBBBOOBO..",
            ".......OBBBBBPBBBO..",
            "......OOBBTTTTTBBOO.",
            ".....OBSSSSSSSSSSBO.",
            "....OBBBBBBBBBBBBBO.",
            "...OOBBBBBBTTTTBBBO.",
            "..OBOBBBBBOTTTTOBBO.",
            "..OBOOOOOOOTTTTOBBO.",
            "...OOOO...OOOOOOOO..",
            "....................",
        ],
    ],

    # 10. Toilette (groom)
    "groom": [
        [
            "....................",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBOOBBBOOBO..",
            ".......OBBBBBPBBTOO.",
            "......OOBBTTTTTBTTO.",
            ".....OBSSSSSSSSSOOO.",
            "....OBBBBBBBBBBBBBO.",
            "...OOBBBBBBTTTTBBBO.",
            "..OBOBBBBBOTTTTOBBO.",
            "..OBOOOOOOOTTTTOBBO.",
            "...OOOO...OOOOOOOO..",
            "....................",
        ],
        [
            "....................",
            ".........OO...OO....",
            "........OBOO.OBOO...",
            "........OBPOOOOOO...",
            ".......OSSSSSSSSO...",
            ".......OBBBBBBBBO...",
            ".......OBEWBBBOOBO..",
            ".......OBBBBBPPOTTO.",
            "......OOBBTTTTTOTTO.",
            ".....OBSSSSSSSSSOOO.",
            "....OBBBBBBBBBBBBBO.",
            "...OOBBBBBBTTTTBBBO.",
            "..OBOBBBBBOTTTTOBBO.",
            "..OBOOOOOOOTTTTOBBO.",
            "...OOOO...OOOOOOOO..",
            "....................",
        ],
    ],

    # 11. Saut / Pounce (4 frames dynamiques : préparation, bond ascendant, vol plané, réception)
    "jump": [
        # Frame 0 : Flexion / Préparation au sol (ressort)
        [
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            "...........OO...OO..",
            "..OO......OBOO.OBOO.",
            ".OBO......OBPOOOOOO.",
            ".OBO.....OSSSSSSSSO.",
            "..OBOOOO.OBEWBBBEWBO",
            "..OBSSSOOBBBBBBPBBBO",
            "..OBBBBBBBBBBBTTTTBO",
            ".OBSSSSSSSSSSSSSSSO.",
            ".OTTO..OTTO..OTTO...",
            ".OOOO..OOOO..OOOO...",
        ],
        # Frame 1 : Élan ascendant (corps étiré en diagonale vers le haut)
        [
            "....................",
            "................OO..",
            "...............OBOO.",
            "...........OO..OBPOO",
            "..........OBOOOSSSSO",
            ".........OSSSOBEWBO.",
            "........OBBBBBPBBBO.",
            ".......OBBBBBTTTTBO.",
            "...OO.OBBBBBBBBBO...",
            "..OBOOBSSSOOBBO.....",
            "..OBOOBBBO..OTTO....",
            "...OBOSSSO..OOOO....",
            "....OBBO............",
            "....OTTO............",
            "....OOOO............",
            "....................",
        ],
        # Frame 2 : Vol plané / Extension maximale en plein vol
        [
            "....................",
            "..............OO.OO.",
            ".............OBOOBOO",
            ".............OBPOOOO",
            "............OSSSSO..",
            "..OO.......OBEWBO...",
            ".OBOO.....OBBPBBBO..",
            "OBOBBBOOOBBBTTTTBO..",
            ".OBSSSSBBBBBBBBBO...",
            "..OBBO...OBBO.OTTO..",
            "..OTTO...OTTO.OOOO..",
            "..OOOO...OOOO.......",
            "....................",
            "....................",
            "....................",
            "....................",
        ],
        # Frame 3 : Descente / Préparation de l'atterrissage
        [
            "....................",
            "....................",
            "....................",
            "...........OO...OO..",
            "..OO......OBOO.OBOO.",
            ".OBO......OBPOOOOOO.",
            ".OBO.....OSSSSSSSSO.",
            "..OBO...OBEWBBBEWBO.",
            "...OBOOOBBBBBBPBBBO.",
            "....OBSSSOBBBBTTTBO.",
            "....OBBBBBBBBBBBBBO.",
            ".....OBBO....OBBO...",
            ".....OBBO....OBBO...",
            ".....OTTO....OTTO...",
            ".....OOOO....OOOO...",
            "....................",
        ],
    ],
}


class SpriteBank:
    """Generates and caches scaled QPixmaps for all coat styles, animations, and frames."""

    def __init__(self):
        self._cache: Dict[Tuple[str, str, int, int, bool], QPixmap] = {}

    def clear_cache(self):
        self._cache.clear()

    def get_frame(
        self,
        coat: str,
        anim: str,
        frame_idx: int,
        scale: int = 5,
        facing_left: bool = False,
    ) -> QPixmap:
        if coat not in COAT_PALETTES:
            coat = "Roux Tigré"
        if anim not in SPRITE_FRAMES:
            anim = "sit"

        frames = SPRITE_FRAMES[anim]
        frame_idx = frame_idx % len(frames)
        key = (coat, anim, frame_idx, scale, facing_left)

        if key in self._cache:
            return self._cache[key]

        palette = COAT_PALETTES[coat]
        grid = frames[frame_idx]
        height = len(grid)
        width = len(grid[0])

        img = QImage(width, height, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)

        for y, row in enumerate(grid):
            for x, ch in enumerate(row):
                if ch != "." and ch in palette:
                    img.setPixelColor(x, y, QColor(palette[ch]))

        if facing_left:
            img = img.mirrored(True, False)

        pixmap = QPixmap.fromImage(img).scaled(
            width * scale,
            height * scale,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        self._cache[key] = pixmap
        return pixmap

    def frame_count(self, anim: str) -> int:
        return len(SPRITE_FRAMES.get(anim, SPRITE_FRAMES["sit"]))

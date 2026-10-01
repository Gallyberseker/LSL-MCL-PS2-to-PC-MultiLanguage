"""Formats binaires, signatures et contraintes de texte du moteur Larry MCL."""
import re
import struct

SFD_NON_VOCAUX = {
    "vug.sfd",
}

FORMATS_IMAGES = (
    "BMP",
    "DDS",
    "JPG",
    "JPEG",
    "PNG",
    "GIF",
    "WEBP",
    "ICO",
)

SIGNATURES_INCONNUES = {
    b"8BPS": "PSD",
    b"TIM2": "TIM2",
    b"II*\x00": "TIFF_LE",
    b"MM\x00*": "TIFF_BE",
}

EXT_IMAGES = {
    ".bmp",
    ".dds",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".ico",
}

SIG_JAM = struct.pack("<6I", 0xFF, 0x2D, 0x42, 0x53, 0x8B, 0xA2)

ENTRY = re.compile(
    rb'^([ \t]*)'
    rb'"([^"]+)"'
    rb'([ \t]+)'
    rb'"((?:\\.|[^"\\])*)"'
    rb'([ \t]*)\r?$', re.M)

GLYPH = {
    0xBD: 0xC0,
    0xBE: 0xC1,
    0xC6: 0xC2,
    0xBC: 0xBF,
    0xC7: 0xC3,
    0xFE: 0xB0,
    0xFD: 0xC4,
}

ACCENT = {
    0xC0: b"A",
    0xC1: b"A",
    0xC2: b"A",
    0xC3: b"A",
    0xC4: b"A",
    0xC5: b"A",
    0xE0: b"a",
    0xE1: b"a",
    0xE2: b"a",
    0xE3: b"a",
    0xE4: b"a",
    0xE5: b"a",
    0xC7: b"C",
    0xE7: b"c",
    0xC8: b"E",
    0xC9: b"E",
    0xCA: b"E",
    0xCB: b"E",
    0xE8: b"e",
    0xE9: b"e",
    0xEA: b"e",
    0xEB: b"e",
    0xCC: b"I",
    0xCD: b"I",
    0xCE: b"I",
    0xCF: b"I",
    0xEC: b"i",
    0xED: b"i",
    0xEE: b"i",
    0xEF: b"i",
    0xD1: b"N",
    0xF1: b"n",
    0xD2: b"O",
    0xD3: b"O",
    0xD4: b"O",
    0xD5: b"O",
    0xD6: b"O",
    0xF2: b"o",
    0xF3: b"o",
    0xF4: b"o",
    0xF5: b"o",
    0xF6: b"o",
    0xD9: b"U",
    0xDA: b"U",
    0xDB: b"U",
    0xDC: b"U",
    0xF9: b"u",
    0xFA: b"u",
    0xFB: b"u",
    0xFC: b"u",
    0xDD: b"Y",
    0xFF: b"y",
    0xDF: b"ss",
    0x85: b"...",
    0x91: b"'",
    0x92: b"'",
    0x93: b"'",
    0x94: b"'",
    0xA1: b"",
    0xBF: b"",
}

PC_KEYS = {
    "DYNSTR01",
    "DIALBUFF",
    "LOADLOC",
    "LOADSPCE",
    "CTRecBuf",
}

MAX_TEXTE_AIS = 255

JETON_COMMANDE_JAM = re.compile(rb"(?:<>|[\xB0-\xC4]+)")

MARQUEURS_CONSOLE_PC = (
    "memory card",
    "carte memoire",
    "carte mémoire",
    "speicherkarte",
    "tarjeta de memoria",
    "scheda di memoria",
    "playstation",
)

RACCORDS_CONSOLE_PC = (
    " sur la",
    " sur le",
    " dans la",
    " dans le",
    " de la",
    " du",
    " on the",
    " in the",
    " from the",
    " of the",
    " auf der",
    " auf dem",
    " in der",
    " von der",
    " en la",
    " en el",
    " de la",
    " del",
    " sulla",
    " sul",
    " nella",
    " nel",
    " della",
    " del",
)

MOTS_LIAISON_FIN_PC = {
    "a",
    "à",
    "al",
    "alla",
    "am",
    "an",
    "at",
    "au",
    "auf",
    "aux",
    "bei",
    "by",
    "dalla",
    "dans",
    "de",
    "del",
    "della",
    "der",
    "des",
    "di",
    "die",
    "du",
    "el",
    "en",
    "for",
    "from",
    "im",
    "in",
    "la",
    "las",
    "le",
    "les",
    "lo",
    "los",
    "mit",
    "nel",
    "nella",
    "of",
    "on",
    "par",
    "para",
    "per",
    "por",
    "pour",
    "sul",
    "sulla",
    "sur",
    "the",
    "to",
    "von",
    "vom",
    "zu",
    "zum",
    "zur",
}

SECTOR_SIZE = 2048


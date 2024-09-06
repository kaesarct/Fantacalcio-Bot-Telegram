# Enum per le squadre
from enum import Enum


class Team(Enum):
    COM = "Como"
    BOL = "Bologna"
    EMP = "Empoli"
    JUV = "Juventus"
    MIL = "Milan"
    VEN = "Venezia"
    GEN = "Genoa"
    ROM = "Roma"
    ATA = "Atalanta"
    FIO = "Fiorentina"
    TOR = "Torino"
    LEC = "Lecce"
    CAG = "Cagliari"
    NAP = "Napoli"
    MON = "Monza"
    INT = "Inter"
    PAR = "Parma"
    UDI = "Udinese"
    LAZ = "Lazio"
    VER = "Verona"

day_of_week_map = {
    "mon": "Lun",
    "tue": "Mar",
    "wed": "Mer",
    "thu": "Gio",
    "fri": "Ven",
    "sat": "Sab",
    "sun": "Dom",
}

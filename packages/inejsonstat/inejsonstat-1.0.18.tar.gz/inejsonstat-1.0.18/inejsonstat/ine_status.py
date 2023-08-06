import enum


class Status(enum.Enum):
   D = "Definitive"
   P = "Provisional"
   E = "Estimated"
   UNKNOWN = "Unknown"
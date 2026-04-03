import re

# Expresión matemática: solo tokens válidos — números, funciones conocidas, operadores, paréntesis.
# Rechaza secuencias de letras arbitrarias (como "rm") y dobles puntos ("12..5").
_KNOWN_FUNCS = r"(?:sin|cos|tan|asin|acos|atan|sqrt|log10|log|exp|abs)"
_CONSTANT = r"(?:pi|e)"
_NUMBER = r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
_OPERATOR = r"[+\-*/^]"
_PAREN = r"[()]"
_SPACE = r"\s+"
EXPRESSION_REGEX = re.compile(
    r"^(?:" + _NUMBER + r"|" + _KNOWN_FUNCS + r"|" + _CONSTANT + r"|" + _OPERATOR + r"|" + _PAREN + r"|" + _SPACE + r")+$"
)

# Email RFC 5322 simplificado
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Password: mínimo 8 chars, 1 mayúscula, 1 número
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*\d).{8,}$")

# UUID v4
UUID_V4_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

# Preference key: letras y guión bajo, 3-50 chars
PREFERENCE_KEY_REGEX = re.compile(r"^[a-zA-Z_]{3,50}$")

# Device ID: alfanumérico + guiones, 8-64 chars
DEVICE_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{8,64}$")

# Número decimal con notación científica opcional
NUMBER_REGEX = re.compile(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$")

# Unidad de medida
UNIT_REGEX = re.compile(r"^[a-zA-Z/]{1,20}$")

# Entity type para sync
ENTITY_TYPE_REGEX = re.compile(r"^[a-zA-Z_]{3,50}$")


def validate_expression(value: str) -> bool:
    return bool(EXPRESSION_REGEX.match(value.strip()))

def validate_email(value: str) -> bool:
    return bool(EMAIL_REGEX.match(value))

def validate_password(value: str) -> bool:
    return bool(PASSWORD_REGEX.match(value))

def validate_uuid_v4(value: str) -> bool:
    return bool(UUID_V4_REGEX.match(value.lower()))

def validate_preference_key(value: str) -> bool:
    return bool(PREFERENCE_KEY_REGEX.match(value))

def validate_device_id(value: str) -> bool:
    return bool(DEVICE_ID_REGEX.match(value))

def validate_number(value: str) -> bool:
    return bool(NUMBER_REGEX.match(value))

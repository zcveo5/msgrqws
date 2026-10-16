import os
from pathlib import Path
from typing import Any, Dict, Union

# Специальные маркеры для сохранения оригинальных типов данных
TYPE_MARKERS = {
    "bool": "__TYPE_BOOL__:",
    "int": "__TYPE_INT__:",
    "float": "__TYPE_FLOAT__:",
    "str": "",  # Строки сохраняются как есть
}


def save_dict_to_fs(data: Dict[str, Any], base_path: Union[str, Path]) -> None:
    """Сохраняет словарь в файловую систему.

    Ключ со словарем -> папка.
    Ключ с простым значением -> файл без расширения.
    """
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)

    for key, value in data.items():
        file_or_dir_path = base_path / str(key)

        if isinstance(value, dict):
            # Если значение — словарь, рекурсивно создаем папку
            save_dict_to_fs(value, file_or_dir_path)

        elif isinstance(value, bool):  # Важно: bool наследуется от int, проверяем первым
            content = f"{TYPE_MARKERS['bool']}{value}"
            file_or_dir_path.write_text(content, encoding="utf-8")

        elif isinstance(value, int):
            content = f"{TYPE_MARKERS['int']}{value}"
            file_or_dir_path.write_text(content, encoding="utf-8")

        elif isinstance(value, float):
            content = f"{TYPE_MARKERS['float']}{value}"
            file_or_dir_path.write_text(content, encoding="utf-8")

        elif isinstance(value, str):
            file_or_dir_path.write_text(value, encoding="utf-8")

        else:
            raise TypeError(f"Неподдерживаемый тип данных для ключа '{key}': {type(value)}")


def load_dict_from_fs(base_path: Union[str, Path]) -> Dict[str, Any]:
    """Загружает словарь из файловой системы обратно в Python-объект."""
    base_path = Path(base_path)
    result: Dict[str, Any] = {}

    if not base_path.exists():
        raise FileNotFoundError(f"Путь {base_path} не найден.")

    for item in base_path.iterdir():
        key = item.name

        if item.is_dir():
            # Если объект — директория, рекурсивно считываем ее содержимое
            result[key] = load_dict_from_fs(item)

        elif item.is_file():
            content = item.read_text(encoding="utf-8")

            # Восстанавливаем оригинальные типы данных по маркерам
            if content.startswith(TYPE_MARKERS["bool"]):
                raw_val = content[len(TYPE_MARKERS["bool"]) :]
                result[key] = raw_val == "True"

            elif content.startswith(TYPE_MARKERS["int"]):
                raw_val = content[len(TYPE_MARKERS["int"]) :]
                result[key] = int(raw_val)

            elif content.startswith(TYPE_MARKERS["float"]):
                raw_val = content[len(TYPE_MARKERS["float"]) :]
                result[key] = float(raw_val)

            else:
                result[key] = content

    return result
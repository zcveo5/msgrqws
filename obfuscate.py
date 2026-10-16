import ast
import random
import string


def get_random(l=16):
    return ''.join(random.sample(string.ascii_letters, l))


class GlobalVariableCollector(ast.NodeVisitor):
    """
    Этот класс просто гуляет по дереву и находит все переменные,
    которые объявляются на глобальном уровне (вне функций и классов).
    """

    def __init__(self, whitelist):
        self.global_vars = set()
        self.whitelist = whitelist
        self._in_function = False
        self._in_class = False  # ИСПРАВЛЕНО: добавили флаг отслеживания класса

    def visit_ClassDef(self, node):
        # Запоминаем старое состояние и выставляем флаг класса
        old_class_state = self._in_class
        self._in_class = True

        # Обходим внутренности класса, но благодаря флагу их пропустим
        self.generic_visit(node)
        self._in_class = old_class_state

    def visit_FunctionDef(self, node):
        # Если функция внутри класса — это метод (например, debugtools). ИГНОРИРУЕМ!
        if self._in_class:
            return

        # Если это глобальная функция (вне класса и вне других функций)
        if not self._in_function:
            if node.name not in self.whitelist:
                self.global_vars.add(node.name)

        # Заходим внутрь функции
        old_func_state = self._in_function
        self._in_function = True
        self.generic_visit(node)
        self._in_function = old_func_state

    def visit_Assign(self, node):
        # Собираем переменные только если мы НЕ в функции и НЕ в классе
        if not self._in_function and not self._in_class:
            for target in node.targets:
                # Обычное присваивание: base_conf = ...
                if isinstance(target, ast.Name):
                    if target.id not in self.whitelist:
                        self.global_vars.add(target.id)
                # Множественное присваивание: x, y = ...
                elif isinstance(target, (ast.Tuple, ast.List)):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name) and elt.id not in self.whitelist:
                            self.global_vars.add(elt.id)

        self.generic_visit(node)


class Plus13Transformer(ast.NodeTransformer):
    """
    Этот класс обходит AST-дерево.
    Когда он видит объявление функции (FunctionDef), он меняет её имя.
    """

    def __init__(self):
        self._names = {}
        self._whitelist = set()  # ИСПРАВЛЕНО: Явно объявили белый список!
        self._in_f_string = False
        self._in_class = False   # ИСПРАВЛЕНО: Добавили флаг класса для трансформера
        self._str_decode_name = get_random(32)

    def visit_Nonlocal(self, node):
        """
        Перехватывает: nonlocal lb1, lb2, cont
        И переименовывает переменные в соответствии с нашей таблицей self._names
        """
        new_names = []
        for name in node.names:
            if name in self._names:
                new_names.append(self._names[name])
                print(f"[!] Переименована переменная в nonlocal: '{name}' -> '{self._names[name]}'")
            else:
                new_names.append(name)

        node.names = new_names
        return node

    def visit_JoinedStr(self, node):
        # Если f-строка пустая, возвращаем её как есть
        if not node.values:
            return node

        # Собираем дерево сложения элементов f-строки
        # Переводим каждый элемент в строку через str(x), если это значение
        current_node = None
        for val in node.values:
            # Если это статичный текст (Constant)
            if isinstance(val, ast.Constant):
                next_node = val
            # Если это переменная/выражение в фигурных скобках (FormattedValue)
            elif isinstance(val, ast.FormattedValue):
                # Оборачиваем значение в вызов str(), чтобы не упало при сложении
                next_node = ast.Call(
                    func=ast.Name(id='str', ctx=ast.Load()),
                    args=[val.value],
                    keywords=[]
                )
            else:
                next_node = val

            if current_node is None:
                current_node = next_node
            else:
                # Складываем: current_node + next_node
                current_node = ast.BinOp(
                    left=current_node,
                    op=ast.Add(),
                    right=next_node
                )

        # Рекурсивно обрабатываем получившееся дерево (чтобы visit_Constant зашифровал константы!)
        return self.visit(current_node)

    def visit_Constant(self, node):
        # Шифруем строку ТОЛЬКО если она не пустая и мы НЕ внутри f-строки
        if isinstance(node.value, str) and len(node.value) > 0 and not self._in_f_string:
            raw_bytes = node.value.encode('utf-8')
            encrypted = bytes([c ^ 42 for c in raw_bytes])

            new_node = ast.Call(
                func=ast.Name(id=self._str_decode_name, ctx=ast.Load()),
                args=[ast.Constant(value=encrypted)],
                keywords=[]
            )
            return new_node
        return node

    def _resolve_function_name(self, name):
        if name in self._whitelist:  # ИСПРАВЛЕНО: Проверяем белый список перед генерацией!
            return name
        if name not in self._names:
            self._names[name] = get_random()
        return self._names[name]

    def visit_FunctionDef(self, node):
        # ИСПРАВЛЕНО: Если мы внутри класса — это метод. Не трогаем его имя вообще!
        if self._in_class:
            return self.generic_visit(node)

        # 1. Меняем имя самой функции (если она не в whitelist)
        if node.name not in self._whitelist:
            new_name = self._resolve_function_name(node.name)
            node.name = new_name

        # Сохраняем старую глобальную/родительскую таблицу имен
        old_names_state = self._names.copy()

        # 2. Ищем все локальные переменные в теле функции
        # Находим аргументы функции: def func(a, b)
        for arg in node.args.args:
            if arg.arg not in self._whitelist:
                self._names[arg.arg] = get_random()
                arg.arg = self._names[arg.arg] # Сразу переименовываем аргумент в объявлении

        # 3. Обходим тело функции с обновленной таблицей self._names
        self.generic_visit(node)

        # 4. Восстанавливаем глобальную таблицу (чтобы локальные переменные не утекли наружу)
        self._names = old_names_state
        return node

    def visit_Global(self, node):
        """
        Перехватывает: global main, chat_window, font_theme
        И переименовывает переменные в соответствии с нашей таблицей self._names
        """
        new_names = []
        for name in node.names:
            if name in self._names:
                new_names.append(self._names[name])
                print(f"[!] Переименована переменная в global: '{name}' -> '{self._names[name]}'")
            else:
                new_names.append(name)

        node.names = new_names
        return node

    def visit_Call(self, node):
        # Если это простой вызов функции по имени (например, my_func())
        if isinstance(node.func, ast.Name):
            if node.func.id in self._names:
                new_name = self._resolve_function_name(node.func.id)
                print(f"[!] Найден вызов функции: '{node.func.id}()' -> меняем на '{new_name}'")
                node.func.id = new_name

        # Идём дальше по дереву
        return self.generic_visit(node)

    def visit_Name(self, node):
        """
        Переименовывает переменную во ВСЕХ контекстах (и при записи, и при чтении).
        """
        # Если имя переменной есть в нашей таблице переименований — меняем его!
        if node.id in self._names:
            node.id = self._names[node.id]

        return self.generic_visit(node)

    def visit_Import(self, node):
        """
        Перехватывает: import data.lib.connect.chat as chat
        Превращает в: chat = __import__('importlib').import_module('data.lib.connect.chat')
        """
        new_nodes = []
        for alias in node.names:
            print(alias.name, 'IMPORT')

            # Настоящее имя модуля (например, 'data.lib.connect.chat')
            module_name = alias.name

            # Имя переменной, в которую импортируем (псевдоним из 'as ...', либо само имя модуля)
            local_name = alias.asname if alias.asname else module_name

            # Защита от точек: если импортируем без 'as' (например, 'import os.path'),
            # локальная переменная в Python создается по первому слову ('os')
            if not alias.asname and '.' in local_name:
                local_name = local_name.split('.')[0]

            # Если мы обфусцируем локальное имя псевдонима
            if alias.asname and alias.asname not in self._whitelist:
                local_name = self._resolve_function_name(alias.asname)

            # Строем вызов: __import__('importlib').import_module('module_name')
            # Это вернет строго конечный модуль, независимо от уровня вложенности пакетов!
            import_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Call(
                        func=ast.Name(id='__import__', ctx=ast.Load()),
                        args=[ast.Constant(value='importlib')],
                        keywords=[]
                    ),
                    attr='import_module',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value=module_name)],
                keywords=[]
            )

            # Строим присваивание: local_name = ...
            assign_node = ast.Assign(
                targets=[ast.Name(id=local_name, ctx=ast.Store())],
                value=import_call
            )
            new_nodes.append(assign_node)

        # Возвращаем список новых нод вместо старого импорта
        return new_nodes

    def visit_ImportFrom(self, node):
        if not node.module:
            return node

        module_name = node.module

        # === КЕЙС 1: Импорт звездочкой (from module import *) ===
        if len(node.names) == 1 and node.names[0].name == '*':
            # (Тут твой рабочий код с globals().update(...) через importlib.import_module)
            importlib_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Call(func=ast.Name(id='__import__', ctx=ast.Load()), args=[ast.Constant(value='importlib')], keywords=[]),
                    attr='import_module', ctx=ast.Load()
                ),
                args=[ast.Constant(value=module_name)],
                keywords=[]
            )
            globals_update = ast.Call(
                func=ast.Attribute(
                    value=ast.Call(func=ast.Name(id='globals', ctx=ast.Load()), args=[], keywords=[]),
                    attr='update', ctx=ast.Load()
                ),
                args=[ast.Attribute(value=importlib_call, attr='__dict__', ctx=ast.Load())],
                keywords=[]
            )
            return ast.Expr(value=globals_update)


        # === КЕЙС 2: Импорт конкретных имен (from tkinter.messagebox import askyesno) ===
        temp_var_name = get_random()
        names_to_import = [alias.name for alias in node.names]

        # Строим: _temp = __import__('importlib').import_module('tkinter.messagebox')
        # Это вернет строго конечный sub-module/package!
        import_call = ast.Call(
            func=ast.Attribute(
                value=ast.Call(
                    func=ast.Name(id='__import__', ctx=ast.Load()),
                    args=[ast.Constant(value='importlib')],
                    keywords=[]
                ),
                attr='import_module',
                ctx=ast.Load()
            ),
            args=[ast.Constant(value=module_name)],
            keywords=[]
        )

        assign_temp = ast.Assign(
            targets=[ast.Name(id=temp_var_name, ctx=ast.Store())],
            value=import_call
        )

        new_nodes = [assign_temp]

        # Вытаскиваем функции ручками из правильного объекта
        for alias in node.names:
            orig_name = alias.name
            local_name = alias.asname if alias.asname else orig_name

            # === ЗАЩИТА ОТ ТОЧЕК В ИМЕНИ ===
            # Если имя содержит точку (например, 'messagebox' из-за сложного пути),
            # Python на самом деле создает локальную переменную с именем последней части.
            if '.' in local_name:
                local_name = local_name.split('.')[-1]

            # Если мы обфусцируем это имя (или оно уже в таблице)
            if alias.asname or local_name in self._names:
                local_name = self._resolve_function_name(local_name)

            # Строим: local_name = _temp_xxx.orig_name
            get_attribute = ast.Attribute(
                value=ast.Name(id=temp_var_name, ctx=ast.Load()),
                attr=orig_name,
                ctx=ast.Load()
            )

            # Теперь тут гарантированно чистое имя без точек в id!
            assign_local = ast.Assign(
                targets=[ast.Name(id=local_name, ctx=ast.Store())],
                value=get_attribute
            )
            new_nodes.append(assign_local)

        # del _temp
        delete_temp = ast.Delete(
            targets=[ast.Name(id=temp_var_name, ctx=ast.Del())]
        )
        new_nodes.append(delete_temp)

        return new_nodes

    def visit_Attribute(self, node):
        # Переименовываем только сам объект (node.value), к которому обращаемся!
        # node.attr (то, что после точки) оставляем КАК ЕСТЬ.
        node.value = self.visit(node.value)
        return node

    def visit_ClassDef(self, node):
        # Помечаем, что зашли в класс. Методы класса переименовывать нельзя!
        old_class_state = self._in_class
        self._in_class = True

        # Обходим тело класса
        self.generic_visit(node)

        self._in_class = old_class_state
        return node

# --- ТЕСТ —--

# Исходный код, который мы хотим «обфусцировать»
tree = ast.parse(open('./msgr.py').read())

# Шаг 2: Определяем белый список (то, что нельзя переименовывать ни при каких условиях)
# Сюда обязательно заносим json, sys, open, твой дешифратор и т.д.
whitelist = {'print', 'len', 'range', 'str', 'bytes', 'decrypt', 'globals', '__import__', 'json', 'open'}

# Шаг 3: Собираем ВСЕ глобальные переменные (включая base_conf внутри try/except!)
collector = GlobalVariableCollector(whitelist)
collector.visit(tree)

print(f"[!] Найдены глобальные переменные для обфускации: {collector.global_vars}")

# Шаг 4: Создаем наш основной трансформер и заранее передаем ему собранные глобальные переменные
transformer = Plus13Transformer()
transformer._whitelist = whitelist

# Заранее генерируем случайные имена для всех собранных глобальных переменных!
for var_name in collector.global_vars:
    transformer._names[var_name] = get_random()

# Шаг 5: Запускаем обфускацию дерева
modified_tree = transformer.visit(tree)
ast.fix_missing_locations(modified_tree)
# Шаг 3: Исправляем координаты строк/колонок в измененном дереве (обязательно для генерации)

# Шаг 4: Превращаем измененное AST-дерево обратно в текст Python-кода
decrypt_func_source = f"""
def {transformer._str_decode_name}(encrypted_bytes):
    return bytes([b ^ 42 for b in encrypted_bytes]).decode('utf-8')
"""
# Парсим функцию дешифратора в AST
decrypt_ast = ast.parse(decrypt_func_source)

# Забираем саму ноду объявления функции (FunctionDef)
# и вставляем её в самый верх тела нашего основного модуля (на индекс 0)
modified_tree.body.insert(0, decrypt_ast.body[0])


# --- ШАГ 4: Фиксим локации и генерируем финальный код
ast.fix_missing_locations(modified_tree)
result_code = ast.unparse(modified_tree)

with open('./OOmsgr.py', 'w') as fl:
    fl.write(result_code)
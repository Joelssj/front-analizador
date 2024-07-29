import re
import json

def analyze_syntactic(code):
    errors = []

    # Intentar parsear como JSON completo
    try:
        data = json.loads(code)
        if isinstance(data, dict):
            # Verificar que las claves necesarias estén presentes
            if "table" not in data or "id" not in data:
                errors.append("El JSON debe contener las claves 'table' e 'id'.")
            # Verificar tipos de valores
            if not isinstance(data.get("table"), str):
                errors.append("El valor de 'table' debe ser una cadena.")
            if not isinstance(data.get("id"), int):
                errors.append("El valor de 'id' debe ser un entero.")
            if not errors:
                return "Sintaxis correcta"
        else:
            errors.append("El JSON debe ser un objeto.")
    except json.JSONDecodeError:
        # Si no es un JSON válido, continuar con el análisis de SQL
        pass

    # Si no es JSON, proceder con el análisis de SQL
    tokens = re.findall(r"'.*?'|\b\w+\b|[(),;=<>]", code)

    def expect(token, expected, index):
        if token.upper() != expected:
            errors.append(f"Se esperaba '{expected}' pero se encontró '{token}' en la posición {index}")
            return False
        return True

    def parse_create_table(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'CREATE', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'TABLE', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de tabla después de 'TABLE' en la posición {index}")
            return token_count
        index += 1

        if not expect(tokens[index], '(', index):
            return token_count
        index += 1

        while index < token_count and tokens[index] != ')':
            if tokens[index].upper() == 'PRIMARY':
                index += 1
                if not expect(tokens[index], 'KEY', index):
                    return token_count
                index += 1

                if not expect(tokens[index], '(', index):
                    return token_count
                index += 1

                if not re.match(r'\b\w+\b', tokens[index]):
                    errors.append(f"Se esperaba un nombre de columna para la clave primaria, pero se encontró '{tokens[index]}' en la posición {index}")
                    return token_count
                index += 1

                if not expect(tokens[index], ')', index):
                    return token_count
                index += 1
            else:
                if not re.match(r'\b\w+\b', tokens[index]):
                    errors.append(f"Se esperaba un nombre de columna, pero se encontró '{tokens[index]}' en la posición {index}")
                    return token_count
                index += 1

                if tokens[index].upper() not in ['INT', 'VARCHAR', 'DATE', 'DECIMAL']:
                    errors.append(f"Se esperaba un tipo de dato, pero se encontró '{tokens[index]}' en la posición {index}")
                    return token_count
                index += 1

                if tokens[index] == '(':
                    index += 1
                    if not re.match(r'\b\d+\b', tokens[index]):
                        errors.append(f"Se esperaba un número dentro de los paréntesis, pero se encontró '{tokens[index]}' en la posición {index}")
                        return token_count
                    index += 1

                    if tokens[index] == ',':
                        index += 1
                        if not re.match(r'\b\d+\b', tokens[index]):
                            errors.append(f"Se esperaba un número después de la coma en los paréntesis, pero se encontró '{tokens[index]}' en la posición {index}")
                            return token_count
                        index += 1

                    if not expect(tokens[index], ')', index):
                        return token_count
                    index += 1

                while tokens[index].upper() in ['PRIMARY', 'NOT', 'AUTO_INCREMENT']:
                    if tokens[index].upper() == 'PRIMARY':
                        index += 1
                        if not expect(tokens[index], 'KEY', index):
                            return token_count
                    if tokens[index].upper() == 'NOT':
                        index += 1
                        if not expect(tokens[index], 'NULL', index):
                            return token_count
                    index += 1

            if tokens[index] == ',':
                index += 1
            elif tokens[index] == ')':
                break
            else:
                errors.append(f"Se esperaba ',' o ')', pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count

        if not expect(tokens[index], ')', index):
            return token_count
        index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_create_database(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'CREATE', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'DATABASE', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de base de datos después de 'DATABASE' en la posición {index}")
            return token_count
        index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_use_database(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'USE', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de base de datos después de 'USE' en la posición {index}")
            return token_count
        index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_drop_table(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'DROP', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'TABLE', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de tabla después de 'TABLE' en la posición {index}")
            return token_count
        index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_drop_database(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'DROP', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'DATABASE', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de base de datos después de 'DATABASE' en la posición {index}")
            return token_count
        index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_alter_table(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'ALTER', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'TABLE', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de tabla después de 'TABLE' en la posición {index}")
            return token_count
        index += 1

        if tokens[index].upper() == 'RENAME':
            index += 1
            if not expect(tokens[index], 'TO', index):
                return token_count
            index += 1

            if not re.match(r'\b\w+\b', tokens[index]):
                errors.append(f"Se esperaba un nuevo nombre de tabla después de 'TO' en la posición {index}")
                return token_count
            index += 1

        elif tokens[index].upper() == 'ADD':
            index += 1
            if not expect(tokens[index], 'COLUMN', index):
                return token_count
            index += 1

            if not re.match(r'\b\w+\b', tokens[index]):
                errors.append(f"Se esperaba un nombre de columna después de 'COLUMN' en la posición {index}")
                return token_count
            index += 1

            if tokens[index].upper() not in ['INT', 'VARCHAR', 'DATE', 'DECIMAL']:
                errors.append(f"Se esperaba un tipo de dato después del nombre de la columna en la posición {index}")
                return token_count
            index += 1

            if tokens[index] == '(':
                index += 1
                if not re.match(r'\b\d+\b', tokens[index]):
                    errors.append(f"Se esperaba un número dentro de los paréntesis, pero se encontró '{tokens[index]}' en la posición {index}")
                    return token_count
                index += 1

                if tokens[index] == ',':
                    index += 1
                    if not re.match(r'\b\d+\b', tokens[index]):
                        errors.append(f"Se esperaba un número después de la coma en los paréntesis, pero se encontró '{tokens[index]}' en la posición {index}")
                        return token_count
                    index += 1

                if not expect(tokens[index], ')', index):
                    return token_count
                index += 1

        elif tokens[index].upper() == 'DROP':
            index += 1
            if not expect(tokens[index], 'COLUMN', index):
                return token_count
            index += 1

            if not re.match(r'\b\w+\b', tokens[index]):
                errors.append(f"Se esperaba un nombre de columna después de 'COLUMN' en la posición {index}")
                return token_count
            index += 1

        elif tokens[index].upper() == 'MODIFY':
            index += 1
            if not expect(tokens[index], 'COLUMN', index):
                return token_count
            index += 1

            if not re.match(r'\b\w+\b', tokens[index]):
                errors.append(f"Se esperaba un nombre de columna después de 'COLUMN' en la posición {index}")
                return token_count
            index += 1

            if tokens[index].upper() not in ['INT', 'VARCHAR', 'DATE', 'DECIMAL']:
                errors.append(f"Se esperaba un tipo de dato después del nombre de la columna en la posición {index}")
                return token_count
            index += 1

            if tokens[index] == '(':
                index += 1
                if not re.match(r'\b\d+\b', tokens[index]):
                    errors.append(f"Se esperaba un número dentro de los paréntesis, pero se encontró '{tokens[index]}' en la posición {index}")
                    return token_count
                index += 1

                if tokens[index] == ',':
                    index += 1
                    if not re.match(r'\b\d+\b', tokens[index]):
                        errors.append(f"Se esperaba un número después de la coma en los paréntesis, pero se encontró '{tokens[index]}' en la posición {index}")
                        return token_count
                    index += 1

                if not expect(tokens[index], ')', index):
                    return token_count
                index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_insert_into(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'INSERT', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'INTO', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de tabla después de 'INTO' en la posición {index}")
            return token_count
        index += 1

        if not expect(tokens[index], '(', index):
            return token_count
        index += 1

        while index < token_count and tokens[index] != ')':
            if not re.match(r'\b\w+\b', tokens[index]):
                errors.append(f"Se esperaba un nombre de columna, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

            if tokens[index] == ',':
                index += 1
            elif tokens[index] == ')':
                break
            else:
                errors.append(f"Se esperaba ',' o ')', pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count

        if not expect(tokens[index], ')', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'VALUES', index):
            return token_count
        index += 1

        if not expect(tokens[index], '(', index):
            return token_count
        index += 1

        while index < token_count and tokens[index] != ')':
            if not re.match(r"'[^']*'", tokens[index]) and not re.match(r'\b\d+\b', tokens[index]):
                errors.append(f"Se esperaba un valor, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

            if tokens[index] == ',':
                index += 1
            elif tokens[index] == ')':
                break
            else:
                errors.append(f"Se esperaba ',' o ')', pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count

        if not expect(tokens[index], ')', index):
            return token_count
        index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_delete_from(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'DELETE', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'FROM', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de tabla después de 'FROM' en la posición {index}")
            return token_count
        index += 1

        if tokens[index].upper() == 'WHERE':
            index += 1
            if not re.match(r'\b\w+\b', tokens[index]):
                errors.append(f"Se esperaba un nombre de columna en la cláusula WHERE, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

            if not re.match(r'=|<|>|<=|>=|<>', tokens[index]):
                errors.append(f"Se esperaba un operador de comparación en la cláusula WHERE, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

            if not re.match(r"'[^']*'|\b\d+\b", tokens[index]):
                errors.append(f"Se esperaba un valor en la cláusula WHERE, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_update(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'UPDATE', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de tabla después de 'UPDATE' en la posición {index}")
            return token_count
        index += 1

        if not expect(tokens[index], 'SET', index):
            return token_count
        index += 1

        while index < token_count and tokens[index] != 'WHERE':
            if not re.match(r'\b\w+\b', tokens[index]):
                errors.append(f"Se esperaba un nombre de columna en la cláusula SET, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

            if not expect(tokens[index], '=', index):
                return token_count
            index += 1

            if not re.match(r"'[^']*'|\b\d+\b", tokens[index]):
                errors.append(f"Se esperaba un valor en la cláusula SET, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

            if tokens[index] == ',':
                index += 1
            elif tokens[index] == 'WHERE':
                break
            else:
                errors.append(f"Se esperaba ',' o 'WHERE', pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count

        if tokens[index].upper() == 'WHERE':
            index += 1
            if not re.match(r'\b\w+\b', tokens[index]):
                errors.append(f"Se esperaba un nombre de columna en la cláusula WHERE, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

            if not re.match(r'=|<|>|<=|>=|<>', tokens[index]):
                errors.append(f"Se esperaba un operador de comparación en la cláusula WHERE, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

            if not re.match(r"'[^']*'|\b\d+\b", tokens[index]):
                errors.append(f"Se esperaba un valor en la cláusula WHERE, pero se encontró '{tokens[index]}' en la posición {index}")
                return token_count
            index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    def parse_rename_table(tokens, start_index):
        index = start_index
        token_count = len(tokens)

        if not expect(tokens[index], 'RENAME', index):
            return token_count
        index += 1

        if not expect(tokens[index], 'TABLE', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nombre de tabla después de 'TABLE' en la posición {index}")
            return token_count
        index += 1

        if not expect(tokens[index], 'TO', index):
            return token_count
        index += 1

        if not re.match(r'\b\w+\b', tokens[index]):
            errors.append(f"Se esperaba un nuevo nombre de tabla después de 'TO' en la posición {index}")
            return token_count
        index += 1

        if tokens[index] == ';':
            index += 1
        else:
            errors.append(f"Se esperaba ';' al final de la declaración en la posición {index}")
            return token_count

        return index

    index = 0
    while index < len(tokens):
        if tokens[index].upper() == 'CREATE' and index + 1 < len(tokens) and tokens[index + 1].upper() == 'TABLE':
            index = parse_create_table(tokens, index)
        elif tokens[index].upper() == 'CREATE' and index + 1 < len(tokens) and tokens[index + 1].upper() == 'DATABASE':
            index = parse_create_database(tokens, index)
        elif tokens[index].upper() == 'USE':
            index = parse_use_database(tokens, index)
        elif tokens[index].upper() == 'DROP' and index + 1 < len(tokens) and tokens[index + 1].upper() == 'TABLE':
            index = parse_drop_table(tokens, index)
        elif tokens[index].upper() == 'DROP' and index + 1 < len(tokens) and tokens[index + 1].upper() == 'DATABASE':
            index = parse_drop_database(tokens, index)
        elif tokens[index].upper() == 'ALTER' and index + 1 < len(tokens) and tokens[index + 1].upper() == 'TABLE':
            index = parse_alter_table(tokens, index)
        elif tokens[index].upper() == 'INSERT' and index + 1 < len(tokens) and tokens[index + 1].upper() == 'INTO':
            index = parse_insert_into(tokens, index)
        elif tokens[index].upper() == 'DELETE' and index + 1 < len(tokens) and tokens[index + 1].upper() == 'FROM':
            index = parse_delete_from(tokens, index)
        elif tokens[index].upper() == 'UPDATE':
            index = parse_update(tokens, index)
        elif tokens[index].upper() == 'RENAME' and index + 1 < len(tokens) and tokens[index + 1].upper() == 'TABLE':
            index = parse_rename_table(tokens, index)
        else:
            errors.append(f"Token inesperado: '{tokens[index]}' en la posición {index}")
            index += 1

    if not errors:
        return "Sintaxis correcta"
    else:
        return "\n".join(errors)

# Ejemplo de uso
code = "INSERT INTO Personas (Nombre, Edad, Correo) VALUES ('Juan Pérez', 30, 'juan.perez@example.com');"
result = analyze_syntactic(code)
print(result)

# Prueba con DROP DATABASE
code_drop = "DROP DATABASE D;"
result_drop = analyze_syntactic(code_drop)
print(result_drop)

# Prueba con ALTER TABLE
code_alter_add = "ALTER TABLE Personas ADD COLUMN Telefono VARCHAR(15);"
result_alter_add = analyze_syntactic(code_alter_add)
print(result_alter_add)

code_alter_drop = "ALTER TABLE Personas DROP COLUMN Edad;"
result_alter_drop = analyze_syntactic(code_alter_drop)
print(result_alter_drop)

code_alter_modify = "ALTER TABLE Personas MODIFY COLUMN Nombre VARCHAR(100);"
result_alter_modify = analyze_syntactic(code_alter_modify)
print(result_alter_modify)

# Prueba con RENAME TABLE
code_rename = "RENAME TABLE Personas TO Usuarios;"
result_rename = analyze_syntactic(code_rename)
print(result_rename)

# Prueba con DELETE en formato JSON
code_delete_json = '{"table": "Personas", "id": 1}'
result_delete_json = analyze_syntactic(code_delete_json)
print(result_delete_json)

# Prueba con DELETE en SQL
code_delete_sql = "DELETE FROM Usuarios WHERE Usuario_ID = 1;"
result_delete_sql = analyze_syntactic(code_delete_sql)
print(result_delete_sql)
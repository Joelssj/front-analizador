import re

def analyze_semantic(code):
    errors = []

    # Verificación de tipos de datos y restricciones
    def check_data_types_and_constraints(code):
        data_types = ['INT', 'VARCHAR', 'DATE', 'DECIMAL']
        tokens = re.findall(r'\b\w+\b|[(),;]', code)
        index = 0

        while index < len(tokens):
            token = tokens[index].upper()
            if token in ['CREATE', 'ALTER']:
                index += 1
                if index < len(tokens) and tokens[index].upper() == 'TABLE':
                    index += 1
                    if index < len(tokens) and re.match(r'\b\w+\b', tokens[index]):
                        index += 1
                        if index < len(tokens) and tokens[index] == '(':
                            index += 1
                            while index < len(tokens) and tokens[index] != ')':
                                column_name = tokens[index]
                                index += 1
                                if index < len(tokens) and tokens[index].upper() in data_types:
                                    data_type = tokens[index].upper()
                                    index += 1
                                    if data_type == 'VARCHAR':
                                        if index < len(tokens) and tokens[index] == '(':
                                            index += 1
                                            if index >= len(tokens) or not re.match(r'\b\d+\b', tokens[index]):
                                                errors.append(f"Se esperaba un número dentro de los paréntesis para VARCHAR, pero se encontró '{tokens[index]}' en la posición {index}")
                                            index += 1
                                            if index < len(tokens) and tokens[index] != ')':
                                                errors.append(f"Se esperaba ')' después del tamaño de VARCHAR, pero se encontró '{tokens[index]}' en la posición {index}")
                                            index += 1
                                    elif data_type == 'DECIMAL':
                                        if index < len(tokens) and tokens[index] == '(':
                                            index += 1
                                            if index >= len(tokens) or not re.match(r'\b\d+\b', tokens[index]):
                                                errors.append(f"Se esperaba un número dentro de los paréntesis para DECIMAL, pero se encontró '{tokens[index]}' en la posición {index}")
                                            index += 1
                                            if index < len(tokens) and tokens[index] == ',':
                                                index += 1
                                                if index >= len(tokens) or not re.match(r'\b\d+\b', tokens[index]):
                                                    errors.append(f"Se esperaba un número después de la coma en los paréntesis para DECIMAL, pero se encontró '{tokens[index]}' en la posición {index}")
                                                index += 1
                                            if index < len(tokens) and tokens[index] != ')':
                                                errors.append(f"Se esperaba ')' después de los números de DECIMAL, pero se encontró '{tokens[index]}' en la posición {index}")
                                            index += 1
                                else:
                                    # Ignorar las palabras clave adicionales y las restricciones
                                    if tokens[index].upper() not in ['PRIMARY', 'KEY', 'NOT', 'NULL', 'AUTO_INCREMENT', ',', '(', ')']:
                                        errors.append(f"Tipo de dato inválido '{tokens[index]}' en la posición {index}")
                                    index += 1
                                if index < len(tokens) and tokens[index] == ',':
                                    index += 1
            else:
                index += 1

    # Realizar la verificación de tipos de datos y restricciones
    check_data_types_and_constraints(code)

    return "\n".join(errors) if errors else "Semánticamente correcto"

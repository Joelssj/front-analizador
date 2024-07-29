import re

def analyze_lexical(code):
    tokens = re.findall(r'\w+|[^\s\w]', code)
    lexical_results = []
    total_results = {
        'KEYWORD': 0,
        'IDENTIFIER': 0,
        'OPERATOR': 0,
        'SYMBOL': 0,
        'NUMERIC_CONSTANT': 0,
        'STRING_CONSTANT': 0,
        'COMMENT': 0
    }

    keywords = {'CREATE', 'TABLE', 'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'INT', 'VARCHAR'}
    operators = {'=', '>', '<', '!', '+', '-', '*', '/'}
    symbols = {'(', ')', '{', '}', '[', ']', ',', ';', '.'}

    for token in tokens:
        token_type = ''
        if token.upper() in keywords:
            token_type = 'KEYWORD'
        elif token in operators:
            token_type = 'OPERATOR'
        elif token in symbols:
            token_type = 'SYMBOL'
        elif re.match(r'^\d+$', token):
            token_type = 'NUMERIC_CONSTANT'
        elif re.match(r'^".*"$', token) or re.match(r"^'.*'$", token):
            token_type = 'STRING_CONSTANT'
        elif token.startswith('--') or token.startswith('#'):
            token_type = 'COMMENT'
        else:
            token_type = 'IDENTIFIER'
        
        lexical_results.append({'token': token, 'type': token_type})
        total_results[token_type] += 1

    return lexical_results, total_results

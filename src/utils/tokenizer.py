import re
from typing import Any, Generator, List

def tokenize(code) -> Generator[tuple[str, str | None, str, str | Any | None, Any, int] | Any, Any, None]:
    token_specification = [
        ('TRANSICION', r'>>.*'),
        ('ESCENA', r'>.*'),
        ('ACCION', r'<[^>]+>'),
        ('PERSONAJE', r'@(?:[^\s@,.:;]+(?:@[^\s@,.:;]+)*)'),
        ('ACOTACION', r'\([^)]+\)'),
        ('DIALOGO', r'--.*'),
        ('TITULO', r'\[T:\s*[^\]]+\]'),
        ('TEXTO', r'.+?(?=>>|>|<|@|\(|--|$)')
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    # Token ID counter
    token_id_counter = [1]
   
    # Function to recursively find nested tokens
    def find_tokens(text, line_num, line_start_pos=0):

        # Avoid creating a local variable
        nonlocal token_id_counter

        for mo in re.finditer(tok_regex, text, re.UNICODE):
            kind = mo.lastgroup
            value = mo.group()
            start_pos = mo.start()

            # Update line_num based on the number of newlines before the token
            line_num += value.count('\n')

            if kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')
            elif kind in ('ACCION', 'ACOTACION'):
                metatext = value[1:-1]
            elif kind == 'PERSONAJE':
                metatext = value[1:]
            elif kind in ('DIALOGO', 'TRANSICION'):
                metatext = value[2:]
            elif kind == 'TITULO':
                metatext = re.search(r'\[T:\s*(.*?)\]', value).group(1)
            elif kind == 'ESCENA':
                metatext = value[1:]
            elif kind == 'TEXTO':
                metatext = value

            else:
                metatext = None

            token_pos = start_pos + line_start_pos
            
            token_id = '.'.join(map(str, token_id_counter))

            yield (token_id, kind, value, metatext, line_num, token_pos)

            # If the token is a container token, recursively find tokens inside it
            if kind in ('ACCION', 'ACOTACION', 'DIALOGO', 'ESCENA', 'TRANSICION'):
                token_id_counter.append(1)
                for nested_token in find_tokens(metatext, line_num, token_pos + 1):
                    yield nested_token
                token_id_counter.pop()
            token_id_counter[-1] += 1

        line_num += 1  # Increment line_num for each line


    # Start tokenization
    line_num = 1
    for line in code.split('\n'):
        for token in find_tokens(line, line_num):
            yield token
        line_num += 1

def run_tokenizer(code: str) -> List[Generator[tuple[str, str | None, str, str | Any | None, Any, int] | Any, Any, None]]:
    return list(tokenize(code))

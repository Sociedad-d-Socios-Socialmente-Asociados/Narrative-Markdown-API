class TokenNode:
    def __init__(self, token_id, token_type, full_text, text, line_number, line_position):
        self.token_id = token_id
        self.token_type = token_type
        self.full_text = full_text
        self.text = text
        self.line_number = line_number
        self.line_position = line_position
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

def build_trees(token_list):
    nodes = {}
    root_list = []

    for token in token_list:
        token_id, token_type, full_text, text, line_number, line_position = token
        node = TokenNode(token_id, token_type, full_text, text, line_number, line_position)
        nodes[token_id] = node

        if '.' in token_id:
            parent_token_id = '.'.join(token_id.split('.')[:-1])
            nodes[parent_token_id].add_child(node)
        else:
            root_list.append(nodes[token_id])

    return root_list

def verify_trees(root_list):
    
    valid_relations = {
        'ESCENA': ['PERSONAJE', 'TEXTO'],
        'ACCION': ['PERSONAJE', 'ACOTACION', 'TEXTO'],
        'PERSONAJE': ['TEXTO'],
        'ACOTACION': ['PERSONAJE', 'TEXTO'],
        'DIALOGO': ['PERSONAJE', 'ACOTACION', 'TEXTO'],
        'TITULO': ['TEXTO'],
        'TRANSICION': ['TEXTO']
    }

    def verify_tree(root):
        if root is None:
            return None
        if root.token_type in valid_relations:
            for child in root.children:
                if child.token_type not in valid_relations[root.token_type]:
                    return f"Invalid nesting: {root.token_type} cannot contain {child.token_type} in line {child.line_number}."
        return None
    
    for root in root_list:
        error = verify_tree(root)
        if error:
            return error

def run_syntax_tree(token_list) -> tuple:
    root_list = build_trees(token_list)
    error = verify_trees(root_list)
    if not error:
        return root_list, True
    else:
        return error, False
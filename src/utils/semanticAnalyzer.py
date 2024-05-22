from typing import Any, Generator, List
from src.utils.syntaxTree import TokenNode

class SemanticError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SemanticAnalyzer:
    def __init__(self, root_nodes: List[TokenNode], token_list: List[Generator[tuple[str, str | None, str, str | Any | None, Any, int] | Any, Any, None]]):
        self.root_nodes = root_nodes
        self.token_list = list(token_list)

    def analyze(self):
        """
        Analyze the script for semantic errors.
        Raises:
            SemanticError: If a semantic error is found.
        """
        self.verify_title() # Verify that the first token is a title
        last_token_type = None
        title_count = 0
        line_tokens = {}
        for root in self.root_nodes:

            # Verify that there is only one token per line
            self.verify_no_multiple_tokens_per_line(root=root, line_tokens=line_tokens)

            # Verify that there is only one title in the script
            if root.token_type == 'TITULO':
                title_count = self.verify_single_title(root=root, title_count=title_count)

            # Verify that a transition is not followed by another transition
            elif root.token_type == 'TRANSICION':
                self.verify_no_multiple_transitions(root=root, last_token_type=last_token_type)
                # TODO: Check if a transition is not the last token, there must have a scene after it  
            
            # Verify that acotations are within a dialogue or an action, not as independent tokens
            elif root.token_type == 'ACOTACION':
                self.verify_no_single_acotations(root=root)
            
            # Verify that a dialogue is preceded by a character name
            elif root.token_type == 'DIALOGO':
                self.verify_dialogue_preceded_by_character(root=root, last_token_type=last_token_type)
            
            # Verify that a scene is preceded by a transition or is the first scene
            elif root.token_type == 'ESCENA':
                self.verify_scenes(root=root, last_token_type=last_token_type)
            
            last_token_type = root.token_type

    def verify_title(self):
        """
        Verify that the first token is a title.
        Raises:
            SemanticError: If the first token is not a title.
        """
        if self.root_nodes[0].token_type != 'TITULO':
            raise SemanticError(f"Title must be the first element in the script.")
        
    def verify_single_title(self, root: TokenNode, title_count: int):
        """
        Verify that there is only one title in the script.
        Args:
            title_count (int): The number of titles found in the script.
        Raises:
            SemanticError: If the script contains more than one title.
        """
        title_count += 1
        if title_count != 1:
            raise SemanticError(f"Script must contain exactly one title. Found another title in line {root.line_number}.")
        return title_count
        
    def verify_scenes(self, root: TokenNode, last_token_type: str):
        """
        Verify that a scene is preceded by a transition or is the first scene.
        Args:
            root (TokenNode): The current token node.
            last_token_type (str): The type of the last token.
        Raises:
            SemanticError: If a scene is not preceded by a transition or is not the first scene.
        """
        if root.token_type == 'ESCENA':
            if last_token_type is not None and last_token_type != 'TRANSICION' and last_token_type != 'TITULO':
                raise SemanticError(f"Scene '{root.token_type}' at line {root.line_number} must be preceded by a transition or be the first scene.")

    def verify_no_single_acotations(self, root: TokenNode):
        """
        Verify that acotations are within a dialogue or an action.
        Args:
            root (TokenNode): The current token node.
        Raises:
            SemanticError: If an acotation is not within a dialogue or an action.
        """
        raise SemanticError(f"Acotations must be within a dialogue or an action (line {root.line_number}).")

    def verify_no_multiple_tokens_per_line(self, root: TokenNode, line_tokens: dict[int, list[str]]):
        """
        Verify that there is only one token per line.
        Args:
            root (TokenNode): The current token node.
            line_tokens (dict[int, list[str]]): A dictionary of line numbers and tokens.
        Raises:
            SemanticError: If there are multiple tokens on the same line.
        """
        if root.line_number not in line_tokens:
            line_tokens[root.line_number] = []
        line_tokens[root.line_number].append(root.token_type)

        for line_number, tokens in line_tokens.items():
            if len(tokens) > 1:
                raise SemanticError(f"Multiple tokens found on line {line_number}: {tokens}. Only one token allowed per line unless nested.")
    
    def verify_dialogue_preceded_by_character(self, root: TokenNode, last_token_type: str):
        """
        Verify that a dialogue is preceded by a character name.
        Args:
            root (TokenNode): The current token node.
            last_token_type (str): The type of the last token.
        Raises:
            SemanticError: If a dialogue is not preceded by a character name.
        """
        if root.token_type == 'DIALOGO':
            if last_token_type != 'PERSONAJE':
                raise SemanticError(f"Dialogue '{root.token_type}' at line {root.line_number} must be preceded by a character name.")

    def verify_no_multiple_transitions(self, root: TokenNode, last_token_type: str):
        """
        Verify that there are no multiple transitions in a row.
        Args:
            root (TokenNode): The current token node.
            last_token_type (str): The type of the last token.
        Raises:
            SemanticError: If there are multiple transitions in a row.
        """
        if last_token_type == 'TRANSICION':
            raise SemanticError(f"You cannot have multiple transitions in a row. Found two transitions at line {root.line_number}.")
    
def run_semantic_analyzer(root_nodes, token_list):
    """
    Run the semantic analyzer on the script.
    Args:
        root_nodes (list[TokenNode]): The root nodes of the syntax tree.
        token_list (generator): The token list.
    Returns:
        bool: True if the semantic analysis passed, False otherwise.
    """
    semantic_analyzer = SemanticAnalyzer(root_nodes, token_list)
    try:
        semantic_analyzer.analyze()
        return True, ""
    except SemanticError as e:
        return False, e.args[0]

    
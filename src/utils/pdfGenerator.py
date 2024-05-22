import random
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from typing import Dict, List
from src.utils.syntaxTree import TokenNode


def generate_random_color():
    """
    Generate a random color.
    """
    return colors.Color(random.random(), random.random(), random.random(), alpha=1)


def complex_names(name: str):
    """
    Replace the '@' character with a space in the name of the character.
    """
    if "@" in name:
        return name.replace("@", " ")
    else:
        return name


def assign_colors_to_characters(token_list):
    """
    Assign colors to characters.
    Args:
        tokens: List of tokens.
    Returns:
        Dictionary of characters with their assigned colors.
    """
    characters = {}
    for token in token_list:
        if token[1] == "PERSONAJE":
            character_name = complex_names(token[3].upper())
            if character_name not in characters:
                characters[character_name] = generate_random_color()
    return characters


def get_parent_token_content(
    token: TokenNode,
    custom_styles: Dict[str, ParagraphStyle],
    character_colors: Dict[str, colors.Color],
):
    """
    Get the full text of a parent token.
    Args:
        token: The parent token.
        custom_styles: Dictionary of custom styles.
        character_colors: Dictionary of characters with their assigned colors.
    Returns:
        full_text: The full text of the parent token.
    """
    full_text = ""
    for child in token.children:
        if child.token_type == "PERSONAJE":
            name = complex_names(child.text.upper())
            full_text += f'<font name="{custom_styles[child.token_type].fontName}" size="{custom_styles[child.token_type].fontSize}" color="{character_colors[name]}">{name}</font>'
        elif child.token_type == "ACOTACION":
            full_text += f'<font name="{custom_styles[token.token_type].fontName}" size="{custom_styles[token.token_type].fontSize}">{child.full_text}</font>'
        else:
            full_text += f'<font name="{custom_styles[token.token_type].fontName}" size="{custom_styles[token.token_type].fontSize}">{child.text}</font>'

    return full_text


def generate_pdf(root_tokens: List[TokenNode], full_token_list, output_filename: str):
    """
    Generate a PDF file from the script.
    Args:
        root_tokens: List of root tokens.
        full_token_list: List of all tokens.
        output_filename: Name of the output file.
    """
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=64,
        leftMargin=64,
        topMargin=72,
        bottomMargin=36,
    )
    Story = []

    # Custom styles for screenplay format
    custom_styles = {
        "TITULO": ParagraphStyle(
            name="Title",
            fontSize=18,
            leading=22,
            spaceAfter=14,
            alignment=TA_CENTER,
            fontName="Courier-Bold",
            textColor=colors.black,
        ),
        "ESCENA": ParagraphStyle(
            name="Scene",
            fontSize=12,
            leading=14,
            spaceAfter=10,
            leftIndent=0,
            fontName="Courier",
            textColor=colors.black,
        ),
        "PERSONAJE": ParagraphStyle(
            name="Character",
            fontSize=12,
            leading=14,
            spaceAfter=2,
            leftIndent=0,
            alignment=TA_CENTER,
            fontName="Courier",
        ),
        "DIALOGO": ParagraphStyle(
            name="Dialog",
            fontSize=12,
            leading=14,
            spaceAfter=6,
            leftIndent=0.7 * inch,
            rightIndent=0.7 * inch,
            alignment=TA_CENTER,
            fontName="Courier",
            textColor=colors.black,
        ),
        "ACCION": ParagraphStyle(
            name="Action",
            fontSize=12,
            leading=14,
            spaceAfter=6,
            leftIndent=0,
            fontName="Courier",
            textColor=colors.black,
        ),
        "TRANSICION": ParagraphStyle(
            name="Transition",
            fontSize=12,
            leading=14,
            spaceAfter=6,
            rightIndent=0,
            alignment=TA_RIGHT,
            fontName="Courier",
            textColor=colors.black,
        ),
    }

    character_colors = assign_colors_to_characters(full_token_list)

    for token in root_tokens:
        token_type = token.token_type
        token_content = ""
        if token.children:
            token_content = get_parent_token_content(
                token, custom_styles, character_colors
            )
            p = Paragraph(token_content, custom_styles[token_type])
            Story.append(p)
            Story.append(Spacer(1, 0.2 * inch))

        else:
            token_content = token.text
            if token_type == "TITULO":
                p = Paragraph(token_content, custom_styles["TITULO"])
            elif token_type == "ESCENA":
                p = Paragraph(token_content.upper(), custom_styles["ESCENA"])
            elif token_type == "PERSONAJE":
                character_name = token_content.upper()
                character_style = ParagraphStyle(
                    name=f"Character_{character_name}",
                    parent=custom_styles["PERSONAJE"],
                    textColor=character_colors[character_name],
                )
                p = Paragraph(character_name, character_style)
            elif token_type == "DIALOGO":
                p = Paragraph(token_content, custom_styles["DIALOGO"])
            elif token_type == "ACCION":
                p = Paragraph(token_content, custom_styles["ACCION"])
            elif token_type == "TRANSICION":
                p = Paragraph(token_content.upper(), custom_styles["TRANSICION"])
            else:
                continue

            Story.append(p)
            Story.append(Spacer(1, 0.2 * inch))

    doc.build(Story)
    print(f"PDF file generated: {output_filename}")

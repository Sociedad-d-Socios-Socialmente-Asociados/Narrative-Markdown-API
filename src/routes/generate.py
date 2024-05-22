import os
import random
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from src.utils.pdfGenerator import generate_pdf
from src.utils import schemas
from src.utils.semanticAnalyzer import run_semantic_analyzer
from src.utils import setup
from src.utils.syntaxTree import run_syntax_tree
from src.utils.tokenizer import run_tokenizer

router = APIRouter()


def upload_to_firebase(local_file_path, remote_file_name):
    num_files = sum(1 for _ in setup.STORAGE_CLIENT.list_blobs())
    if num_files >= 5:
        print("Deleting files.")
        for blob in setup.STORAGE_CLIENT.list_blobs():
            blob.delete()
        filename, file_extension = os.path.splitext(remote_file_name)
        blob = setup.STORAGE_CLIENT.blob(filename+str(random.randint(0, 100))+file_extension)
        blob.upload_from_filename(local_file_path)
        blob.make_public()
        return blob.public_url

    # Parse the file name and extension
    filename, file_extension = os.path.splitext(remote_file_name)
    blob = setup.STORAGE_CLIENT.blob(filename+str(random.randint(0, 100))+file_extension)
    blob.upload_from_filename(local_file_path)
    blob.make_public()
    return blob.public_url


@router.post(
    "/text",
    description="Compile the text and turn it into a PDF.",
)
async def generate_from_text(req: schemas.generate_from_text):

    token_list = run_tokenizer(req.text)
    root_nodes, success = run_syntax_tree(token_list)

    if success:
        print("Syntax tree is valid.")
        result, message = run_semantic_analyzer(root_nodes, token_list)
        if result:
            generate_pdf(root_nodes, token_list, r"src\routes\output.pdf")
            url = upload_to_firebase(r"src\routes\output.pdf", "output.pdf")
            return JSONResponse({"url": f"{url}"}, status_code=200)
        else:
            return JSONResponse(
                {"message": f"Semantic analysis failed: {message}"}, status_code=400
            )

    else:
        return JSONResponse({"message": f"SyntaxError:{root_nodes}"}, status_code=400)


@router.post(
    "/file",
    description="Compile the text from a file and turn it into a PDF.",
)
async def generate_from_file(file: UploadFile = File(...)):

    # Extract the file name and extension
    filename, file_extension = os.path.splitext(file.filename)

    if file_extension != ".txt":
        return JSONResponse(
            {"message": "Invalid file extension. Please provide a .txt file."},
            status_code=400,
        )

    # Read the file content as a string
    content = await file.read()
    code = content.decode("utf-8")

    # Remove newline characters from the code
    code = code.replace("\r", "")

    token_list = run_tokenizer(code)
    root_nodes, success = run_syntax_tree(token_list)

    if success:
        print("Syntax tree is valid.")
        result, message = run_semantic_analyzer(root_nodes, token_list)
        if result:
            generate_pdf(root_nodes, token_list, r"src\routes\output.pdf")
            url = upload_to_firebase(r"src\routes\output.pdf", "output.pdf")
            return JSONResponse({"url": f"{url}"}, status_code=200)
        else:
            return JSONResponse(
                {"message": f"Semantic analysis failed: {message}"}, status_code=400
            )

    else:
        return JSONResponse({"message": f"SyntaxError: {root_nodes}"}, status_code=400)

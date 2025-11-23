from pathlib import Path
import os
from langchain.tools import tool
from constants import MAX_CHARS_READ_LIMIT,aiWorkingDirectory

class DirectoryNotFoundError(Exception):
    pass


def validateAndNormalizeAiPath(directoryPath:str)->Path:
    if directoryPath.strip()=="":
        raise TypeError("directoryPath is empty")
    directoryPathObject = Path(directoryPath)

    if directoryPathObject.is_absolute():
        if not directoryPath.startswith(str(aiWorkingDirectory)):
            raise PermissionError(f"{directoryPath}")
            
        
    if aiWorkingDirectory.exists() == False:
        aiWorkingDirectory.mkdir(exist_ok=True)
        return aiWorkingDirectory
    
    if not directoryPathObject.is_absolute():  
        if not directoryPath.startswith("AI"):
            outputPathObject:Path = Path().joinpath("AI",directoryPathObject).resolve()
        else:
            outputPathObject:Path = Path(directoryPath).resolve()
    else:
        outputPathObject:Path = Path(directoryPath)
    
    return outputPathObject
@tool
def createFolder(directoryPath:str)->str:
    """creates only final folder path specified if it doesn't exist"""
    try:
        inputDirectoryPath = validateAndNormalizeAiPath(directoryPath)
    except PermissionError:
        return f"Error:Permission denined"

    Path(inputDirectoryPath).mkdir(exist_ok=True)
    return "Folder created"

@tool
def listDirectoryContent(directoryPath:str)->list[str]|str:
    """Gets a list of files and folders from a specified directory path"""
    
    try:
        inputDirectoryPath = validateAndNormalizeAiPath(directoryPath)
    except PermissionError:
        return f"Error:Permission denined"

    if not inputDirectoryPath.is_dir():
        return f"Error:Directory not found"
    
    return os.listdir(inputDirectoryPath)

@tool
def readFile(filePath:str)->str:
    """reads file contents of text or equivalent files"""
    filePathObject = Path(filePath)
    try:
        validatedFilePath = validateAndNormalizeAiPath(str(filePathObject))
    except PermissionError:
        return f"Error:Permission denined"
    
    if not validatedFilePath.exists():
        return f"Error:Path not found"
    
    with open(validatedFilePath,"r") as file:
        fileContents = file.read()
    if len(fileContents)>MAX_CHARS_READ_LIMIT:
        fileContents=fileContents[:MAX_CHARS_READ_LIMIT] + "... more characters are in this file."
    return fileContents

@tool
def writeFile(filePath:str,content:str)->str:
    """writes content to the specified file path"""
    filePathObject = Path(filePath)
    try:
        validatedFilePath = validateAndNormalizeAiPath(str(filePathObject))
    except PermissionError:
        return f"Error:Permission denined"
<<<<<<< HEAD
    try:
        with open(validatedFilePath,"w",encoding="utf-8") as file:
            file.write(content)
    except FileNotFoundError as e:
            if not validatedFilePath.parent.is_dir():
                return f"Error:Folder not found {validatedFilePath.parent}"
            return f"Error: File not found exception thrown {e}"
        
=======

    with open(validatedFilePath,"w",encoding="utf-8") as file:
        file.write(content)
>>>>>>> 3c1dd19130ae14a18177d80d49e9977de9383a1b
    return "Successfully written to file"

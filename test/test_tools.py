
from tools.fileManager import listDirectoryContent,validateAndNormalizeAiPath,DirectoryNotFoundError

from typing import Type
import pytest
from pathlib import Path

@pytest.mark.parametrize(
    "inputPath,expectedOutput",
    [
    (r"C:\Users\balak\OneDrive\Documents\Code projects\Python\Local-chat-bot","Error:Permission denined"),
    (r"AI\daa",[]),
    (r"daa",[]),
    (r"\tools\AI","Error:Directory not found"),
    (r"AIar", "Error:Directory not found"),
    ]
    )
def test_listDirectoryContent(inputPath:str,expectedOutput:str)->None:
    assert listDirectoryContent(inputPath) == expectedOutput




@pytest.mark.parametrize(
        "inputPath,expectedOutput,exceptionTypeRaised",
        [
            (".",r"C:\Users\balak\OneDrive\Documents\Code projects\Python\Local-chat-bot\AI",None),
            ("AI",r"C:\Users\balak\OneDrive\Documents\Code projects\Python\Local-chat-bot\AI",None),
            (r"AI\daa",r"C:\Users\balak\OneDrive\Documents\Code projects\Python\Local-chat-bot\AI\daa",None),
            (r"C:\Users\balak\OneDrive\Documents\Code projects\Python\Local-chat-bot\AI",r"C:\Users\balak\OneDrive\Documents\Code projects\Python\Local-chat-bot\AI",None),
            (r"C:\Users\balak\OneDrive",'',PermissionError),
            ("",None,TypeError)
        ]
)

def test_validateAndNormalizeAiDirectory(inputPath:str,expectedOutput:str,
                                        exceptionTypeRaised:Type[BaseException]|None)->None:
    if exceptionTypeRaised is None:
        assert validateAndNormalizeAiPath(inputPath)==Path(expectedOutput)
    
    else:
        with pytest.raises(exceptionTypeRaised):
            validateAndNormalizeAiPath(inputPath)

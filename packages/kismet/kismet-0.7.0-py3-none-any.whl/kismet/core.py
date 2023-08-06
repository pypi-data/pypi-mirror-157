from typing import List, Optional
import re

from kismet.parser import KismetParser
from kismet.personality.core import analyze
from kismet.types import Message

# Create parser object.
parser = KismetParser()


def process(string: str):
    return parser.parse(string)

def process_markdown(string: str) -> Optional[str]:
    blocks = code_blocks(string)
    answers = [
        answer
        for answer in [parser.parse(block) for block in blocks]
        if answer is not None
    ]
    return "```\n" + "\n".join(answers) + "\n```" if answers else None

def process_messages(messages: List[Message], client_id: int):
    return analyze(messages, client_id)

def code_blocks(string: str, syntax_type: str = "kismet"):
    blocks = []
    fence = None
    ignore = False
    for line in string.splitlines(keepends=True):
        while line:
            if fence:
                # Look for fence end
                match = re.search(fence, line)
                if match:
                    if not ignore:
                        blocks[-1] += line[: match.start()]
                    fence = None
                    line = line[match.end() :]
                elif not ignore:
                    blocks[-1] += line
                    line = None
                else:
                    line = None
            else:
                # Look for fence start
                match = re.search(r"^`{3,}", line)
                if match:
                    fence = "^" + match.group()
                    syntax = line[match.end() :]
                    if syntax != "\n" and syntax != syntax_type + "\n":
                        ignore = True
                    else:
                        blocks.append("")
                    line = None
                else:
                    match = re.search(r"`+", line)
                    if match:
                        fence = match.group()
                        line = line[match.end() :]
                        blocks.append("")
                    else:
                        line = None
    if fence:
        del blocks[-1]
    return blocks

from datetime import datetime, timedelta
import math
import re
from typing import List

import torch
from torch.distributions.gamma import Gamma
from torch.distributions.categorical import Categorical
import numpy

from kismet.personality.responses import responses as responses_
from kismet.types import Message


class Responder:
    def __init__(self, responses=responses_):
        self.categorical = Categorical(torch.ones(len(responses_)))
        self.responses = responses

    def respond(self, excitement: int):
        if excitement < 1:
            return None

        response = [
            self.responses[self.categorical.sample()]
            for _ in range(excitement)
        ]
        return " ".join(response)


responder_ = Responder()

KISMET_TIMEDELTA = timedelta(seconds=32)
KISMET_PATTERN = re.compile(r"[Kk]+\s*[Ii]+\s*[Ss]+\s*[Mm]+\s*[Ee]+\s*[Tt]+")

def analyze(messages: List[Message]):
    messages.reverse()
    count = len(messages)
    mentioned = None
    attention = 0
    for idx, message in enumerate(messages):
        if is_mentioned(message.content):
            mentioned = idx
        if mentioned is None:
            continue
        delta = datetime.utcnow() - message.created_at
        attention += get_attention(message.content) * 8/(8+delta.seconds) * 1/(idx - mentioned + 1)
    print(attention)
    excitement = round(float(Gamma(1.2, 2 / attention).sample()) if attention > 0 else 0)
    return respond(excitement)

def respond(excitement: int, responder: Responder = responder_):
    return responder.respond(excitement)

def is_mentioned(string: str):
    return KISMET_PATTERN.match(string)

def get_attention(string: str):
    return numpy.arcsinh(
        math.log(len(string.replace(r"\s", "")))
    )
from datetime import timedelta
import math
import re
from typing import List

import torch
from torch.distributions.gamma import Gamma
from torch.distributions.categorical import Categorical
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

def analyze(messages: List[Message], client_id: int):
    if len(messages) == 0:
        return None
    count = len(messages)
    latest = messages[0].created_at
    messages.reverse()
    alerted = 0
    attention = 0
    for idx, message in enumerate(messages):
        is_result = (message.author_id == client_id and message.reply_id)
        is_alerted = is_result or is_mentioned(message.content)
        if is_alerted:
            alerted = idx
        delta = latest - message.created_at
        attention += (
                get_attention(message.content, is_alerted)
                * (0.125 if message.author_id == client_id else 1)
                * (0.25 if is_result else 1)
                * 4/(4+delta.seconds)
                * (1/(1 + math.exp(0.5 * (idx - alerted - 2))))
                * (1/(1 + math.exp(0.5 * (count - idx - 2))))
            )
    excitement = round(
        float(Gamma(
            1 + (2/(1+math.exp(2 * (count - alerted - 1)))),
            1 / (2 * attention)
        ).sample())
        if attention > 0 else 0
    )
    return respond(excitement)

def respond(excitement: int, responder: Responder = responder_):
    return responder.respond(excitement)

def is_mentioned(string: str):
    return KISMET_PATTERN.match(string)

def get_attention(string: str, is_alerted: bool):
    return 1 / (1 + math.exp(-0.125 * (len(string.replace(r"\s", "")) - (2 if is_alerted else 4))))
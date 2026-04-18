"""Structured error helper."""


def json_error(code, message):
    return {"error": message, "code": code}

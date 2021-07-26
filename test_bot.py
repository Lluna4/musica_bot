from bot import on_message
import pytest


@pytest.mark.parametrize(
    "message, expected1, expected2, expected3, expected4", [
        (".p https://youtu.be/dQw4w9WgXcQ", True, False, 1, ["https://youtu.be/dQw4w9WgXcQ"])
    ]
)
def test_con(message):
    assert on_message(message) == expected1, expected2, expected3, expected4


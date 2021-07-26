from botwin import con


def test_con():
    assert con("", True, [1,0], 0, True) == (True, [0], 0, True)
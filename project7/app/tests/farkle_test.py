import farkle
import os
import sys
sys.path.append(os.path.join('..'))


def test_roll_dice():
    roll_1 = farkle.roll_dice(1)
    assert len(roll_1) == 1
    assert roll_1[0] <= 6
    assert roll_1[0] >= 0

    roll_2 = farkle.roll_dice(6)
    assert len(roll_2) == 6
    assert roll_2[0] <= 6
    assert roll_2[0] >= 0
    assert roll_2[1] <= 6
    assert roll_2[2] >= 0


def test_score():
    assert farkle.score([1]) == 100
    assert farkle.score([5]) == 50
    assert farkle.score([5, 5]) == 100
    assert farkle.score([5, 5, 5]) == 500
    assert farkle.score([1, 1, 1]) == 1000
    assert farkle.score([2, 2, 2]) == 200
    assert farkle.score([1, 1, 1, 2, 2, 2]) == 1200
    assert farkle.score([1, 1, 1, 1, 1, 1]) == 3000
    assert farkle.score([5, 5, 5, 5, 5, 5]) == 3000
    assert farkle.score([5, 5, 5, 5, 5]) == 2000
    assert farkle.score([5, 5, 5, 5, 5, 1]) == 2100
    assert farkle.score([2, 2, 2, 2, 1, 1]) == 1200

    assert farkle.score([2]) == 0
    assert farkle.score([2, 3, 4, 6]) == 0
    assert farkle.score([6, 6, 4, 4, 2, 2]) == 0


def test_save_dice():
    assert farkle.save_dice([2], [0]) == False
    assert farkle.save_dice([1], [0]) == True
    assert farkle.save_dice([5], [0]) == True
    assert farkle.save_dice([5, 5, 5, 5, 5, 1], [0, 1, 2, 3, 4, 5]) == True
    assert farkle.save_dice([5, 5, 5, 5, 5, 2], [0, 1, 2, 3, 4, 5]) == False
    assert farkle.save_dice([5, 5, 5, 5, 5, 2], [5]) == False


test_roll_dice()
test_score()
test_save_dice()


import random


def hash_roll(dice):
    """ hash_roll will convert the roll into a hash where the keys are the die
    values and the values are the number of times the die appeared in the roll
    """
    d = {}
    for v in dice:
        if v in d:
            d[v] += 1
        else:
            d[v] = 1
    return d


def roll_dice(number):
    """ roll dice rolls the specified number of dice
    """
    return [random.choice(range(1, 7)) for _ in range(number)]


def save_dice(dice, indices):
    """ save_dice checks to see if the indices will return a valid score
    Guidelines
    ----------
    A player must save dice that will score
    A player cannot save less than 3 2s, 3s, 4s, or 6s
    A player cannot save the same index more than once
    """
    if len(indices) > dice or len(indices) > len(set(indices)):
        return False
    vals = []
    for i in indices:
        if i > len(dice):
            return False
        vals.append(dice[i])
    d = hash_roll(vals)
    for k, v in d.iteritems():
        if k in [2, 3, 4, 6] and v < 3:
            return False
    return True


def score(dice):
    """ score converts the dice into a score
    """
    total = 0
    hr = hash_roll(dice)
    for k, v in hr.iteritems():
        if v > 3:
            total += 1000 * (v-3)
        if v == 3:
            if k == 1:
                total += 1000
            else:
                total += k * 100
        if v < 3 and k == 1:
            total += 100 * v
        if v < 3 and k == 5:
            total += 50 * v
    return total


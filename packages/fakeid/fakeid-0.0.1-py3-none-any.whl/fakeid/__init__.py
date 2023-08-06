import random


def birthday():
    day = str(random.randint(1, 28))
    month = str(random.randint(1, 12))
    year = str(random.randint(1990, 2001))
    dmy = day+"/"+month+"/"+year
    return dmy

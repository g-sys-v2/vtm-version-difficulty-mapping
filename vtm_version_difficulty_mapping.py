"""
Tabulates roll success probabilities for Vampire: The Masquerade old and 5th edition rules.
Maps old roll parameters to 5th edition ones and outputs the probability of success for both.
<<<<<<< HEAD
"""
from sys import argv
from math import factorial as fact

DIE_MAX = 10


def binomial(p, n, x):
    if p == 1:
        return 1
    if x > n:
        return 0
    c_nx = fact(n)/(fact(n-x)*fact(x))
    return c_nx*(p**x)*((1-p)**(n-x))


def p_one_or_more(p, n, s):
    result = 0
    for i in range(s, n+1):
        result += binomial(p, n, i)
        if result >= 1:
            return 1.0
    return result


def format_result(r):
    return round(r*100, 2)


def p_owod(n, s, d):
    if n < s:
        return 0
    return format_result(p_one_or_more(((DIE_MAX-d+1)/DIE_MAX), n, s))


def get_p_dist_owod():
    p_dist = {}
    for n in range(1, 21):
        if n not in p_dist:
            p_dist[n] = {}
        for s in range(1, 11):
            if s not in p_dist[n]:
                p_dist[n][s] = {}
            for d in range(1, 11):
                if d not in p_dist[n][s]:
                    p_dist[n][s][d] = {}
                result = p_owod(n, s, d)
                p_dist[n][s][d] = result
    return p_dist


def p_e5(n, d):
    if n < d:
        return 0
    return format_result(p_one_or_more((1/2), n, d))


def get_p_dist_e5():
    p_dist = {}
    for n in range(1, 21):
        if n not in p_dist:
            p_dist[n] = {}
        for d in range(1, 11):
            if d not in p_dist:
                p_dist[n][d] = {}
            result = p_e5(n,d)
            p_dist[n][d] = result
    return p_dist


def get_p_map(p_dist_owod, p_dist_e5):
    p_map = {}
    for n in p_dist_owod.keys():
        if n not in p_map:
            p_map[n] = {}
        for s in p_dist_owod[n].keys():
            if s not in p_map[n]:
                p_map[n][s] = {}
            for d in p_dist_owod[n][s].keys():
                if d not in p_map[n][s]:
                    p_map[n][s][d] = {}
                mapped_d = 1
                min_diff = abs(p_dist_owod[n][s][d] - p_dist_e5[n][mapped_d])
                for d_e5 in p_dist_e5[n]:
                    diff = abs(p_dist_owod[n][s][d] - p_dist_e5[n][d_e5])
                    if diff < min_diff:
                        min_diff = diff
                        mapped_d = d_e5
                p_map[n][s][d] = mapped_d
    return p_map


p_dist_owod = get_p_dist_owod()
p_dist_e5 = get_p_dist_e5()
p_map = get_p_map(p_dist_owod, p_dist_e5)

help_statement = f"description:\n\tConverts a VTM V20 roll into a 5E roll. Returns required 5E " \
                 f"Difficulty for the given number of dice.\n"\
                 f"usage:\n\tpython vtm_version_difficulty_mapping.py "\
                 f"<number of dice> <successes required> <difficulty>\n"
if len(argv) == 1 or argv[1] == "-h" or argv[1] == "h":
    print(help_statement)
    exit()
try:
    n = int(argv[1])
    s = int(argv[2])
    d = int(argv[3])
    print(
        f"owod\n"
        f"\tparameters:\n"
        f"\t\tdice: {n}\n"
        f"\t\trequired successes: {s}\n"
        f"\t\tdifficulty: {d}\n"
        f"\tsuccess chance: {p_dist_owod[n][s][d]}%\n"
        f"5e\n"
        f"\tdifficulty: {p_map[n][s][d]}\n"
        f"\tsuccess chance: {p_dist_e5[n][p_map[n][s][d]]}%\n"
    )
except (SyntaxError, IndexError):
    print(help_statement)

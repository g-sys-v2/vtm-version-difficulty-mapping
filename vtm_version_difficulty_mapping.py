"""
Vampire: The Masquerade™ Version Difficulty Mapper

Tabulates roll success probabilities for Vampire: The Masquerade old and 5th edition rules.
Maps old roll parameters to 5th edition ones and outputs the probability of success for both.

George T
01/16/20
"""

import csv
from sys import argv
from math import factorial as fact

DIE_MAX = 10


def c(n, x):
    return fact(n)/(fact(n-x)*fact(x))


def binomial(p, n, x):
    if p == 1:
        return 1.0
    if x > n:
        return 0.0
    return c(n, x)*(p**x)*((1-p)**(n-x))


def p_one_or_more(p, n, s):
    result = 0
    for x in range(s, n+1):
        result += binomial(p, n, x)
    return result


def p_crit_fail(n, s, d, x, y):
    if n == x:
        return 1.0
    if x < s:
        return 0.0
    return c(n-x, y)*((1/(d-1))**(y))*((1-(1/(d-1)))**(n-x-y))


def p_v20(n, s, d):
    if n < s:
        return 0
    #return p_one_or_more(((DIE_MAX-d+1)/DIE_MAX), n, s)
    result = 0
    for x in range(s, n+1):
        inter_result = binomial((DIE_MAX-d+1)/DIE_MAX, n, x)
        for y in range(x-s+1, n-x+1):
            if y > n-x:
                break
            inter_result *= 1 - p_crit_fail(n, s, d, x, y)
        result += inter_result
    return result


def p_e5(n, d):
    if n < d:
        return 0
    return p_one_or_more((1/2), n, d)


def get_p_dist_v20():
    p_dist = {}
    for n in range(1, 21):
        if n not in p_dist:
            p_dist[n] = {}
        for s in range(1, 11):
            if s > n:
                break
            if s not in p_dist[n]:
                p_dist[n][s] = {}
            for d in range(2, 11):
                if d not in p_dist[n][s]:
                    p_dist[n][s][d] = {}
                result = p_v20(n, s, d)
                p_dist[n][s][d] = result
    return p_dist


def get_p_dist_e5():
    p_dist = {}
    for n in range(1, 21):
        if n not in p_dist:
            p_dist[n] = {}
        for d in range(1, 11):
            if d > n:
                break
            if d not in p_dist:
                p_dist[n][d] = {}
            result = p_e5(n,d)
            p_dist[n][d] = result
    return p_dist


def get_p_map(p_dist_v20, p_dist_e5):
    p_map = {}
    for n in p_dist_v20.keys():
        if n not in p_map:
            p_map[n] = {}
        for s in p_dist_v20[n].keys():
            if s not in p_map[n]:
                p_map[n][s] = {}
            for d in p_dist_v20[n][s].keys():
                if d not in p_map[n][s]:
                    p_map[n][s][d] = {}
                mapped_d = 1
                min_diff = abs(p_dist_v20[n][s][d] - p_dist_e5[n][mapped_d])
                for d_e5 in p_dist_e5[n]:
                    diff = abs(p_dist_v20[n][s][d] - p_dist_e5[n][d_e5])
                    if diff < min_diff:
                        min_diff = diff
                        mapped_d = d_e5
                p_map[n][s][d] = mapped_d
    return p_map


def format_result(r):
    return round(r*100, 2)


def write_csv_v20(table, filename="v20.csv"):
    with open(filename, "w") as f:
        w = csv.writer(f)
        w.writerow(["dice pool", "successes required", "v20 difficulty", "success probability"])
        for n in table.keys():
            for s in table[n].keys():
                for d in table[n][s].keys():
                    w.writerow([n, s, d, f"{format_result(table[n][s][d])}%"])


def write_csv_e5(table, filename="5e.csv"):
    with open(filename, "w") as f:
        w = csv.writer(f)
        w.writerow(["dice pool", "5e difficulty", "success probability"])
        for n in table.keys():
            for d in table[n].keys():
                w.writerow([n, d, f"{format_result(table[n][d])}%"])


help_statement = f"description:\n\tConverts a VTM V20 roll into a 5E roll. Returns required 5E " \
                 f"Difficulty for the given number of dice.\n"\
                 f"usage:\n\tpython vtm_version_difficulty_mapping.py "\
                 f"<number of dice> <successes required> <difficulty>\n"

if len(argv) == 1 or argv[1] == "-h" or argv[1] == "h":
    print(help_statement)
    exit()

try:
    p_dist_v20 = get_p_dist_v20()
    p_dist_e5 = get_p_dist_e5()
    p_map = get_p_map(p_dist_v20, p_dist_e5)

    if argv[1] == "--csv":
        write_csv_v20(p_dist_v20)
        write_csv_e5(p_dist_e5)
        exit()

    n = int(argv[1])
    s = int(argv[2])
    d = int(argv[3])

    print(
        f"rs\n"
        f"\tparameters:\n"
        f"\t\tdice: {n}\n"
        f"\t\trequired successes: {s}\n"
        f"\t\tdifficulty: {d}\n"
        f"\tsuccess chance: {format_result(p_dist_v20[n][s][d])}%\n"
        f"5e\n"
        f"\tdifficulty: {p_map[n][s][d]}\n"
        f"\tsuccess chance: {format_result(p_dist_e5[n][p_map[n][s][d]])}%\n"
    )
except (SyntaxError, IndexError):
    print(help_statement)

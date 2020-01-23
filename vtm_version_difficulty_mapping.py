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
P_SUCCESS_E5 = 1/2


def c(n, x):
    return fact(n)/(fact(n-x)*fact(x))


def binomial(p, n, x):
    if p == 1:
        return 1.0
    if x > n:
        return 0.0
    return c(n, x)*(p**x)*((1-p)**(n-x))


def p_owod_cancelling_ones(n, s, d, x, y):
    if n == x:
        return 1.0
    if x < s:
        return 0.0
    return c(n-x, y)*((1/(d-1))**(y))*((1-(1/(d-1)))**(n-x-y))


def p_owod_cancelling_ones_cum(n, s, d, x):
    result = 1
    for y in range(x-s+1, n-x+1):
        if y > n - x:
            break
        result *= 1 - p_owod_cancelling_ones(n, s, d, x, y)
    return result


def p_owod(n, s, d):
    if n < s:
        return 0
    result = 0
    for x in range(s, n+1):
        result += binomial((DIE_MAX-d+1)/DIE_MAX, n, x)*p_owod_cancelling_ones_cum(n, s, d, x)
    return result


def p_e5_double_tens(n, d, t, s):
    return c(d, t)*((1/DIE_MAX)**t)*c(d-t, s)*((P_SUCCESS_E5-1/DIE_MAX)**s)*((P_SUCCESS_E5)**(n-t-s))


def p_e5_double_tens_cum(n, d):
    result = 0
    t = 2
    s = d-t-1
    while s >= 0:
        result += p_e5_double_tens(n, d, t, s)
        s -= 1
        if 2*t+s < d:
            t += 2
            s -= 2
    return result


def p_e5(n, d):
    if n < d:
        return 0
    result = 0
    for x in range(d, n+1):
        result += binomial(P_SUCCESS_E5, n, x) + p_e5_double_tens_cum(n, d)
    return result


def get_p_dist_owod():
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
                result = p_owod(n, s, d)
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


def format_result(r):
    return round(r*100, 2)


def write_csv_owod(table, filename="owod.csv"):
    with open(filename, "w") as f:
        w = csv.writer(f)
        w.writerow(["dice pool", "successes required", "owod difficulty", "success probability"])
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


def write_csv_map(table, filename="mapping.csv"):
    with open(filename, "w") as f:
        w = csv.writer(f)
        w.writerow(["dice pool", "successes required", "owod difficulty", "5e difficulty"])
        for n in table.keys():
            for s in table[n].keys():
                for d in table[n][s].keys():
                    w.writerow([n, s, d, table[n][s][d]])


help_statement = f"\n" \
                 f"description:\n" \
                 f"\tConverts a VTM OWOD (V20) roll into a 5E roll.\n" \
                 f"\tReturns required 5E Difficulty for the given number of dice.\n"\
                 f"usage:\n" \
                 f"\tpython vtm_version_difficulty_mapping.py "\
                 f"<number of dice> <successes required> <difficulty>\n" \
                 f"options:\n" \
                 f"\t--csv:\tWrite probability tables in CSV format.\n" \
                 f"\th, -h --help:\tPrint this message.\n"

if len(argv) == 1 or argv[1] in ["h", "-h", "--help"]:
    print(help_statement)
    exit()

try:
    p_dist_owod = get_p_dist_owod()
    p_dist_e5 = get_p_dist_e5()
    p_map = get_p_map(p_dist_owod, p_dist_e5)

    if argv[1] == "--csv":
        write_csv_owod(p_dist_owod)
        write_csv_e5(p_dist_e5)
        write_csv_map(p_map)
        exit()

    n = int(argv[1])
    s = int(argv[2])
    d = int(argv[3])

    print(
        f"\n"
        f"owod\n"
        f"\tdice: {n}\n"
        f"\trequired successes: {s}\n"
        f"\tdifficulty: {d}\n"
        f"\tsuccess chance: {format_result(p_dist_owod[n][s][d])}%\n"
        f"5e\n"
        f"\tdice: {n}\n"
        f"\tdifficulty: {p_map[n][s][d]}\n"
        f"\tsuccess chance: {format_result(p_dist_e5[n][p_map[n][s][d]])}%\n"
    )
except (SyntaxError, IndexError):
    print(help_statement)

# Vampire: The Masquerade™ Roll Version Mapper

![image](https://user-images.githubusercontent.com/59987226/72588032-de65d480-38ab-11ea-9cd6-34b1143f2a49.png)

## Summary

With the release of 5th Edition, Vampire: The Masquerade (VTM) 
introduced an entirely new system to determine the difficulty of 
succeeding on rolls. Unfortunately, this means that not only are 
certain features of the older Old World of Darkness (OWOD) system
(here approximated by the 20th Anniversary Edition) difficult
to transfer to the new ruleset, but entire chronicles that use OWOD
rules are basically unusable for players that wish to use 5E.

This project seeks to amend that by autonomously determining the 
required 5E Difficulty given any OWOD roll (up to a dice pool of 20).
It also calculates the chance of success for each of these rolls for
both the OWOD version and its 5E equivalent, for the players'
reference.

## Description

According to OWOD rules, every roll that a player is asked to make 
follows the following setup: in order to pass a check, a player with
a dice pool of `n` 10-sided die must roll `s` successes with a 
Difficulty `d`, where a die roll is considered a success if it
comes up `d` or higher.

For example, a player may be asked to roll a check for dodging. Due to
the player's physical stats, they have 5 dice to roll for the check.
In order to pass the check, they must roll 3 successes at a Difficulty
of 7. Thus, every die rolled is considered a success only if it comes
up 7 or higher, and 3 or more such results are required for the player
to pass the check.

5th Edition streamlines these requirements and redefines some terms.
A typical 5E roll still has the player rolling `n` dice, but now the
'Difficulty' is the number of successes required (equivalent to `s` in
OWOD rules), and all die results are successful if they come up 6 or 
higher (meaning every die has a 50% chance of being a success).

Despite the similarities in jargon, it is very difficult to directly
map from one formula to the other. If a Storyteller is using an OWOD
chronicle that calls for the aforementioned `(n=5,s=3,d=7)` roll, what
should they use for a 5E equivalent? The default response would either
be to match the difficulty or the required number of successes, but
some statistical testing will soon show that neither one is sufficient,
and that in fact it may not be possible to map the OWOD roll to a 5E
roll with the same probability of success.

The same goes for solving for 5E Difficulty given OWOD parameters 
(since the number of dice `n` is the same in both formulas). The 
probability distribution formulas for each version's chance of success
for a roll make it very difficult to do so without a
lot of approximation. Instead, this program tabulates the probability 
of success for every possible combination of parameters between both
versions for a player dice pool of 1 to 20.

## Implementation

The probability calculations and mapping algorithm are implemented as
follows. Note the combination term:

`C(n, x) = n!/(x! * (n-x)!)`

### OWOD Roll Success Probability

The program calculates the probability of success for every single 
combination of `(n,s,d)` such that `1<n<20`, `1<s<10`, and `1<d<10`.
Results for larger dice pools are omitted because they are unusual
in everyday gameplay. These success probabilites are modeled as a
cumulative binomial distribution where the chance of success on a 
single die is 

`(10-d+1)/10 = (11-d)/10`.


The base OWOD roll success probability for each roll such that the 
number of successes is exactly that which is required is calculated as 
follows:

```
P(owod_base_success) = C(n,s) * ((11-d)/10)**s * (1-(11-d)/10)**(n-s)

where
    n: The number of dice
    s: The required number of successes
    d: The Difficulty as defined above for OWOD
```

In addition to this, OWOD (V20) rules specify that any 1s rolled in
this manner cancel out any success results. To model this, each 
success probability is further augmented by the probability that
none of the failure results are 1s. This itself is a (negative) 
cumulative binomial distribution formulated as follows:

```
P(owod_no_1s) = sum(x-s+1, n-x+1, 1 - P(owod_one_or_more_1s))

where
    P(owod_one_or_more_1s) = C(n-x, y)*((1/(d-1))**(y))*((1-(1/(d-1)))**(n-x-y))
    n: The number of dice
    s: The required number of successes
    d: The Difficulty as defined above for OWOD
    x: The number of successes for this iteration
    y: The number of 1s for this iteration
``` 

This results in a final OWOD roll success probability modeled as the
sum of the probabiblities of getting exactly the required number of 
successes or more and not having those successes negated by 1s:

```
P(owod_success) = sum(x=s, n+1, P(owod_base_success) * P(owod_no_1s))
                = sum(x=s, n+1, (C(n,s) * ((11-d)/10)**s * (1-(11-d)/10)**(n-s))
                  * sum(y=x-s+1, n-x+1, 1 - P(owod_one_or_more_1s)))
                = sum(x=s, n+1, (C(n,s) * ((11-d)/10)**s * (1-(11-d)/10)**(n-s))
                  * sum(y=x-s+1, n-x+1, 
                        1 - C(n-x, y)*((1/(d-1))**(y))*((1-(1/(d-1)))**(n-x-y))))
where
    n: The number of dice
    s: The required number of successes
    d: The Difficulty as defined above for OWOD
```

### 5E Roll Success Probability

The program calculates the probability of success for every single 
combination of `(n,d)` such that `1<n<20` and `1<d<10`.
These success probabilites are modeled as a cumulative binomial 
distribution where the chance of success on a single die is `1/2`.

The base 5E roll success probability for each roll is calculated as 
follows:

```
P(5e_base_success) = C(n,d) * (1/2)**d * (1/2)**(n-d)
 
where
    n: The number of dice
    d: The Difficulty as defined above for 5E
```

In addition to this, 5E rules specify that every pair of 10s rolled
counts as four successes, instead of two. This is modeled by applying
to every base success probability the probability of an alternative
which is a failure unless the doubling 10s rule is applied. For
example, a roll of 7 dice at Difficulty 5 that results in only 3 
successes is a base failure. However, if 2 of those 3 dice are 10s,
then the final result is actually 5 successes and the roll is an
overall success.

The logic whereby this term is derived is implemented as a deterministic
calculation based on finding every combination wherein the 
number of total successes is less than the Difficulty (regardless of
the number of dice being rolled), but one or more pair of successes
are 10s. In computational terms, the algorithm starts with the 
probability that the roll is 1 die short of an overall success 
(Difficulty - 1), that at least one pair of successes are 10s, and
that the rest of the dice are all failures. It then adds the probability
that there are (Difficulty - 2) successes, and so on.
If necessary, the algorithm will continue this calculation with an
additional pair of 10s, and will keep doing so until no further
successful rolls matching the aforementioned conditions are possible.

Note that this approach also normalizes every pair of duplicate rolls 
where the overall number of successes is equal but the number of 10s
is not. This is necessitated by the fact that the probability of a non-10 
success is calculated as the probability of a general success, which
is possibly a 10. The reason for this implementation is that it is
more efficient than simply calculating every possible combination of
successes with every possible number of pairs of 10s.

The additional probability of an overall success with one or more
pairs of 10s that would otherwise be a failure is calculated as follows:

```
P(5e_failure_but_for_10s) = sum((t=2, s=d-t-1), (d/2, 0),
                                 C(d, t) * ((1/DIE_MAX)**t) 
                                 * C(d-t, s) * ((P_SUCCESS_E5-1/DIE_MAX)**s) 
                                 * ((P_SUCCESS_E5)**(n-t-s)))
where
    n: The number of dice
    d: The Difficulty as defined above for 5E
    t: The number of 10s
    s: The number of other successes rolled (possibly also 10s)
```

Thus the final success probability is:

```
P(5e_success) = sum(d, n+1, P(5e_base_success) + P(5e_failure_but_for_10s))
              = sum(d, n+1, C(n,d) * (1/2)**d * (1/2)**(n-d)
                            + sum((t=2, s=d-t-1), (d/2, 0),
                                  C(d, t) * ((1/DIE_MAX)**t) 
                                  * C(d-t, s) * ((P_SUCCESS_E5-1/DIE_MAX)**s) 
                                  * ((P_SUCCESS_E5)**(n-t-s))))
```

### Version Mapping

Once these probabilities are tabulated, the program attempts to map
every single entry in the OWOD probability table to an entry in the
5E table according to the number of dice being rolled.

A Storyteller attempting to use an OWOD chronicle or other 
feature using 5E rules will want to take a suggested OWOD roll and
translate it into 5E terms. Thus, the Storyteller only needs to 
derive the 5E Difficulty, since the number of dice being rolled is 
the same. In order to simulate this, the program will take an entry 
in the OWOD table, find an entry in the 5E table with the same 
number of dice, and attempt to find a 5E Difficulty rating in the 
5E set that results in a roll success probability that is as close
as possible to that of the OWOD roll.

Note: it is not always possible to map rolls such that the chance
of success for the 5E roll is the same as for the OWOD roll. In these
cases, the closest match is chosen.

## Requirements

This script requires only a vanilla install of Python.

## Install

```
git clone https://github.com/g-sys-v2/vtm-version-difficulty-mapping.git
```

## Run

`python vtm_version_difficulty_mapping.py <n> <s> <d>`

```
where
    n: Number of dice being rolled in the OWOD roll
    s: Number of successes required in the OWOD roll
    d: OWOD Difficulty rating for the OWOD roll
```

The program will return the input parameters as well as the 
probability of success for the OWOD roll using them, in addition to
the corresponding 5E Difficulty and the associated probability of 
success.

### Example

`>python vtm_version_difficulty_mapping.py 5 3 7`

result:

```
v20
	parameters:
		dice: 5
		required successes: 3
		difficulty: 7
	success chance: 31.74%
5e
	difficulty: 4
	success chance: 18.75%
```




































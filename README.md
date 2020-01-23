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

### OWOD Roll Success Probability

The program calculates the probability of success for every single 
combination of `(n,s,d)` such that `1<n<20`, `1<s<10`, and `1<d<10`.
Results for larger dice pools are omitted because they are unusual
in everyday gameplay. These success probabilites are modeled as a
cumulative binomial distribution where the chance of success on a 
single die is 

`(10-d+1)/10 = (11-d)/10`.


The OWOD roll success probability for each roll is calculated as 
follows:

```
P(s_owod) = C(n,s) * ((11-d)/10)**s * (1-(11-d)/10)**(n-s)
 
where
    P(s_owod): The probability of passing a roll check
    n: The number of dice
    s: The required number of successes
    d: The Difficulty as defined above for OWOD
    C(n,s) = n!/(s! * (n-s)!)
```

### 5E Roll Success Probability

The program calculates the probability of success for every single 
combination of `(n,d)` such that `1<n<20` and `1<d<10`.
These success probabilites are modeled as a cumulative binomial 
distribution where the chance of success on a single die is `1/2`.

The 5E roll success probability for each roll is calculated as 
follows:

```
P(s_5e) = C(n,d) * (1/2)**d * (1/2)**(n-d)
 
where
    P(s_5e): The probability of passing a roll check
    n: The number of dice
    d: The Difficulty as defined above for 5E
    C(n,d) = n!/(d! * (n-d)!)
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




































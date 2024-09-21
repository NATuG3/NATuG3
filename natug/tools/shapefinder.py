from functools import cache

from natug.structures.profiles import NucleicAcidProfile

C = 8  # number of domains
R = 1  # symmetry factor
nucleic_acid_profile = NucleicAcidProfile(
    D=2.2, H=3.549, g=134.8, T=2, B=21, Z_c=0.17, Z_mate=0.094
)


class Combo(tuple):
    """A combination of numbers that add up to a target number."""

    def __eq__(self, other):
        return sorted(self) == sorted(other)

    def __hash__(self):
        return hash(tuple(sorted(tuple(self))))


def find_combos(n, c):
    """Find all the ways to combine c numbers to add up to n."""
    combinations = set()

    @cache
    def new_options(current_combo):
        current_combo = list(current_combo)

        options = []
        for i in range(c):
            new_combo = list(current_combo)

            if new_combo[i] - 1 < 0:
                continue

            new_combo[i] -= 1
            for ii in range(c):
                rerun_on_combo = new_combo.copy()
                rerun_on_combo[ii] += 1
                options.append(rerun_on_combo)

        return options

    def combo_finder():
        base = tuple([n] + [0] * (c - 1))  # [1, 0, 0, ...0] where length is c

        options = new_options(base)
        for option in options:
            if 0 not in option:
                combinations.add(tuple(option))

        counter = 0

        def searcher(options, tick):
            nonlocal counter

            counter += 1
            if counter % 10000000 == 0:
                print(counter, tick, len(combinations), combinations)

            if tick == 0:
                return
            else:
                for option in options:
                    option = tuple(option)
                    if 0 not in option:
                        combinations.add(option)
                    searcher(new_options(option), tick - 1)

        searcher(options, n)  # should be n

    combo_finder()

    return combinations


def shapefind():
    target_M_over_R = (nucleic_acid_profile.B * (C - 2)) // (2 * R)

    assert closes([4, 13, 4, 14] * 3, nucleic_acid_profile)

    matches = []
    for combo in find_combos(target_M_over_R, C):
        if closes(combo, nucleic_acid_profile):
            matches.append(combo)

    print(matches)


shapefind()

#!/usr/bin/env python3
"""Exact D2 arithmetic fixtures, not a universal gameplay resolver or engine test.

Selected channel order, rounding, time schedule and ideal contact assumptions are
part of these illustrative fixtures. A game must choose its own policy and share
matching golden vectors with its actual runtime implementation.
"""
from fractions import Fraction as F
import argparse
import json
from pathlib import Path


def round_even(value):
    q, r = divmod(value.numerator, value.denominator)
    twice = 2 * r
    return q + (twice > value.denominator or (twice == value.denominator and q % 2))


def channel_hit():
    raw_physical = (F(100) + 20) * F(5, 4) * F(11, 10) * F(3, 2)
    armor = max(F(0), F(100) * F(4, 5) - 10)
    physical = max(F(0), raw_physical * 100 / (100 + armor) - 20)
    fire = F(40) * F(5, 4) * (1 - (F(1, 4) - F(1, 10)))
    channels = [round_even(physical), round_even(fire)]
    barrier = 30
    absorbed = min(barrier, channels[0]); incoming = sum(channels) - absorbed
    return {'physical_before_round': str(physical), 'fire_before_round': str(fire),
            'rounded_channels': channels, 'barrier_absorbed': absorbed,
            'incoming_hp': incoming, 'actual_hp_loss': min(100, incoming),
            'overkill': max(0, incoming - 100), 'hp_after': max(0, 100 - incoming)}


def periodic_damage():
    hp, barrier, stagger = F(10), F(3, 2), 0
    rows = []
    for tick in range(1, 9):
        resistance = F(1, 4) if tick <= 4 else F(1, 2)
        amount = F(6) * F(1, 4) * (1 - resistance)
        blocked = min(barrier, amount); barrier -= blocked
        actual_loss = min(hp, amount - blocked); hp -= actual_loss
        if actual_loss > 0:
            stagger += 2
        rows.append({'tick': tick, 'at_seconds': str(F(tick, 4)),
                     'damage': str(amount), 'hp_loss': str(actual_loss),
                     'hp_after': str(hp), 'barrier_after': str(barrier)})
    return {'hp_after': str(hp), 'barrier_after': str(barrier), 'stagger': stagger,
            'ticks': rows, 'resume_after_tick4_next': 5}


def ttk_two_successes():
    # Independent p=1/2 trials, first trial at t=1. Threshold needs 2 successes.
    cdf = lambda n: F(0) if n < 2 else 1 - F(n + 1, 2 ** n)
    def quantile(p):
        n = 2
        while cdf(n) < p:
            n += 1
        return n
    return {'guaranteed_ttk_seconds': 3, 'random_mean_seconds': 4,
            'random_median_seconds': quantile(F(1, 2)),
            'random_p95_seconds': quantile(F(95, 100)),
            'cdf7': str(cdf(7)), 'cdf8': str(cdf(8))}


def ideal_contact():
    # Single 2D frictionless normal contact, wall static. Not damage conversion.
    inverse_mass = F(1, 800)
    central_effective_mass = 1 / inverse_mass
    offset_effective_mass = 1 / (inverse_mass + F(1, 2) ** 2 / 200)
    speed, restitution = F(5), F(1, 5)
    return {'central_effective_mass_kg': str(central_effective_mass),
            'central_impulse_Ns': str((1 + restitution) * central_effective_mass * speed),
            'normal_energy_before_J': str(F(1, 2) * 800 * speed ** 2),
            'normal_energy_loss_J': str(F(1, 2) * 800 * speed ** 2 * (1 - restitution ** 2)),
            'offset_effective_mass_kg': str(offset_effective_mass),
            'offset_impulse_Ns': str((1 + restitution) * offset_effective_mass * speed)}


def verify(path):
    expected = json.loads(Path(path).read_text(encoding='utf-8'))
    actual = {'channel_hit': channel_hit(), 'periodic_damage': periodic_damage(),
              'ttk_two_successes': ttk_two_successes(), 'ideal_contact': ideal_contact()}
    errors = [name + ': golden output mismatch' for name, result in actual.items()
              if result != expected.get('cases', {}).get(name)]
    if expected.get('scope') != 'illustrative_D2_arithmetic_not_game_or_engine_proof':
        errors.append('missing explicit fixture scope')
    return {'valid': not errors, 'errors': errors, 'cases_checked': len(actual),
            'scope': 'exact arithmetic of chosen fixture assumptions only',
            'quality_certified': False, 'runtime_verified': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fixture', type=Path)
    a = p.parse_args()
    result = verify(a.fixture)
    print(json.dumps(result, indent=2))
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

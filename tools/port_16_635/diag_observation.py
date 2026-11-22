"""Port diagnostic: run the first ~40 s of a native match with WAIT actions and print
per-owner elixir / hand / cycle as the Python environment sees them."""
from dataclasses import replace
import json

from native_runner.battle_env import BattleEnvV1
from native_runner.contracts import ActionV1
from native_runner.cr_native_env import DEFAULT_HOST, DEFAULT_PORT, NativeClashEnv
from native_runner.match_factory import MatchConfig
from native_runner.rich_telemetry_adapter import RuntimeEffectCatalog
from native_runner.training.v4.expert import POLICY_DECISION_TICKS
from native_runner.training.v4.factory import production_semantic_bundle

bundle = production_semantic_bundle()
native = NativeClashEnv(DEFAULT_HOST, DEFAULT_PORT, timeout=30.0)
native.public_card_play_events_from_combat_ring = True
env = BattleEnvV1(native=native, card_catalog=bundle.native_card_catalog,
                  semantic_subset_contract=bundle.semantic_subset_contract,
                  effect_catalog=RuntimeEffectCatalog.from_catalog(bundle.native_effect_catalog))
obs, _ = env.reset(match_config=MatchConfig(), options={"render_mode": "headless", "decision_ticks": POLICY_DECISION_TICKS,
                                                         "event_driven_decisions": False,
                                                         "allow_initial_remaining_runtime_rejections": True})
for step in range(3):
    o = obs[step % 2]
    if True:
        for p in o.players:
            fields = {k: getattr(p, k) for k in ('owner', 'elixir_exact', 'elixir') if hasattr(p, k)}
            hand = getattr(p, 'hand', None)
            print(o.tick, fields, 'hand=', [(c.to_dict() if hasattr(c, 'to_dict') else c) for c in (hand or ())][:2],
                  'next=', getattr(p, 'next_card', None))
    commands = {owner: (ActionV1.wait(owner, ticks=POLICY_DECISION_TICKS),) for owner in (0, 1)}
    obs, *_ = env.step(commands, record_trace=False)
o = obs[0]; d = o.to_dict() if hasattr(o, 'to_dict') else {}
print('obs keys:', sorted(d)[:60])
pl = [p for p in d.get('players', [])]
print('player0:', json.dumps(pl[0], default=str)[:1500] if pl else None)
for k in ('legal_actions', 'action_mask', 'hand_cards', 'cards'):
    if k in d: print(k, json.dumps(d[k], default=str)[:1500])

print('towers:', json.dumps(d.get('towers'), default=str)[:1400])
print('time/phase:', json.dumps(d.get('time'), default=str)[:400], json.dumps(d.get('phase'), default=str)[:300])
print('entities:', len(d.get('entities') or []))

for tw in d.get('towers') or []: print('tower', tw['owner'], tw['tower_kind'], tw['position'], tw['hitpoints'], tw['max_hitpoints'], 'troop', tw.get('tower_troop_id'), 'active', tw['active'])

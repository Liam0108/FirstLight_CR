"""Port diagnostic: tensorize live observations with validation and print per-field ranges."""
import dataclasses, sys
import torch
from native_runner.battle_env import BattleEnvV1
from native_runner.contracts import ActionV1
from native_runner.cr_native_env import DEFAULT_HOST, DEFAULT_PORT, NativeClashEnv
from native_runner.match_factory import MatchConfig
from native_runner.rich_telemetry_adapter import RuntimeEffectCatalog
from native_runner.training.v4.expert import POLICY_DECISION_TICKS
from native_runner.training.v4.factory import production_semantic_bundle
from native_runner.training.v4.policy_session import build_policy_session_v4, load_policy_v4

policy = load_policy_v4(r'checkpoints\General\checkpoint-step-00000460.pt', device='cpu')
bundle = production_semantic_bundle()
native = NativeClashEnv(DEFAULT_HOST, DEFAULT_PORT, timeout=30.0)
native.public_card_play_events_from_combat_ring = True
env = BattleEnvV1(native=native, card_catalog=bundle.native_card_catalog,
                  semantic_subset_contract=bundle.semantic_subset_contract,
                  effect_catalog=RuntimeEffectCatalog.from_catalog(bundle.native_effect_catalog))
obs, _ = env.reset(match_config=MatchConfig(level_cap=11, minimum_card_level=11, king_tower_level=11),
                   options={"render_mode": "headless", "decision_ticks": POLICY_DECISION_TICKS,
                            "event_driven_decisions": False, "allow_initial_remaining_runtime_rejections": True})
init = {o: next(p.elixir_exact for p in ob.players if p.owner == o) for o, ob in obs.items()}
s = build_policy_session_v4(env, policy.model, actor_owner=0, device=torch.device('cpu'), sample=False)
s.start_episode(obs[0], initial_elixir=init)
for _ in range(30):
    obs, *_ = env.step({o: (ActionV1.wait(o, ticks=POLICY_DECISION_TICKS),) for o in (0, 1)}, record_trace=False)
    s.tensorizer.tensorize(obs[0], validate=False)
batch = s.tensorizer.tensorize(obs[0], validate=True)
def walk(prefix, value):
    if isinstance(value, torch.Tensor):
        if value.numel() == 0: print(f'{prefix:60} empty {tuple(value.shape)}'); return
        v = value.float()
        bad = int(torch.isnan(v).sum() + torch.isinf(v).sum())
        print(f'{prefix:60} {str(tuple(value.shape)):22} min={v.min().item():.4g} max={v.max().item():.4g} mean={v.mean().item():.4g}' + (f' NONFINITE={bad}' if bad else ''))
    elif dataclasses.is_dataclass(value):
        for f in dataclasses.fields(value): walk(f'{prefix}.{f.name}', getattr(value, f.name))
walk('batch', batch)

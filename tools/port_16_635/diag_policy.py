"""Port diagnostic: run a short policy-vs-policy segment and report, per decision, how many
deploy candidates are legal and what the policy chose."""
import collections, sys
import torch
from native_runner.battle_env import BattleEnvV1
from native_runner.contracts import ActionKind, ActionV1
from native_runner.cr_native_env import DEFAULT_HOST, DEFAULT_PORT, NativeClashEnv
from native_runner.match_factory import MatchConfig
from native_runner.rich_telemetry_adapter import RuntimeEffectCatalog
from native_runner.training.v4.expert import FIRST_POLICY_DECISION_TICK, POLICY_DECISION_TICKS
from native_runner.training.v4.factory import production_semantic_bundle
from native_runner.training.v4.policy_session import build_policy_session_v4, load_policy_v4
from native_runner.training.v4.tensors import CANDIDATE_DEPLOY
from native_runner.training.v4.decoding import ShadowCandidateLegality

ckpt = sys.argv[1] if len(sys.argv) > 1 else r'checkpoints\General\checkpoint-step-00000460.pt'
policy = load_policy_v4(ckpt, device='cpu')
bundle = production_semantic_bundle()
native = NativeClashEnv(DEFAULT_HOST, DEFAULT_PORT, timeout=30.0)
native.public_card_play_events_from_combat_ring = True
env = BattleEnvV1(native=native, card_catalog=bundle.native_card_catalog,
                  semantic_subset_contract=bundle.semantic_subset_contract,
                  effect_catalog=RuntimeEffectCatalog.from_catalog(bundle.native_effect_catalog))
match = MatchConfig(level_cap=11, minimum_card_level=11, king_tower_level=11)
obs, _ = env.reset(match_config=match, options={"render_mode": "headless", "decision_ticks": POLICY_DECISION_TICKS,
                                                 "event_driven_decisions": False,
                                                 "allow_initial_remaining_runtime_rejections": True})
init = {o: next(p.elixir_exact for p in ob.players if p.owner == o) for o, ob in obs.items()}
sessions = [build_policy_session_v4(env, policy.model, actor_owner=o, device=torch.device('cpu'), sample=False) for o in (0, 1)]
for o, s in enumerate(sessions): s.start_episode(obs[o], initial_elixir=init)
captured = {}
for o, s in enumerate(sessions):
    orig = s.tensorizer.tensorize
    def wrap(observation, validate=True, _orig=orig, _o=o):
        b = _orig(observation, validate=validate); captured[_o] = b; return b
    s.tensorizer.tensorize = wrap
stats = collections.Counter()
for step in range(160):
    cmds = {}
    for o, s in enumerate(sessions):
        ob = obs[o]
        chosen = ()
        if ob.tick >= FIRST_POLICY_DECISION_TICK:
            chosen = s.decide(ob).decoded.actions
            b = captured[o]
            deploy = b.candidates.variant == CANDIDATE_DEPLOY
            legal = ShadowCandidateLegality(b.candidates, s.tensorizer.config).candidate_mask()
            n_legal = int((legal & deploy).sum().item()); n_dep = int((deploy & b.candidates.mask).sum().item())
            kinds = [a.kind.name for a in chosen]
            stats[(o, 'decisions')] += 1; stats[(o, 'legal>0')] += n_legal > 0
            stats[(o, 'played')] += any(a.kind != ActionKind.WAIT for a in chosen)
            if step % 20 == 0:
                me = next(p for p in ob.players if p.owner == o)
                print(f'tick={ob.tick} owner={o} elixir={me.elixir_exact} deploy_masked={n_dep} deploy_legal={n_legal} chose={kinds}')
        else:
            s.tensorizer.tensorize(ob, validate=False)
        cmds[o] = tuple(chosen) or (ActionV1.wait(o, ticks=POLICY_DECISION_TICKS),)
    obs, *_ = env.step(cmds, record_trace=False)
print(dict(stats))

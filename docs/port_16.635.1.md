# Port: Null's Royale 15.535.13 → 16.635.1

This branch (`port/nulls-16.635.1`) runs FirstLight CR on **Null's Royale 16.635.1
(arm64-v8a), content update 16.635.93**. The shipped checkpoints and card/model
catalogs are unchanged (they stay bound to the 15.535.86 card contract).

## Engine identity

| | 15.535.13 | 16.635.1 |
| --- | --- | --- |
| APK SHA-256 | `685c115e…` | `996ce53f61905e931ddbf01539987f7a2b27505b55742e96ff185b597992d6f7` |
| libg.so SHA-256 | `110aa2b5…` | `0b580222e5a3502cf153bb5e6297ec32d2b154b605b777c74873dd75722e4eaa` |
| libg build id | `90e6f351…` | `179ac4bd38c205bc5041d372a79f1c2f929b1c30` |
| content | 15.535.86 | 16.635.93 (`fingerprint.json` `553c8f15…`) |

`native_runner/supported_engine.json` and `native_runner/runtime_update_pins.json`
carry the live identity; `ruleset.live_source_files()` overlays them on the
(unchanged, SHA-pinned) competitive manifest.

## What changed in the game binary and how the probe follows it

- ~150 code / vtable / global addresses relocated (function matching by strings,
  normalized body hash, call graph and vtable slots, then manual review). All 56
  hook prologues / call-site fingerprints are regenerated and verified against
  the new libg (`tools/port_16_635/verify_fingerprints.py`).
- Struct fields re-derived from CSV loader data flow (column name → offset),
  per-class aligned accesses and live memory dumps. Notable moves: SpellData
  +0x38 from 0x208, AreaEffectObjectData (LifeDuration/Radius/…), ProjectileData
  DragBackSpeed, GameApp pending event +8, GameState command context 0x210,
  content-ready flag 0x720, LogicPlayer hand 0x210 / cycle 0x220,
  CaptureCharacterRuntime vectors rotated, CharacterAbilityData MaxCharges/Cooldown.
- Logic command type ids were renumbered: deploy 86 → 153, champion ability 2 → 189.
- ABI changes: CombatDamage now takes `(component, DamageInfo*)`; ConsumeCard gained a
  7th argument; WarpPositionCommit reads x3; the action dispatcher split into
  three entry points (all hooked).
- No longer present (edges disabled with never-matching sentinels): the SpawnAttach
  helper (inlined) and the effect-heal caller return (now a tail call).
- The offline "连接错误" popup is suppressed from cold boot (16.635 enqueues it
  before a control session exists).
- Visible (native-render) matches: the ReplayManager controller slot moved
  0x20 → 0x28, the ReplayBattleController active lifecycle state is 9 (was 8),
  and the ActionSpawnToLocation mode-1 caller now keeps the request *base* at
  sp+0x78 (the probe re-adds +0x48).
- The console's AI-vs-AI duel uses sampled decoding by default (same as Human vs
  AI); `offline_duel --deterministic` restores argmax decoding.
- AI-vs-AI applies the historical opening protocol automatically: a side that has
  not played by tick 300 (15 s) gets one forced first action
  (`--opening-fallback-tick`, `--no-opening-fallback`). Without it the shipped
  policies can sit at full elixir until someone commits.
- Human-vs-AI (`offline_agent`) gets the same opening protocol, and both modes add a
  stall guard: a model that has sat at full elixir for 100 ticks (5 s) is forced to
  play (`--stall-ticks`, `offline_agent --no-forced-plays`, `offline_duel --no-stall-guard`).
- After the final result the native scene keeps its last frame (no results screen
  in offline mode); the console reports "对局已结束".

## Evolutions added by 16.635

Of the 66 new `_EV1` rows only **ElectroGiant_EV1 (26000085)** is live (the rest are
`NotInUse`). It is supported at runtime (`battle_env.RUNTIME_ONLY_EVOLUTIONS`): a
match may enable it with form-availability bit 1, the engine runs the real
evolution, and the frozen checkpoints observe/play the card as its base form.
Teaching a policy the evolution itself requires retraining with an updated catalog.

## Running

1. Dedicated MuMu Android 12 instance with root (this machine: index 1,
   `127.0.0.1:16416`), stock 16.635.1 installed and updated once.
2. `./check_original_game.ps1`, `./build_offline_engine.ps1`, `./install_offline_engine.ps1`
   (or `tools/port_16_635/rebuild_and_install.ps1`).
3. Level-11 match config: `tools/port_16_635/match_level11.json`; with ElectroGiant
   evolution: `tools/port_16_635/match_electrogiant_evo.json`.
4. Use `--sample` with the evaluator: with deterministic decoding the shipped policies
   rarely exceed 50 % act probability per 5-tick decision and mostly wait.

## Verified

- Full sampled level-11 game, General vs General: 45 / 44 plays, 0 rejected actions,
  native final result at tick 6139.
- Full sampled level-11 game with ElectroGiant evolution enabled on both sides
  (`match_electrogiant_evo.json`): evolved ElectroGiant units spawned and were
  encoded as the base form; 43 / 43 plays, 0 rejected actions, final result at tick 6115.
- Console AI-vs-AI visible match in the MuMu window (General vs General, level 11):
  full 3-minute match, native final result at tick 3603, 22 / 23 plays.
- Deterministic games complete without crashes (few plays, see above).

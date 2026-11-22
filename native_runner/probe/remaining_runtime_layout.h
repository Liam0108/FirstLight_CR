#pragma once

#include <cstddef>
#include <cstdint>
#include <limits>

// Exact-build layout and call-site contract for runtime mechanics which are
// not snapshots of HP/position/effects.  These constants are valid only for
// Null's Royale 15.535.13 with the SHA-256/build-id below.
namespace cr_remaining_runtime {

inline constexpr char kSchema[] = "native-remaining-runtime.v1";
inline constexpr char kExactLibgSha256[] = "0b580222e5a3502cf153bb5e6297ec32d2b154b605b777c74873dd75722e4eaa";
inline constexpr char kExactLibgBuildId[] = "179ac4bd38c205bc5041d372a79f1c2f929b1c30";

inline constexpr std::int32_t kResourceFixedPointScale = 10000;
inline constexpr std::size_t kLogicDataGlobalIdOffset = 0x40;

// Common LogicGameObject / LogicCharacter layout.
inline constexpr std::size_t kObjectNativeIdOffset = 0x08;
inline constexpr std::size_t kObjectDataOffset = 0x48;
inline constexpr std::size_t kCharacterSpawnUntargetableOffset = 0x174;

// LogicCharacterData resource/lifetime/visibility fields.
inline constexpr std::size_t kManaGenerationEnabledOffset = 0x3a4;
inline constexpr std::size_t kSpawnAttachOffset = 0x3a5;
inline constexpr std::size_t kAttachedCharacterDataOffset = 0x2f8;
inline constexpr std::size_t kManaGenerateLimitOffset = 0x3ac;
inline constexpr std::size_t kManaCollectAmountOffset = 0x3b0;
inline constexpr std::size_t kManaGenerateTimeMsOffset = 0x3b4;
inline constexpr std::size_t kManaOnDeathOffset = 0x3b8;
inline constexpr std::size_t kManaOnDeathForOpponentOffset = 0x3bc;
inline constexpr std::size_t kAllowAreaDamageWhenInvisibleOffset = 0x768;
inline constexpr std::size_t kUntargetableWhenSpawnedOffset = 0x76a;

// The resource object stores elixir in 1/10000 units.
inline constexpr std::size_t kResourceFixedValueOffset = 0x2f8;
inline constexpr std::uintptr_t kResourceWholeDeltaOffset = 0x01098b8c;
inline constexpr std::uintptr_t kResourceFixedDeltaOffset = 0x01098510;
inline constexpr std::uintptr_t kPeriodicResourceCallOffset = 0x010775dc;
inline constexpr std::uintptr_t kPeriodicResourceReturnOffset = 0x010775e0;
inline constexpr std::uintptr_t kDeathOwnerResourceCallOffset = 0x010c1278;
inline constexpr std::uintptr_t kDeathOwnerResourceReturnOffset = 0x010c127c;
inline constexpr std::uintptr_t kDeathOpponentResourceCallOffset = 0x010c1394;
inline constexpr std::uintptr_t kDeathOpponentResourceReturnOffset = 0x010c1398;

inline constexpr std::uint8_t kResourceWholeDeltaPrologue[16] = {
    0xfd, 0x7b, 0xbd, 0xa9, 0xf6, 0x57, 0x01, 0xa9, 0xf4, 0x4f, 0x02, 0xa9, 0xfd, 0x03, 0x00, 0x91,
};
inline constexpr std::uint8_t kResourceFixedDeltaPrologue[16] = {
    0xfd, 0x7b, 0xbd, 0xa9, 0xf5, 0x0b, 0x00, 0xf9, 0xf4, 0x4f, 0x02, 0xa9, 0xfd, 0x03, 0x00, 0x91,
};
inline constexpr std::uint8_t kPeriodicResourceCallFingerprint[16] = {
    0x6c, 0x85, 0x00, 0x94, 0xe0, 0x03, 0x13, 0xaa, 0x68, 0x4d, 0x00, 0x94, 0x28, 0x6d, 0xf6, 0x97,
};
inline constexpr std::uint8_t kDeathOwnerResourceCallFingerprint[16] = {
    0x45, 0x5e, 0xff, 0x97, 0xe0, 0x03, 0x16, 0xaa, 0x02, 0x46, 0xf5, 0x97, 0xb8, 0x83, 0x1e, 0xf8,
};
inline constexpr std::uint8_t kDeathOpponentResourceCallFingerprint[16] = {
    0x5f, 0x5c, 0xff, 0x97, 0xe0, 0x03, 0x16, 0xaa, 0xbb, 0x45, 0xf5, 0x97, 0xf9, 0x03, 0x00, 0xaa,
};

enum class ResourceDeltaCause : std::uint8_t {
  None = 0,
  Periodic = 1,
  DeathOwner = 2,
  DeathOpponent = 3,
};

constexpr ResourceDeltaCause classify_resource_delta(std::uintptr_t hook_offset, std::uintptr_t caller_return_offset) {
  if (hook_offset == kResourceWholeDeltaOffset && caller_return_offset == kPeriodicResourceReturnOffset) {
    return ResourceDeltaCause::Periodic;
  }
  if (hook_offset == kResourceWholeDeltaOffset && caller_return_offset == kDeathOwnerResourceReturnOffset) {
    return ResourceDeltaCause::DeathOwner;
  }
  if (hook_offset == kResourceFixedDeltaOffset && caller_return_offset == kDeathOpponentResourceReturnOffset) {
    return ResourceDeltaCause::DeathOpponent;
  }
  return ResourceDeltaCause::None;
}

constexpr std::int64_t requested_resource_delta_fixed(ResourceDeltaCause cause, std::int32_t amount_argument) {
  if (amount_argument < 0 || cause == ResourceDeltaCause::None) {
    return -1;
  }
  if (cause == ResourceDeltaCause::DeathOpponent) {
    return amount_argument;
  }
  return static_cast<std::int64_t>(amount_argument) * kResourceFixedPointScale;
}

// LogicAreaEffectObject exact runtime identity and fields.
inline constexpr std::int32_t kAreaEffectObjectKind = 3;
inline constexpr std::uintptr_t kAreaEffectObjectVtableOffset = 0x01a4f9a0;
inline constexpr std::uintptr_t kAreaEffectObjectFactoryOffset = 0x01080fa4;
inline constexpr std::uintptr_t kAreaEffectObjectTickOffset = 0x01070d18;
inline constexpr std::size_t kAreaEffectObjectLevelOffset = 0xfc;
inline constexpr std::size_t kAreaEffectObjectRemainingLifeOffset = 0x100;
inline constexpr std::size_t kAreaEffectObjectParentOffset = 0x120;
inline constexpr std::size_t kAreaEffectObjectFollowTargetOffset = 0x128;
inline constexpr std::size_t kAreaEffectObjectRelatedTargetOffset = 0x130;

// LogicAreaEffectObjectData fields consumed by the runtime object.
inline constexpr std::size_t kAreaLifeDurationOffset = 0x148;
inline constexpr std::size_t kAreaRadiusOffset = 0x14c;
inline constexpr std::size_t kAreaAffectsHiddenOffset = 0x18d;
inline constexpr std::size_t kAreaCanBeTargetedOffset = 0x19b;
inline constexpr std::size_t kAreaStayAfterParentDiesOffset = 0x170;
inline constexpr std::size_t kAreaFollowBehaviourOffset = 0x1a0;

inline constexpr std::uintptr_t kCombatSpawnOffset = 0x01083358;
inline constexpr std::uintptr_t kCombatRemoveOffset = 0x0108355c;
inline constexpr std::uint8_t kCombatSpawnPrologue[16] = {
    0xfd, 0x7b, 0xbc, 0xa9, 0xf7, 0x0b, 0x00, 0xf9, 0xf6, 0x57, 0x02, 0xa9, 0xf4, 0x4f, 0x03, 0xa9,
};
inline constexpr std::uint8_t kCombatRemovePrologue[16] = {
    0xfd, 0x7b, 0xbd, 0xa9, 0xf5, 0x0b, 0x00, 0xf9, 0xf4, 0x4f, 0x02, 0xa9, 0xfd, 0x03, 0x00, 0x91,
};
inline constexpr std::uint8_t kAreaEffectObjectTickPrologue[16] = {
    0xff, 0xc3, 0x03, 0xd1, 0xfd, 0x7b, 0x09, 0xa9, 0xfc, 0x6f, 0x0a, 0xa9, 0xfa, 0x67, 0x0b, 0xa9,
};

constexpr bool exact_area_effect_object(std::int32_t object_kind, std::uintptr_t runtime_vtable_offset) {
  return object_kind == kAreaEffectObjectKind && runtime_vtable_offset == kAreaEffectObjectVtableOffset;
}

// SpawnAttach=true reaches the generic character-spawn helper only through
// this exact call site.  A TLS context around the helper lets the existing
// committed-spawn hook attach the validated source to each validated child.
//
// 16.635.1: the helper was inlined into all of its callers, so there is no
// hookable entry and no exact caller return address any more. The sentinel
// values below never match a real caller offset, which disables the
// SpawnAttach provenance edge; the hook and fingerprints are not installed.
inline constexpr bool kSpawnAttachHelperAvailable = false;
inline constexpr std::uintptr_t kCharacterSpawnHelperOffset = ~std::uintptr_t{0};
inline constexpr std::uintptr_t kSpawnAttachHelperCallOffset = ~std::uintptr_t{0};
inline constexpr std::uintptr_t kSpawnAttachHelperReturnOffset = ~std::uintptr_t{0};
inline constexpr std::uint8_t kCharacterSpawnHelperPrologue[16] = {
    0xff, 0x43, 0x04, 0xd1, 0xfd, 0x7b, 0x0b, 0xa9, 0xfc, 0x6f, 0x0c, 0xa9, 0xfa, 0x67, 0x0d, 0xa9,
};
inline constexpr std::uint8_t kSpawnAttachHelperCallFingerprint[16] = {
    0xc9, 0x00, 0x00, 0x94, 0xa0, 0x43, 0x00, 0xd1, 0xc2, 0xc5, 0x11, 0x94, 0xbf, 0x2e, 0x00, 0x71,
};

constexpr bool exact_spawn_attach_path(std::uintptr_t helper_offset, std::uintptr_t caller_return_offset) {
  return helper_offset == kCharacterSpawnHelperOffset && caller_return_offset == kSpawnAttachHelperReturnOffset;
}

// Contextual native predicate: bool(subject, source, option).  Character
// vtable+0x148 points to f1cb90.  f1cb90 has a +0x180 early-false guard and
// falls through to the larger body at f1cba0; hooking only the body loses
// authoritative negative results.
inline constexpr std::uintptr_t kCharacterVtableOffset = 0x01a4fbb8;
inline constexpr std::size_t kAreaDamageEligibleVtableSlot = 0x148;
inline constexpr std::uintptr_t kAreaDamageEligibleOffset = 0x01079120;
inline constexpr std::uintptr_t kAreaDamageEligibleBodyOffset = 0x01079130;
inline constexpr std::uint8_t kAreaDamageEligiblePrologue[16] = {
    0x08, 0xc0, 0x40, 0xf9, 0x68, 0x00, 0x00, 0xb4, 0xe0, 0x03, 0x00, 0x12, 0xc0, 0x03, 0x5f, 0xd6,
};

// King-tower start action:
// ActionWaitToActivate runtime checks its condition, then calls f23110.
inline constexpr std::uintptr_t kTowerTargetSetOffset = 0x010ba8e0;
inline constexpr std::uintptr_t kActionDispatchOffset = 0x01080784;
inline constexpr std::uintptr_t kActionSpawnToLocationExecuteOffset = 0x00fb7e64;
inline constexpr std::uintptr_t kActionSpawnToLocationStaticVtableOffset = 0x01a47298;
inline constexpr std::size_t kActionSpawnToLocationDataOffset = 0xf0;
// ActionSpawnToLocation mode 1 creates its child through the concrete object
// manager entry at f2ffb8.  The f24188 caller reaches this function only after
// the exact request has produced the child; its LR and caller-frame request
// slot therefore form a synchronous, pointer-exact causal bridge.  Mode 3
// uses a different path and is intentionally excluded by the caller guard.
inline constexpr std::uintptr_t kActionSpawnMode1ChildCreateOffset = 0x0108d838;
inline constexpr std::uintptr_t kActionSpawnMode1ChildCreateReturnOffset = 0x0108236c;
inline constexpr std::size_t kActionSpawnMode1RequestSlotOffset = 0x78;  // 16.635.1 (was 0x68)
inline constexpr std::size_t kActionSpawnMode1RequestDataOffset = 0x00;
inline constexpr std::size_t kActionSpawnMode1RequestSourceOffset = 0x08;
inline constexpr std::size_t kActionSpawnMode1RequestBaseFromSlot = 0x48;
inline constexpr std::uintptr_t kPendingObjectAddOffset = 0x010830f4;
inline constexpr std::uintptr_t kActionWaitUpdateOffset = 0x010b6110;
inline constexpr std::uintptr_t kActionWaitDispatchCallOffset = 0x010b6178;
inline constexpr std::uintptr_t kActionWaitDispatchReturnOffset = 0x010b617c;
inline constexpr std::uintptr_t kActionWaitStaticVtableOffset = 0x01a32488;
inline constexpr std::uintptr_t kActionWaitRuntimeVtableOffset = 0x01a4f7f8;
inline constexpr std::size_t kActionWaitConditionOffset = 0xf0;
inline constexpr std::size_t kActionWaitOnActivateActionOffset = 0xf8;
inline constexpr std::size_t kActionRuntimeStaticDataOffset = 0x18;
inline constexpr std::size_t kActionRuntimeOwnerOffset = 0x20;

inline constexpr std::uint8_t kActionDispatchPrologue[16] = {
    0xfd, 0x7b, 0xbd, 0xa9, 0xf6, 0x57, 0x01, 0xa9, 0xf4, 0x4f, 0x02, 0xa9, 0xfd, 0x03, 0x00, 0x91,
};
inline constexpr std::uint8_t kActionSpawnToLocationExecutePrologue[16] = {
    0xff, 0x83, 0x03, 0xd1, 0xfd, 0x7b, 0x08, 0xa9, 0xfc, 0x6f, 0x09, 0xa9, 0xfa, 0x67, 0x0a, 0xa9,
};
inline constexpr std::uint8_t kActionSpawnMode1ChildCreatePrologue[16] = {
    0xfd, 0x7b, 0xbc, 0xa9, 0xf7, 0x0b, 0x00, 0xf9, 0xf6, 0x57, 0x02, 0xa9, 0xf4, 0x4f, 0x03, 0xa9,
};
inline constexpr std::uint8_t kPendingObjectAddPrologue[16] = {
    0x08, 0x00, 0x40, 0xf9, 0x02, 0xe0, 0x41, 0x39, 0xe3, 0x03, 0x1f, 0x2a, 0x04, 0x21, 0x40, 0xf9,
};
inline constexpr std::uint8_t kActionWaitUpdatePrologue[16] = {
    0xfd, 0x7b, 0xbc, 0xa9, 0xf7, 0x0b, 0x00, 0xf9, 0xf6, 0x57, 0x02, 0xa9, 0xf4, 0x4f, 0x03, 0xa9,
};
inline constexpr std::uint8_t kActionWaitDispatchCallFingerprint[16] = {
    0xdf, 0x29, 0xff, 0x97, 0xe0, 0x03, 0x13, 0xaa, 0xf4, 0x4f, 0x43, 0xa9, 0xf7, 0x0b, 0x40, 0xf9,
};

// ActionChangeGameObjectData exact static object and execution entry.
inline constexpr std::uintptr_t kChangeGameObjectDataVtableOffset = 0x01a3feb8;
inline constexpr std::uintptr_t kChangeGameObjectDataExecuteOffset = 0x00f93844;
inline constexpr std::uintptr_t kChangeMutationCallOffset = 0x00f93884;
inline constexpr std::size_t kChangeNewCharacterDataOffset = 0xf0;
inline constexpr std::size_t kChangeNewProjectileDataOffset = 0xf8;
inline constexpr std::size_t kChangeResetTargetOffset = 0x100;
inline constexpr std::uint8_t kChangeGameObjectDataExecutePrologue[16] = {
    0xfd, 0x7b, 0xbd, 0xa9, 0xf5, 0x0b, 0x00, 0xf9, 0xf4, 0x4f, 0x02, 0xa9, 0xfd, 0x03, 0x00, 0x91,
};
inline constexpr std::uint8_t kChangeMutationCallFingerprint[16] = {
    0x00, 0x01, 0x3f, 0xd6, 0xd3, 0x02, 0x00, 0xb4, 0xe0, 0x03, 0x15, 0xaa, 0xf1, 0xde, 0x03, 0x94,
};

constexpr bool exact_transform_transition(std::uintptr_t old_data, std::uintptr_t new_data,
                                          std::uintptr_t expected_character_data,
                                          std::uintptr_t expected_projectile_data) {
  if (old_data == 0 || new_data == 0 || old_data == new_data) {
    return false;
  }
  const bool character_match = expected_character_data != 0 && new_data == expected_character_data;
  const bool projectile_match = expected_projectile_data != 0 && new_data == expected_projectile_data;
  return character_match != projectile_match;
}

static_assert(classify_resource_delta(kResourceWholeDeltaOffset, kPeriodicResourceReturnOffset) ==
              ResourceDeltaCause::Periodic);
static_assert(classify_resource_delta(kResourceWholeDeltaOffset, kDeathOwnerResourceReturnOffset) ==
              ResourceDeltaCause::DeathOwner);
static_assert(classify_resource_delta(kResourceFixedDeltaOffset, kDeathOpponentResourceReturnOffset) ==
              ResourceDeltaCause::DeathOpponent);
static_assert(requested_resource_delta_fixed(ResourceDeltaCause::Periodic, 1) == 10000);
static_assert(exact_area_effect_object(3, kAreaEffectObjectVtableOffset));
static_assert(exact_spawn_attach_path(kCharacterSpawnHelperOffset, kSpawnAttachHelperReturnOffset));

struct PendingSpawnChildIdentity {
  std::uintptr_t data_pointer = 0;
  std::uintptr_t vtable_offset = 0;
  std::int32_t data_global_id = 0;
};

constexpr std::uint32_t bind_pending_spawn_native_id(std::uint32_t stored, std::uint32_t observed,
                                                    bool exact_creation) {
  return stored == 0 && exact_creation ? observed : stored;
}

constexpr bool pending_spawn_native_id_reused(std::uint32_t created, std::uint32_t current) {
  return created != 0 && current != 0 && created != current;
}

// A deferred proof does not own its native allocation. An uncommitted child
// can be destroyed and its address reused by another concrete object type.
// Data alone is insufficient (native character transforms can change it):
// require a later tick, a different concrete vtable AND different data.
// Same-type reuse and genuine late commits retain the existing strict check.
constexpr bool pending_spawn_address_reused(const PendingSpawnChildIdentity &created,
                                            const PendingSpawnChildIdentity &current,
                                            std::int32_t created_tick, std::int32_t current_tick) {
  return created_tick >= 0 && current_tick > created_tick && created.data_pointer != 0 &&
         current.data_pointer != 0 && created.vtable_offset != 0 && current.vtable_offset != 0 &&
         created.data_global_id != 0 && current.data_global_id != 0 &&
         created.vtable_offset != current.vtable_offset && created.data_pointer != current.data_pointer &&
         created.data_global_id != current.data_global_id;
}

} // namespace cr_remaining_runtime

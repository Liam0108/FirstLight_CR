#pragma once

// Exact-build action-owned movement layout for Null's Royale 15.535.13.
//
// This domain is deliberately separate from ordinary attack-component dashes
// and from active Buff/effect state.  The two hooks below are class-specific:
//
//   * libg+f49d24 commits one ActionDashingAttackChain hop; and
//   * libg+e82a34 executes ActionWarpCharacter and writes the final position.
//
// Runtime records are retained only after the static action name, non-zero
// LogicData global ID, exact action/runtime vtables, and source entity identity
// agree with the narrow allowlist below.

#include <cstddef>
#include <cstdint>

namespace cr_action_movement_runtime {

constexpr const char *kSchema = "native-action-movement-runtime.v1";
constexpr const char *kExpectedLibgSha256 = "0b580222e5a3502cf153bb5e6297ec32d2b154b605b777c74873dd75722e4eaa";
constexpr const char *kExpectedLibgBuildId = "179ac4bd38c205bc5041d372a79f1c2f929b1c30";

constexpr std::uintptr_t kGoldenKnightHopOffset = 0x010a7230;
constexpr std::uintptr_t kWarpPositionCommitOffset = 0x00fc019c;

constexpr std::uint8_t kGoldenKnightHopPrologue[16] = {
    0xfd, 0x7b, 0xbb, 0xa9, 0xfa, 0x67, 0x01, 0xa9, 0xf8, 0x5f, 0x02, 0xa9, 0xf6, 0x57, 0x03, 0xa9,
};
constexpr std::uint8_t kWarpPositionCommitPrologue[16] = {
    0xff, 0xc3, 0x01, 0xd1, 0xfd, 0x7b, 0x01, 0xa9, 0xfc, 0x6f, 0x02, 0xa9, 0xfa, 0x67, 0x03, 0xa9,
};

constexpr std::uintptr_t kDashingAttackChainDataVtableOffset = 0x01a40c28;
constexpr std::uintptr_t kDashingAttackChainRuntimeVtableOffset = 0x01a52428;
constexpr std::uintptr_t kWarpCharacterDataVtableOffset = 0x01a481b0;

constexpr std::size_t kLogicDataNameOffset = 0x28;
constexpr std::size_t kLogicDataGlobalIdOffset = 0x40;
constexpr std::size_t kMinimumActionDataBytes = 0x44;

constexpr std::size_t kActionRuntimeDataOffset = 0x18;
constexpr std::size_t kActionRuntimeOwnerOffset = 0x20;
constexpr std::size_t kDashingAttackChainStateOffset = 0x60;
constexpr std::size_t kDashingAttackChainIndexOffset = 0x64;
constexpr std::size_t kMinimumDashingAttackChainRuntimeBytes = 0x68;

constexpr std::size_t kActionExecutionOwnerOffset = 0x08;
constexpr std::size_t kMinimumActionExecutionContextBytes = 0x10;

constexpr std::int32_t kGoldenKnightCardId = 26000074;
constexpr std::int32_t kBossBanditCardId = 26000103;
constexpr std::int32_t kEliteArcherCardId = 26000062;
constexpr std::int32_t kEliteArcherHeroFormCardId = 203000062;

constexpr const char *kGoldenKnightExecuteActionName = "GoldenKnight_Execute_Charge";
constexpr const char *kBossBanditWarpActionName = "BossBandit_ability_warp";
constexpr const char *kEliteArcherWarpActionName = "EliteArcherHero_Ability_Warp";

} // namespace cr_action_movement_runtime

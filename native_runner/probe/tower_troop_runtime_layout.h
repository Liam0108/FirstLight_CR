#pragma once

#include <cstddef>
#include <cstdint>

// Exact-build Action runtime layouts for the two competitive Tower Troops
// whose public tactical state is not represented by ordinary tower HP/attack
// snapshots.  These constants are valid only for Null's Royale 15.535.13.
namespace cr_tower_troop_runtime {

inline constexpr char kSchema[] = "native-tower-troop-runtime.v1";
inline constexpr char kExactLibgSha256[] = "0b580222e5a3502cf153bb5e6297ec32d2b154b605b777c74873dd75722e4eaa";
inline constexpr char kExactLibgBuildId[] = "179ac4bd38c205bc5041d372a79f1c2f929b1c30";

inline constexpr std::size_t kRuntimeStaticDataOffset = 0x18;
inline constexpr std::size_t kRuntimeSourceObjectOffset = 0x20;

// ActionBurstAttack: Dagger Duchess charge inventory and reload accumulator.
inline constexpr std::uintptr_t kDaggerInitOffset = 0x010a1270;
inline constexpr std::uintptr_t kDaggerTickOffset = 0x010a129c;
inline constexpr std::uintptr_t kDaggerRuntimeVtableOffset = 0x01a51810;
inline constexpr std::uintptr_t kDaggerStaticVtableOffset = 0x01a3f6a8;
inline constexpr std::size_t kDaggerChargeCountOffset = 0x60;
inline constexpr std::size_t kDaggerRechargeElapsedMsOffset = 0x64;
inline constexpr std::size_t kDaggerMaxChargeCountOffset = 0xec;
inline constexpr std::size_t kDaggerRechargeDurationMsOffset = 0xf0;
inline constexpr std::size_t kDaggerRechargeIncrementOffset = 0xf4;
inline constexpr std::uint8_t kDaggerInitPrologue[16] = {
    0xfd, 0x7b, 0xbe, 0xa9, 0xf3, 0x0b, 0x00, 0xf9, 0xfd, 0x03, 0x00, 0x91, 0xf3, 0x03, 0x00, 0xaa,
};
inline constexpr std::uint8_t kDaggerTickPrologue[16] = {
    0xfd, 0x7b, 0xbc, 0xa9, 0xf7, 0x0b, 0x00, 0xf9, 0xf6, 0x57, 0x02, 0xa9, 0xf4, 0x4f, 0x03, 0xa9,
};

// ActionChefTower: delay, contribution accumulator, and pending pancake
// recipient.  contributionNeeded is stored in static units and multiplied by
// 20 by the exact native accessor at libg+0xe58e28.
inline constexpr std::uintptr_t kChefInitOffset = 0x010a5378;
inline constexpr std::uintptr_t kChefTickOffset = 0x010a53ac;
inline constexpr std::uintptr_t kChefRuntimeVtableOffset = 0x01a51ec0;
inline constexpr std::uintptr_t kChefStaticVtableOffset = 0x01a40168;
inline constexpr std::size_t kChefStartDelayRemainingMsOffset = 0x68;
inline constexpr std::size_t kChefCookingContributionOffset = 0x6c;
inline constexpr std::size_t kChefTargetHandleOffset = 0x70;
inline constexpr std::size_t kChefThrowDelayRemainingMsOffset = 0x74;
inline constexpr std::size_t kChefTargetObjectOffset = 0x78;
inline constexpr std::size_t kChefContributionNeededOffset = 0xec;
inline constexpr std::size_t kChefStartDelayDurationMsOffset = 0x184;
inline constexpr std::int32_t kChefContributionScale = 20;
inline constexpr std::int32_t kChefNoThrowDelay = -1;
// ActionChefTower subtracts one 50 ms logic tick at the release boundary. If
// no live recipient can be resolved, it returns with -50 and a null target.
inline constexpr std::int32_t kChefTargetlessThrowDelay = -50;
inline constexpr std::uint8_t kChefInitPrologue[16] = {
    0xfd, 0x7b, 0xbe, 0xa9, 0xf3, 0x0b, 0x00, 0xf9, 0xfd, 0x03, 0x00, 0x91, 0xf3, 0x03, 0x00, 0xaa,
};
inline constexpr std::uint8_t kChefTickPrologue[16] = {
    0xfd, 0x7b, 0xba, 0xa9, 0xfc, 0x6f, 0x01, 0xa9, 0xfa, 0x67, 0x02, 0xa9, 0xf8, 0x5f, 0x03, 0xa9,
};

} // namespace cr_tower_troop_runtime

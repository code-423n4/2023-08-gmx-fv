// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/role/RoleStore.sol";
import "../../contracts/role/Role.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract RoleStoreHarness is RoleStore {

    using EnumerableSet for EnumerableSet.AddressSet;

    function containsRole(address account, bytes32 roleKey) public view returns (bool) {
        return roleMembers[roleKey].contains(account);
    }

    function containsRoleInCache(address account, bytes32 roleKey) public view returns (bool) {
        return roleCache[account][roleKey];
    }

    function getMembersLength(bytes32 roleKey) external view returns (uint256) {
        return roleMembers[roleKey].length();
    }

    function getRoleMemberByIndex(bytes32 roleKey, uint256 index) external view returns (address) {
        return roleMembers[roleKey].at(index);
    }

    function bytes32ToUint(bytes32 val) external view returns (uint256) {
        return uint256(val);
    }

    function addressToBytes32(address val) external view returns (bytes32) {
        return bytes32(uint256(uint160(val)));
    }

    function ROLE_ADMIN() external view returns (bytes32) {
        return Role.ROLE_ADMIN;
    }

    function TIMELOCK_MULTISIG() external view returns (bytes32) {
        return Role.TIMELOCK_MULTISIG;
    }
}

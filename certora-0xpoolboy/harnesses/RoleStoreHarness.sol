// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/role/RoleStore.sol";

contract RoleStoreHarness is RoleStore {
    using EnumerableSet for EnumerableSet.AddressSet;
    //using EnumerableValues for EnumerableSet.AddressSet;
    using EnumerableSet for EnumerableSet.Bytes32Set;
    function isAdmin(address account) external view returns (bool) {
        return hasRole(account, Role.ROLE_ADMIN);
    }
    function hasRoleFromRoleMembers(address account, bytes32 roleKey) external view returns (bool) {
        return roleMembers[roleKey].contains(account);
    }

    function isRoleKey(bytes32 roleKey) external view returns (bool) {
        return roles.contains(roleKey);
    }

    function ROLE_ADMIN() external view returns (bytes32) {
        return Role.ROLE_ADMIN;
    }

    function TIMELOCK_MULTISIG() external view returns (bytes32) {
        return Role.TIMELOCK_MULTISIG;
    }
}
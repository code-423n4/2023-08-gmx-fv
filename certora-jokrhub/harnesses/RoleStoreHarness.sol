// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/role/RoleStore.sol";

contract RoleStoreHarness is RoleStore {
    using EnumerableSet for EnumerableSet.AddressSet;
    using EnumerableSet for EnumerableSet.Bytes32Set;
    function rolesContains(bytes32 roleKey) external returns (bool) {
        return roles.contains(roleKey);
    }

    function roleMembersContains(bytes32 roleKey, address account) external returns (bool) {
        return roleMembers[roleKey].contains(account);
    }

    function roleMembersCount(bytes32 roleKey) external returns(uint256) {
        return roleMembers[roleKey].length();
    }

    function getRoleAdmin() external returns (bytes32) {
        return Role.ROLE_ADMIN;
    }

    function getTimelockMultisig() external returns (bytes32) {
        return Role.TIMELOCK_MULTISIG;
    }

    function isAdminHarness () external returns (bool) {
        if (hasRole(msg.sender, Role.ROLE_ADMIN)) {
            return true;
        }
        return false;
    }

    function admin() external returns (bytes32) {
        return Role.ROLE_ADMIN;
    }


}

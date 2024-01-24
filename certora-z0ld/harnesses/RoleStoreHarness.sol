// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.19;

import "../../contracts/role/RoleStore.sol";

contract RoleStoreHarness is RoleStore {

    using EnumerableSet for EnumerableSet.AddressSet;
    using EnumerableSet for EnumerableSet.Bytes32Set;
    using EnumerableValues for EnumerableSet.AddressSet;
    using EnumerableValues for EnumerableSet.Bytes32Set;

    function hasRoleAdmin(address account) external view returns (bool) {
        return hasRole(account, Role.ROLE_ADMIN);
    }

    function isRoleAdmin(bytes32 roleKey) external pure returns (bool) {
        return roleKey == Role.ROLE_ADMIN;
    }

    function isRoleTimelockMultisig(bytes32 roleKey) external pure returns (bool) {
        return roleKey == Role.TIMELOCK_MULTISIG;
    }

    function addressToBytes32(address addr) external pure returns (bytes32) {
        return bytes32(uint256(uint160(addr)));
    }

    function bytes32ToAddress(bytes32 b) external pure returns (address) {
        return address(uint160(uint256(b)));
    }

    function grantRoleHarness(address account, bytes32 roleKey) external onlyRoleAdmin {
        _grantRole(account, roleKey);
    }

    function revokeRoleHarness(address account, bytes32 roleKey) external onlyRoleAdmin {
        _revokeRole(account, roleKey);
    }
}

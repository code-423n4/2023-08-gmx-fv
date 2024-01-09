// SPDX-License-Identifier: BUSL-1.1

pragma solidity ^0.8.0;
import "../../contracts/oracle/OracleStore.sol";

contract OracleStoreHarness is OracleStore {
    using EnumerableSet for EnumerableSet.AddressSet;
    constructor(RoleStore _roleStore, EventEmitter _eventEmitter) OracleStore(_roleStore, _eventEmitter) {}

    function signersContains(address maybeSigner) public view returns (bool) {
        return signers.contains(maybeSigner);
    }

    function hasRoleWrapper(bytes32 role) public view returns (bool) {
        return roleStore.hasRole(msg.sender, role);
    }

    function hasControllerRole() public view returns (bool) {
        return hasRoleWrapper(Role.CONTROLLER);
    }

    function getSignerSetValues() public view returns (address[] memory) {
        return signers.values();
    }
    function getSignerSetIndexFor(address addr) public view returns (uint256) {
        return signers._inner._indexes[bytes32(uint256(uint160(addr)))];
    }

}
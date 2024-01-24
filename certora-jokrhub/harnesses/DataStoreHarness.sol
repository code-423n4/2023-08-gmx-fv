// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/data/DataStore.sol";

contract DataStoreHarness is DataStore {
    using SafeCast for int256;
    using SignedMath for int256;

    constructor(RoleStore _roleStore) DataStore(_roleStore) {}

    function sumReturnInt256Harness(uint256 uintValue, int256 value) external returns (uint256) {
        return Calc.sumReturnUint256(uintValue, value);
    }

    function negativeCast(int256 value) external returns (uint256) {
        return (-value).toUint256();
    }    

    function isControllerHarness () external returns (bool) {
        if (roleStore.hasRole(msg.sender, Role.CONTROLLER)) {
            return true;
        }
        return false;
    }

    function absHarness(int256 value) external returns (uint256) {
        return value.abs();
    }

    function validString() external returns (string memory) {
        return "error";
    }

    function compareStrings(string memory s1, string memory s2) external returns (bool) {
        return keccak256(abi.encodePacked(s1)) == keccak256(abi.encodePacked(s2));
    }

    function getBytes0() external returns (bytes32) {
        return 0;
    }

}

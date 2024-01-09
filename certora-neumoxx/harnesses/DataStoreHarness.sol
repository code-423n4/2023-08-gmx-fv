// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/data/DataStore.sol";
import {Role} from "../../contracts/role/Role.sol";

contract DataStoreHarness is DataStore {

    using SafeCast for int256;

    constructor(RoleStore _roleStore) DataStore(_roleStore) {}

    function maxInt256() external returns (int256) {
        return type(int256).max;
    }

    function minInt256() external returns (int256) {
        return type(int256).min;
    }

    function stringLength(string calldata value) external returns (uint256) {
        return bytes(value).length;
    }

    function stringsEqual(string memory a, string memory b) external pure returns (bool) {
        return keccak256(abi.encode(a)) == keccak256(abi.encode(b));
    }

    function uintArraysEqual(uint256[] calldata a, uint256[] calldata b) external pure returns (bool) {
        return a.length == b.length && keccak256(abi.encode(a)) == keccak256(abi.encode(b));
    }

    function intArraysEqual(int256[] calldata a, int256[] calldata b) external pure returns (bool) {
        return a.length == b.length && keccak256(abi.encode(a)) == keccak256(abi.encode(b));
    }

    function addressArraysEqual(address[] calldata a, address[] calldata b) external pure returns (bool) {
        return a.length == b.length && keccak256(abi.encode(a)) == keccak256(abi.encode(b));
    }

    function boolArraysEqual(bool[] calldata a, bool[] calldata b) external pure returns (bool) {
        return a.length == b.length && keccak256(abi.encode(a)) == keccak256(abi.encode(b));
    }

    function stringArraysEqual(string[] calldata a, bytes32 key) external view returns (bool) {
        string[] memory b = this.getStringArray(key);
        return a.length == b.length && keccak256(abi.encode(a)) == keccak256(abi.encode(b));
    }

    function bytes32ArraysEqual(bytes32[] calldata a, bytes32[] calldata b) external pure returns (bool) {
        return a.length == b.length && keccak256(abi.encode(a)) == keccak256(abi.encode(b));
    }

    function hasRoleWrapper(bytes32 role) public view returns (bool) {
        return roleStore.hasRole(msg.sender, role);
    }

    function hasControllerRole() public view returns (bool) {
        return hasRoleWrapper(Role.CONTROLLER);
    }

    function applyDeltaToUintRevertCondition(bytes32 key, int256 value) external view returns (bool) {
        uint256 currValue = uintValues[key];
        return value < 0 && (-value).toUint256() > currValue;
    }
}

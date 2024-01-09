// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.19;

import "../../contracts/data/DataStore.sol";
import "../../contracts/utils/Calc.sol";

contract DataStoreHarness is DataStore {

    constructor(RoleStore _roleStore) DataStore(_roleStore) {}

    function sumReturnUint256Harness(uint256 a, int256 b) external pure returns (uint256) {
        return Calc.sumReturnUint256(a, b);
    }

    function hasRoleControllerHarness(address account) external view returns (bool) {
        return roleStore.hasRole(account, Role.CONTROLLER);
    }

    function getStringArrayHarness(bytes32 key, uint256 index) external view returns (bytes1[] memory) {
        string[] memory stringArray = this.getStringArray(key);
        require(index < stringArray.length, "Index out of bounds"); 
        return this.stringToBytes1Array(stringArray[index]);
    }

    function stringToBytes1Array(string calldata val) external pure returns (bytes1[] memory) {

        bytes memory barr = bytes(val); 
        bytes1[] memory arr = new bytes1[](barr.length);  

        for (uint256 i; i < barr.length; ++i) {
            arr[i] = bytes1(barr[i]);
        }

        return arr;
    }

    function bytes32ToUint256(bytes32 val) external pure returns (uint256) {
        return uint256(val);
    }

    function bytes32ToAddress(bytes32 val) external pure returns (address) {
        return address(uint160(uint256(val)));
    }

    function uint256ToBytes32(uint256 val) external pure returns (bytes32) {
        return bytes32(val);
    }

    function addressToBytes32(address val) external pure returns (bytes32) {
        return bytes32(uint256(uint160(val)));
    }

    function minusInt256ToUint256(int256 val) external pure returns (uint256) {
        return uint256(-val);
    }
}

// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/bank/StrictBank.sol";
import "../../contracts/data/Keys.sol";

contract StrictBankHarness is StrictBank {

    constructor(RoleStore _roleStore, DataStore _dataStore) StrictBank(_roleStore, _dataStore) {}

    function afterTransferOut(address token) external {
        _afterTransferOut(token);
    }

    function getETHBalance(address account) external returns(uint256) {
        return account.balance;
    }

    function tokenTransferGasLimit(address token) external pure returns (bytes32) {
        return Keys.TOKEN_TRANSFER_GAS_LIMIT;
    }

    function hasRoleWrapper(bytes32 role) public view returns (bool) {
        return roleStore.hasRole(msg.sender, role);
    }

    function hasControllerRole() public view returns (bool) {
        return hasRoleWrapper(Role.CONTROLLER);
    }

    function getWntAddress() public view returns (address) {
        return dataStore.getAddress(Keys.WNT);
    }

    function getHoldingAddress() public view returns (address) {
        return dataStore.getAddress(Keys.HOLDING_ADDRESS);
    }

    function getGasLimit(address token) public view returns (uint256) {
        return dataStore.getUint(Keys.tokenTransferGasLimit(token));
    }
}

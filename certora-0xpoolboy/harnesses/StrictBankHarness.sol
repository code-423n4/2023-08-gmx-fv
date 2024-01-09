// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/bank/StrictBank.sol";

contract StrictBankHarness is StrictBank {

    constructor(RoleStore _roleStore, DataStore _dataStore) StrictBank(_roleStore, _dataStore) {}

    function afterTransferOut(address token) external {
        _afterTransferOut(token);
    }

    function isController() external view returns(bool) {
        return roleStore.hasRole(msg.sender, Role.CONTROLLER);
    }

    function ERC20TokenBalanceOf(address token, address user) external view returns(uint256) {
        return IERC20(token).balanceOf(user);
    }

    function  getHoldingAddress() external view returns (address) {
        return dataStore.getAddress(Keys.HOLDING_ADDRESS);
    }

    function getTokenGasLimit(address token) external view returns (uint256) {
        return dataStore.getUint(Keys.tokenTransferGasLimit(token));
    }
}
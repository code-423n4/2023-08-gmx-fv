// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/bank/StrictBank.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract StrictBankHarness is StrictBank {

    constructor(RoleStore _roleStore, DataStore _dataStore) StrictBank(_roleStore, _dataStore) {}

    function afterTransferOut(address token) external {
        _afterTransferOut(token);
    }

    function getBalanceOf(address token, address contractAddress) external returns (uint256) {
        return IERC20(token).balanceOf(contractAddress);
    }

    function afterTransferOutHarness(address token) external {
        _afterTransferOut(token);
    }

    function getHoldingAddress() external returns (address) {
        return dataStore.getAddress(Keys.HOLDING_ADDRESS);
    }

    function getWntAddress() external returns (address) {
        return dataStore.getAddress(Keys.WNT);
    }

    function getEthBalance(address account) external returns (uint256) {
        return address(account).balance;
    }

    function isControllerHarness () external returns (bool) {
        if (roleStore.hasRole(msg.sender, Role.CONTROLLER)) {
            return true;
        }
        return false;
    }
}
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.19;

import "../../contracts/bank/StrictBank.sol";

contract StrictBankHarness is StrictBank {

    constructor(RoleStore _roleStore, DataStore _dataStore) StrictBank(_roleStore, _dataStore) {}

    function afterTransferOut(address token) external {
        _afterTransferOut(token);
    }

    function isController(address account) external view returns (bool hasRole) {
        hasRole = roleStore.hasRole(account, Role.CONTROLLER);
    }

    function wntAddress() external view returns (address wnt) {
        wnt = TokenUtils.wnt(dataStore);
    }

    function holdingAddress() external view returns (address holding) {
        holding = dataStore.getAddress(Keys.HOLDING_ADDRESS);
    }
}
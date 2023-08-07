// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "../../contracts/data/DataStore.sol";

contract DataStoreHarness is DataStore {
    constructor(RoleStore _roleStore) DataStore(_roleStore) {}
}

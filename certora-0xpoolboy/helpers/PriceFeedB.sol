// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {PriceFeedMock} from "./PriceFeedMock.sol";

contract PriceFeedB is PriceFeedMock {
    address public immutable feedToken;
    constructor(address _token) {
        feedToken = _token;
    }
}
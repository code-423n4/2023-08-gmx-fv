// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IPriceFeed} from "../../contracts/oracle/IPriceFeed.sol";

/// @title PriceFeedMock - storage based
abstract contract PriceFeedMock is IPriceFeed {
    mapping(uint256 => int256) private _answer;
    mapping(uint256 => uint256) private _updatedAt;

    function latestRoundData() external view returns (
        uint80,
        int256,
        uint256,
        uint256,
        uint80
    ) {
        uint256 updatedAt = _updatedAt[block.timestamp];
        require (updatedAt >= block.timestamp);

        return (
            uint80(0), // roundId
            _answer[block.timestamp], // answer
            0, // startedAt
            updatedAt, // updatedAt
            uint80(0) // answeredInRound
        );
    }
}

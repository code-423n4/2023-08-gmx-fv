// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import {Oracle, DataStore, EventEmitter, RoleStore, OracleStore} from "../../contracts/Oracle/Oracle.sol";
import {OracleUtils} from "../../contracts/Oracle/OracleUtils.sol";
import {Bits} from "../../contracts/utils/Bits.sol";
import {Price} from "../../contracts/price/Price.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/utils/math/SafeCast.sol";
import "../../contracts/oracle/IPriceFeed.sol";
import "../../contracts/utils/Precision.sol";
import "../../contracts/data/Keys.sol";
import "../../contracts/chain/Chain.sol";
import "../../contracts/utils/Precision.sol";
import "../../contracts/role/Role.sol";


contract OracleHarness is Oracle {
    using Price for Price.Props;
    using EnumerableSet for EnumerableSet.AddressSet;

    DataStore public immutable myDataStore;
    EventEmitter public immutable myEventEmitter;
    OracleUtils.ReportInfo public myReportInfo;
    /// @dev : struct fields of SetPricesParams. See _prepareParams().
    uint256 public mySignerInfo;
    address[] public myTokens;
    uint256[] public myCompactedMinOracleBlockNumbers;
    uint256[] public myCompactedMaxOracleBlockNumbers;
    uint256[] public myCompactedOracleTimestamps;
    uint256[] public myCompactedDecimals;
    uint256[] public myCompactedMinPrices;
    uint256[] public myCompactedMinPricesIndexes;
    uint256[] public myCompactedMaxPrices;
    uint256[] public myCompactedMaxPricesIndexes;
    bytes[] public mySignatures;
    address[] public myPriceFeedTokens;

    constructor(
        RoleStore _roleStore,
        OracleStore _oracleStore,
        DataStore _dataStore,
        EventEmitter _eventEmitter
    ) Oracle(_roleStore, _oracleStore) {
        myDataStore = _dataStore;
        myEventEmitter = _eventEmitter;
    }

    function setPrices(
        DataStore,
        EventEmitter,
        OracleUtils.SetPricesParams memory
    ) public override {
        super.setPrices(myDataStore, myEventEmitter, _prepareParams());
    }

    function _prepareParams() internal view returns (OracleUtils.SetPricesParams memory params) {
        require(mySignerInfo & Bits.BITMASK_16 > 0);
        require(myTokens.length == 1);
        require(myCompactedMinOracleBlockNumbers.length == 1);
        require(myCompactedMaxOracleBlockNumbers.length == 1);
        require(myCompactedOracleTimestamps.length == 1);
        require(myCompactedDecimals.length == 1);
        require(myCompactedMinPrices.length == 1);
        require(myCompactedMinPricesIndexes.length == 1);
        require(myCompactedMaxPrices.length == 1);
        require(myCompactedMaxPricesIndexes.length == 1);
        require(mySignatures.length == 1);
        require(myPriceFeedTokens.length == 1);

        params = 
        OracleUtils.SetPricesParams(
            mySignerInfo,
            myTokens,
            myCompactedMinOracleBlockNumbers,
            myCompactedMaxOracleBlockNumbers,
            myCompactedOracleTimestamps,
            myCompactedDecimals,
            myCompactedMinPrices,
            myCompactedMinPricesIndexes,
            myCompactedMaxPrices,
            myCompactedMaxPricesIndexes,
            mySignatures,
            myPriceFeedTokens
        );
    }

     function _prepareMultiParams() internal view returns (OracleUtils.SetPricesParams memory params) {
        require(mySignerInfo & Bits.BITMASK_16 > 0);
        require(myTokens.length == 2);
        require(myCompactedMinOracleBlockNumbers.length == 2);
        require(myCompactedMaxOracleBlockNumbers.length == 2);
        require(myCompactedOracleTimestamps.length == 2);
        require(myCompactedDecimals.length == 2);
        require(myCompactedMinPrices.length == 2);
        require(myCompactedMinPricesIndexes.length == 2);
        require(myCompactedMaxPrices.length == 2);
        require(myCompactedMaxPricesIndexes.length == 2);
        require(mySignatures.length == 2);
        require(myPriceFeedTokens.length == 2);

        params = 
        OracleUtils.SetPricesParams(
            mySignerInfo,
            myTokens,
            myCompactedMinOracleBlockNumbers,
            myCompactedMaxOracleBlockNumbers,
            myCompactedOracleTimestamps,
            myCompactedDecimals,
            myCompactedMinPrices,
            myCompactedMinPricesIndexes,
            myCompactedMaxPrices,
            myCompactedMaxPricesIndexes,
            mySignatures,
            myPriceFeedTokens
        );
    }

    function getStablePrice(DataStore, address token) public view override returns (uint256) {
        return super.getStablePrice(myDataStore, token);
    }

    function getPriceFeedMultiplier(DataStore, address token) public view override returns (uint256) {
        return super.getPriceFeedMultiplier(myDataStore, token);
    }

    function getSignerByInfo(uint256 signerInfo, uint256 i) public view returns (address) {
        uint256 signerIndex = signerInfo >> (16 + 16 * i) & Bits.BITMASK_16;
        require (signerIndex < MAX_SIGNER_INDEX);
        return oracleStore.getSigner(signerIndex);
    }

    function validateSignerHarness(
        bytes32 SALT,
        bytes memory signature,
        address expectedSigner
    ) external view {
        OracleUtils.validateSigner(SALT, myReportInfo, signature, expectedSigner);
    }

    function getPrimaryPriceHarness(address token) external view returns (Price.Props memory) {
        Price.Props memory price = primaryPrices[token];
        return price;
    }

    function setContainsHarness(address token) external view returns (bool) {
        return tokensWithPrices.contains(token);
    }

    function setLengthHarness() external view returns (uint256) {
        return tokensWithPrices.length();
    }

    function getPriceFeedPriceHarness(address token) external view returns (bool, uint256) {
        return _getPriceFeedPrice(myDataStore, token);
    }

    function getMyTokens() external view returns (address[] memory) {
        return myTokens;
    }
    
    function setPricesHarness() external {
        _setPrices(myDataStore, myEventEmitter, _prepareParams());
    }

    function setPricesMultiHarness() external {
        _setPrices(myDataStore, myEventEmitter, _prepareMultiParams());
    }

    function setPricesVerifyHarness () external {
        setPrices(myDataStore, myEventEmitter, _prepareParams());
    }

    function setPricesFromPriceFeedsHarness(address[] calldata priceFeedTokens) external {
        _setPricesFromPriceFeeds(myDataStore, myEventEmitter, priceFeedTokens);
    }

    function validatePricesHarness() external returns(ValidatedPrice[] memory) {
        return _validatePrices(myDataStore, _prepareParams());
    }

    function getSignersHarness() external returns(address [] memory) {
        return _getSigners(myDataStore, _prepareParams());
    }

    function getLatestRoundData(address priceFeedAddress) external returns (int256, uint256) {
        IPriceFeed priceFeed = IPriceFeed(priceFeedAddress);
        (   
            uint80 a,
            int256 _price,
            uint256 b,
            uint256 timestamp,
            uint80 c
        ) = priceFeed.latestRoundData();
        return (_price, timestamp);
    }

    function getPriceFeedKey(address token) external returns (bytes32) {
        return Keys.priceFeedKey(token);
    }

    function getPriceFeedHeartbeatDurationKey(address token) external returns (bytes32) {
        return Keys.priceFeedHeartbeatDurationKey(token);
    }

    function getPriceFeedMultiplierKey(address token) external returns (bytes32) {
        return Keys.priceFeedMultiplierKey(token);
    }

    function castToUint256(int256 _price) external returns (uint256) {
        return SafeCast.toUint256(_price);
    }

    function mulDiv(uint256 price, uint256 precision, uint256 float_precision) external returns (uint256) {
        return Precision.mulDiv(price, precision, float_precision);
    }

    function getCurrentTimestamp() external returns (uint256) {
        return Chain.currentTimestamp();
    }

    function getSignerIndex(uint256 signerInfo, uint256 index) external returns (uint256) {
        return signerInfo >> (16 + 16 * index) & Bits.BITMASK_16;
    }

    function getSignersCount(uint256 signerInfo) external  returns (uint256) {
        return signerInfo & Bits.BITMASK_16;
    }

    function getMinSigners() external returns (uint256) {
        return myDataStore.getUint(Keys.MIN_ORACLE_SIGNERS);
    }

    function getMaxSigners() external returns (uint256) {
        return MAX_SIGNERS;
    }

    function getMaxSignerIndex() external returns (uint256) {
        return MAX_SIGNER_INDEX;
    }

    function getUncompactedOracleTimestampAt0() external returns (uint256) {
        return OracleUtils.getUncompactedOracleTimestamp(myCompactedOracleTimestamps, 0);
    }

    function getMinUncompactedOracleBlockNumberAt0() external returns (uint256) {
        return OracleUtils.getUncompactedOracleBlockNumber(myCompactedMinOracleBlockNumbers, 0);
    }

    function getMaxUncompactedOracleBlockNumberAt0() external returns (uint256) {
        return OracleUtils.getUncompactedOracleBlockNumber(myCompactedMaxOracleBlockNumbers, 0);
    }

    function getTokenAt0 () external returns (address) {
        return myTokens[0];
    }

    function getSignersLength() external returns (uint256) {
        return _getSigners(myDataStore, _prepareParams()).length;
    }

    function getMinPricesAt0() external returns (uint256) {
        return OracleUtils.getUncompactedPrice(myCompactedMinPrices, 0);
    }

    function getMyPriceFeedTokens() external returns (address[] memory) {
        return myPriceFeedTokens;
    }

    function tokenWithPricesLength() external returns (uint256) {
        return tokensWithPrices.length();
    }

    function isEmptyHarness(Price.Props memory props) external returns (bool) {
        return props.min == 0 || props.max == 0;
    }

    function getDiff(uint256 price, uint256 refPrice) external returns (uint256) {
        return Calc.diff(price, refPrice);
    }

    function getDiffFactor(uint256 diff, uint256 refPrice) external returns (uint256) {
        return Precision.toFactor(diff, refPrice);
    }

    function validateRefPriceHarness(address token, uint256 price, uint256 refPrice, uint256 maxRefPriceDeviationFactor) external {
        validateRefPrice(token, price, refPrice, maxRefPriceDeviationFactor);
    }

    function isControllerHarness () external returns (bool) {
        if (roleStore.hasRole(msg.sender, Role.CONTROLLER)) {
            return true;
        }
        return false;
    }

}

 
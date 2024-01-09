// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/utils/math/SafeCast.sol";

import {Oracle, DataStore, EventEmitter, RoleStore, OracleStore, Role} from "../../contracts/oracle/Oracle.sol";
import {OracleUtils} from "../../contracts/oracle/OracleUtils.sol";
import {Bits} from "../../contracts/utils/Bits.sol";
import "../../contracts/data/Keys.sol";
import "../../contracts/oracle/IPriceFeed.sol";
import "../../contracts/price/Price.sol";
import "../../contracts/utils/Precision.sol";

contract OracleHarness is Oracle {

    using EnumerableSet for EnumerableSet.AddressSet;
    //using EnumerableValues for EnumerableSet.AddressSet;

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

    function setPrices() public {
        super.setPrices(myDataStore, myEventEmitter, _prepareParams());
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
        //require(myTokens.length > 0);
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

    function getPriceFeedMultiplier(address token) external view returns (uint256) {
                return super.getPriceFeedMultiplier(myDataStore, token);
    }

    function getPriceFeedPrice(address token) external view returns (bool, uint256) {
        return _getPriceFeedPrice(myDataStore, token);
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

    function getMyPriceFeedToken(uint256 i) external view returns (address) {
        require(i < myPriceFeedTokens.length);
        return myPriceFeedTokens[i];
    }
/*
    function getParams() external view returns (OracleUtils.SetPricesParams memory params){
        return _prepareParams();
    }
*/
    function getPriceFeedHeartbeatDuration(address token) external view returns (uint256) {
        return myDataStore.getUint(Keys.priceFeedHeartbeatDurationKey(token));
    }

    function getPriceFeedTimestamp(address token) external view returns(uint256) {
        address priceFeedAddress = myDataStore.getAddress(Keys.priceFeedKey(token));
        require(priceFeedAddress != address(0));

        IPriceFeed priceFeed = IPriceFeed(priceFeedAddress);
        (
            /* uint80 roundID */,
            /* int256 _price */,
            /* uint256 startedAt */,
            uint256 timestamp,
            /* uint80 answeredInRound */
        ) = priceFeed.latestRoundData();
        return timestamp;
    }

    function getPriceFeedPriceRaw(address token) external view returns(int256) {
        address priceFeedAddress = myDataStore.getAddress(Keys.priceFeedKey(token));
        require(priceFeedAddress != address(0));

        IPriceFeed priceFeed = IPriceFeed(priceFeedAddress);
        (
            /* uint80 roundID */,
            int256 _price,
            /* uint256 startedAt */,
            /* uint256 timestamp*/,
            /* uint80 answeredInRound */
        ) = priceFeed.latestRoundData();
        return _price;
    }

    function validatePrices1() external view returns (address, uint256,uint256,uint256,uint256,uint256) {
        OracleUtils.SetPricesParams memory p = _prepareParams();

        ValidatedPrice[] memory valP_ = _validatePrices(myDataStore, p);
        require(valP_.length >= 1);

        ValidatedPrice memory valP = valP_[0];
        return (valP.token, valP.min, valP.max, valP.timestamp, valP.minBlockNumber, valP.maxBlockNumber);
    }
/*
    function validatePrices1Length() external view returns (uint256) {
        ValidatedPrice[] memory valP = _validatePrices(myDataStore, _prepareParams());
        return valP.length;
    }
*/
    function getTokenLength() external view returns (uint256) {
        return _prepareParams().tokens.length;
    }

    function getMinOracleBlockNumber(uint256 tokenIndex) external view returns(uint256 minOracleBlockNumber) {
        OracleUtils.SetPricesParams memory params = _prepareParams();
        require(tokenIndex < _prepareParams().tokens.length);
        minOracleBlockNumber = OracleUtils.getUncompactedOracleBlockNumber(params.compactedMinOracleBlockNumbers, tokenIndex);
    }

    function getMaxOracleBlockNumber(uint256 tokenIndex) external view returns(uint256 maxOracleBlockNumber) {
        OracleUtils.SetPricesParams memory params = _prepareParams();
        require(tokenIndex < _prepareParams().tokens.length);
        maxOracleBlockNumber = OracleUtils.getUncompactedOracleBlockNumber(params.compactedMaxOracleBlockNumbers, tokenIndex);
    }

    function getMaxPriceAge() external view returns(uint256) {
        return myDataStore.getUint(Keys.MAX_ORACLE_PRICE_AGE);
    }

    function getPrimaryPricesMin(address token) external view returns(uint256){
        return primaryPrices[token].min;
    }

    function getPrimaryPricesMax(address token) external view returns(uint256){
        return primaryPrices[token].max;
    }

    function tokenWithPricesContains(address token) external view returns(bool) {
        return tokensWithPrices.contains(token);
    }

    function validateRefPriceWrapper(
        address token,
        uint256 price,
        uint256 refPrice,
        uint256 maxRefPriceDeviationFactor
    ) external pure returns(uint256) {
        validateRefPrice(token, price, refPrice, maxRefPriceDeviationFactor);
        uint256 diff = Calc.diff(price, refPrice);
        uint256 diffFactor = Precision.toFactor(diff, refPrice);
        return (diffFactor);
    }

    function isController() external view returns(bool) {
        return roleStore.hasRole(msg.sender, Role.CONTROLLER);
    }
    /*
    function MinOracleBlockNumbersAreSorted() external view returns(bool) {
        uint256 prevBlockNum = 0;
        OracleUtils.SetPricesParams memory params = _prepareParams();
        for (uint256 i; i < params.tokens.length; i++) {
            uint256 minOracleBlockNumber = OracleUtils.getUncompactedOracleBlockNumber(params.compactedMinOracleBlockNumbers, i);
            if (prevBlockNum < minOracleBlockNumber) {
                return false;
            }
        }
        return true;
    }*/
}
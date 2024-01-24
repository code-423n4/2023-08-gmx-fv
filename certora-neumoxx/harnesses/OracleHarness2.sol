// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import {Oracle, DataStore, EventEmitter, RoleStore, OracleStore} from "../../contracts/oracle/Oracle.sol";
import {OracleUtils} from "../../contracts/oracle/OracleUtils.sol";
import {Bits} from "../../contracts/utils/Bits.sol";
import {Keys} from "../../contracts/data/Keys.sol";

contract OracleHarness2 is Oracle {

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
        //super.setPrices(myDataStore, myEventEmitter, _prepareParams());
    }

    function getSigners(
        DataStore dataStore,
        OracleUtils.SetPricesParams memory params
    ) external view returns (address[] memory) {
        return _getSigners(myDataStore, _prepareParams());
    }

    function validatePricesNoSignersOneToken() external view returns (ValidatedPrice[] memory) {
        return _validatePrices(myDataStore, _prepareParamsNoSignersOneToken());
    }

    function validatePricesOneSignerOneToken() external view returns (ValidatedPrice[] memory) {
        return _validatePrices(myDataStore, _prepareParamsOneSignerOneToken());
    }

    function validatePricesOneSignerTwoTokens() external view returns (ValidatedPrice[] memory) {
        return _validatePrices(myDataStore, _prepareParamsOneSignerTwoTokens());
    }

    function _prepareParams() internal view returns (OracleUtils.SetPricesParams memory params) {
        require(mySignerInfo == 0);
        require(myTokens.length == 1);
        require(myTokens[0] == address(10));
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

    function _prepareParamsNoSignersOneToken() internal view returns (OracleUtils.SetPricesParams memory params) {
        require(mySignerInfo == 0);
        require(myTokens.length == 1);
        require(myTokens[0] == address(10));
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

    function _prepareParamsOneSignerOneToken() internal view returns (OracleUtils.SetPricesParams memory params) {
        require(mySignerInfo == 2**16 + 1);
        require(myTokens.length == 1);
        require(myTokens[0] == address(10));
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

    function _prepareParamsOneSignerTwoTokens() internal view returns (OracleUtils.SetPricesParams memory params) {
        require(mySignerInfo == 2**16 + 1);
        require(myTokens.length == 2);
        require(myTokens[0] == address(10));
        require(myTokens[1] == address(20));
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

    function getUncompactedOracleTimestampExternal(uint256[] memory compactedOracleTimestamps, uint256 index) external pure returns (uint256) {
        return OracleUtils.getUncompactedOracleTimestamp(compactedOracleTimestamps, index);
    }

    function getMaxOraclePriceAge() public view returns (uint256) {
        return myDataStore.getUint(Keys.MAX_ORACLE_PRICE_AGE);
    }
}

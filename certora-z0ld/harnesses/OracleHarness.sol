// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.19;

import {Oracle, DataStore, EventEmitter, RoleStore, OracleStore} from "../../contracts/oracle/Oracle.sol";
import {OracleUtils} from "../../contracts/oracle/OracleUtils.sol";
import {Bits} from "../../contracts/utils/Bits.sol";
import {Role} from "../../contracts/role/RoleModule.sol";
import {Price} from "../../contracts/price/Price.sol";
import {Keys} from "../../contracts/data/Keys.sol";

import "@openzeppelin/contracts/utils/math/SafeCast.sol";
import "../../contracts/utils/Precision.sol";

contract OracleHarness is Oracle {

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

    function getMinBlockConfirmations() external view returns (uint256) {
        return myDataStore.getUint(Keys.MIN_ORACLE_BLOCK_CONFIRMATIONS);
    }

    function getMaxPriceAge() external view returns (uint256) {
        return myDataStore.getUint(Keys.MAX_ORACLE_PRICE_AGE);
    }

    function getMaxRefPriceDeviationFactor() external view returns (uint256) {
        return myDataStore.getUint(Keys.MAX_ORACLE_REF_PRICE_DEVIATION_FACTOR);
    }

    function myTokensArray() external view returns (address[] memory) {
        return myTokens;
    }

    function myTokensLength() external view returns (uint256) {
        return myTokens.length;
    }

    function myCompactedMinOracleBlockNumbersArray() external view returns (uint256[] memory) {
        return myCompactedMinOracleBlockNumbers;
    }

    function myCompactedMinOracleBlockNumbersLength() external view returns (uint256) {
        return myCompactedMinOracleBlockNumbers.length;
    }

    function myCompactedMaxOracleBlockNumbersArray() external view returns (uint256[] memory) {
        return myCompactedMaxOracleBlockNumbers;
    }

    function myCompactedMaxOracleBlockNumbersLength() external view returns (uint256) {
        return myCompactedMaxOracleBlockNumbers.length;
    }

    function myCompactedOracleTimestampsArray() external view returns (uint256[] memory) {
        return myCompactedOracleTimestamps;
    }

    function myCompactedOracleTimestampsLength() external view returns (uint256) {
        return myCompactedOracleTimestamps.length;
    }

    function myCompactedDecimalsArray() external view returns (uint256[] memory) {
        return myCompactedDecimals;
    }

    function myCompactedDecimalsLength() external view returns (uint256) {
        return myCompactedDecimals.length;
    }

    function myCompactedMinPricesArray() external view returns (uint256[] memory) {
        return myCompactedMinPrices;
    }

    function myCompactedMinPricesLength() external view returns (uint256) {
        return myCompactedMinPrices.length;
    }

    function myCompactedMinPricesIndexesArray() external view returns (uint256[] memory) {
        return myCompactedMinPricesIndexes;
    }

    function myCompactedMinPricesIndexesLength() external view returns (uint256) {
        return myCompactedMinPricesIndexes.length;
    }

    function myCompactedMaxPricesArray() external view returns (uint256[] memory) {
        return myCompactedMaxPrices;
    }

    function myCompactedMaxPricesLength() external view returns (uint256) {
        return myCompactedMaxPrices.length;
    }

    function myCompactedMaxPricesIndexesArray() external view returns (uint256[] memory) {
        return myCompactedMaxPricesIndexes;
    }

    function myCompactedMaxPricesIndexesLength() external view returns (uint256) {
        return myCompactedMaxPricesIndexes.length;
    }

    function mySignaturesArray() external view returns (bytes[] memory) {
        return mySignatures;
    }

    function mySignaturesLength() external view returns (uint256) {
        return mySignatures.length;
    }

    function myPriceFeedTokensArray() external view returns (address[] memory) {
        return myPriceFeedTokens;
    }

    function myPriceFeedTokensLength() external view returns (uint256) {
        return myPriceFeedTokens.length;
    }

    function validatePricesHarness(uint256 index) external view returns (
        uint256 length,
        address token,
        uint256 min,
        uint256 max,
        uint256 timestamp,
        uint256 minBlockNumber,
        uint256 maxBlockNumber
        ) {
        Oracle.ValidatedPrice[] memory vp = _validatePrices(myDataStore, _prepareParams());
        length = vp.length;
        require(index < length);
        
        token = vp[index].token;
        min = vp[index].min;
        max = vp[index].max;
        timestamp = vp[index].timestamp;
        minBlockNumber = vp[index].minBlockNumber;
        maxBlockNumber = vp[index].maxBlockNumber;
    }

    function validatePricesMinBlockNumberArrayHarness() external view returns (uint256[] memory) {
        Oracle.ValidatedPrice[] memory vp = _validatePrices(myDataStore, _prepareParams());
        uint256[] memory arr = new uint256[](vp.length);
        for(uint256 i; i < vp.length; ++i) {
            arr[i] = vp[i].minBlockNumber;
        }

        return arr;
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

    function hasRoleControllerHarness(address account) external view returns (bool) {
        return roleStore.hasRole(account, Role.CONTROLLER);
    }

    function getPrimaryPriceMinHarness(address token) external view returns (uint256) {
        Price.Props memory price = this.getPrimaryPrice(token);
        return price.min;
    }

    function getPrimaryPriceMaxHarness(address token) external view returns (uint256) {
        Price.Props memory price = this.getPrimaryPrice(token);
        return price.max;
    }

    function getPriceFeedPriceHarness(address dataStore, address token) external view returns (bool, uint256) {
        return _getPriceFeedPrice(DataStore(dataStore), token);
    }

    function getPriceFeedAddress(address dataStore, address token) external view returns (address) {
        return DataStore(dataStore).getAddress(Keys.priceFeedKey(token));
    }

    function addressToBytes32(address val) external pure returns (bytes32) {
        return bytes32(uint256(uint160(val)));
    }

    function bytes32ToAddress(bytes32 val) external pure returns (address) {
        return address(uint160(uint256(val)));
    }

    function getHeartbeatDuration(address dataStore, address token) external view returns (uint256 heartbeatDuration) {
        heartbeatDuration = DataStore(dataStore).getUint(Keys.priceFeedHeartbeatDurationKey(token));
    }

    function getAdjustedPrice(address dataStore, address token, int256 _price) external view returns (uint256 adjustedPrice) {
        uint256 price = SafeCast.toUint256(_price);
        uint256 precision = getPriceFeedMultiplier(DataStore(dataStore), token);
        adjustedPrice = Precision.mulDiv(price, precision, Precision.FLOAT_PRECISION);
    }

    function setPricesFromPriceFeedsHarness(address dataStore, address eventEmitter, address[] memory priceFeedTokens) external {
        _setPricesFromPriceFeeds(DataStore(dataStore), EventEmitter(eventEmitter), priceFeedTokens);
    }

    function setPrimaryPriceHarness(address token, uint256 min, uint256 max) external {
        Price.Props memory price = Price.Props(min, max);
        this.setPrimaryPrice(token, price);
    }
}
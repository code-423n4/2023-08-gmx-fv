// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;


import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {Oracle, DataStore, EventEmitter, RoleStore, OracleStore} from "../../contracts/oracle/Oracle.sol";
import {OracleUtils} from "../../contracts/oracle/OracleUtils.sol";
import {Role} from "../../contracts/role/Role.sol";
import {Keys} from "../../contracts/data/Keys.sol";
import {Bits} from "../../contracts/utils/Bits.sol";

import "../../contracts/error/Errors.sol";

contract OracleHarness is Oracle {

    using EnumerableSet for EnumerableSet.AddressSet;

    bytes32 public MY_SALT = keccak256(abi.encode(block.chainid, "xget-oracle-v1"));

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

    /*

    function prepareParams(uint256 signerInfo, address[] memory tokens, uint256[] memory compactedMinOracleBlockNumbers,
            uint256[] memory compactedMaxOracleBlockNumbers, uint256[] memory compactedOracleTimestamps, uint256[] memory compactedDecimals,
            uint256[] memory compactedMinPrices, uint256[] memory compactedMinPricesIndexes, uint256[] memory compactedMaxPrices,
            uint256[] memory compactedMaxPricesIndexes, bytes[] memory signatures, address[] memory priceFeedTokens)
            external view returns (OracleUtils.SetPricesParams memory params) {
        require(mySignerInfo & Bits.BITMASK_16 > 0);

        params =
        OracleUtils.SetPricesParams(
            signerInfo,
            tokens,
            compactedMinOracleBlockNumbers,
            compactedMaxOracleBlockNumbers,
            compactedOracleTimestamps,
            compactedDecimals,
            compactedMinPrices,
            compactedMinPricesIndexes,
            compactedMaxPrices,
            compactedMaxPricesIndexes,
            signatures,
            priceFeedTokens
        );
    }

    function prepareParamsSingle(uint256 signerInfo, address tokens1, uint256 compactedMinOracleBlockNumbers1,
            uint256 compactedMaxOracleBlockNumbers1, uint256 compactedOracleTimestamps1, uint256 compactedDecimals1,
            uint256 compactedMinPrices1, uint256 compactedMinPricesIndexes1, uint256 compactedMaxPrices1,
            uint256 compactedMaxPricesIndexes1, bytes memory signatures1, address priceFeedTokens1)
            external view returns (OracleUtils.SetPricesParams memory params) {

        require(signerInfo & Bits.BITMASK_16 > 0);

        address[] memory tokens = new address[](1);
        tokens[0] = tokens1;
        uint256[] memory compactedMinOracleBlockNumbers = new uint256[](1);
        compactedMinOracleBlockNumbers[0] = compactedMinOracleBlockNumbers1;
        uint256[] memory compactedMaxOracleBlockNumbers = new uint256[](1);
        compactedMaxOracleBlockNumbers[0] = compactedMaxOracleBlockNumbers1;
        uint256[] memory compactedOracleTimestamps = new uint256[](1);
        compactedOracleTimestamps[0] = compactedOracleTimestamps1;
        uint256[] memory compactedDecimals = new uint256[](1);
        compactedDecimals[0] = compactedDecimals1;
        uint256[] memory compactedMinPrices = new uint256[](1);
        compactedMinPrices[0] = compactedMinPrices1;
        uint256[] memory compactedMinPricesIndexes = new uint256[](1);
        compactedMinPricesIndexes[0] = compactedMinPricesIndexes1;
        uint256[] memory compactedMaxPrices = new uint256[](1);
        compactedMaxPrices[0] = compactedMaxPrices1;
        uint256[] memory compactedMaxPricesIndexes = new uint256[](1);
        compactedMaxPricesIndexes[0] = compactedMaxPricesIndexes1;
        bytes[] memory signatures = new bytes[](1);
        signatures[0] = signatures1;
        address[] memory priceFeedTokens = new address[](1);
        priceFeedTokens[0] = priceFeedTokens1;

        params =
        OracleUtils.SetPricesParams(
            signerInfo,
            tokens,
            compactedMinOracleBlockNumbers,
            compactedMaxOracleBlockNumbers,
            compactedOracleTimestamps,
            compactedDecimals,
            compactedMinPrices,
            compactedMinPricesIndexes,
            compactedMaxPrices,
            compactedMaxPricesIndexes,
            signatures,
            priceFeedTokens
        );
    }

    function prepareParamsDouble(uint256 signerInfo, address tokens1, address tokens2,
            uint256 compactedMinOracleBlockNumbers1, uint256 compactedMinOracleBlockNumbers2,
            uint256 compactedMaxOracleBlockNumbers1, uint256 compactedMaxOracleBlockNumbers2,
            uint256 compactedOracleTimestamps1, uint256 compactedOracleTimestamps2,
            uint256 compactedDecimals1, uint256 compactedDecimals2, uint256 compactedMinPrices1,
            uint256 compactedMinPrices2, uint256 compactedMinPricesIndexes1, uint256 compactedMinPricesIndexes2,
            uint256 compactedMaxPrices1, uint256 compactedMaxPrices2, uint256 compactedMaxPricesIndexes1,
            uint256 compactedMaxPricesIndexes2, bytes memory signatures1, bytes memory signatures2,
            address priceFeedTokens1, address priceFeedTokens2)
            external returns (OracleUtils.SetPricesParams memory params) {

        require(signerInfo & Bits.BITMASK_16 > 0);

        bytes[] memory signatures = new bytes[](2);
        signatures[0] = signatures1;
        signatures[1] = signatures2;

        params =
        OracleUtils.SetPricesParams(
            signerInfo,
            _getAddress2ElemArray(tokens1, tokens2),
            _getUint2ElemArray(compactedMinOracleBlockNumbers1, compactedMinOracleBlockNumbers2),
            _getUint2ElemArray(compactedMaxOracleBlockNumbers1, compactedMaxOracleBlockNumbers2),
            _getUint2ElemArray(compactedOracleTimestamps1, compactedOracleTimestamps2),
            _getUint2ElemArray(compactedDecimals1, compactedDecimals2),
            _getUint2ElemArray(compactedMinPrices1, compactedMinPrices2),
            _getUint2ElemArray(compactedMinPricesIndexes1, compactedMinPricesIndexes2),
            _getUint2ElemArray(compactedMaxPrices1, compactedMaxPrices2),
            _getUint2ElemArray(compactedMaxPricesIndexes1, compactedMaxPricesIndexes2),
            signatures,
            _getAddress2ElemArray(priceFeedTokens1, priceFeedTokens2)
        );
    }

    function _getAddress2ElemArray(address a1, address a2) internal returns (address[] memory) {
        address[] memory res = new address[](2);
        res[0] = a1;
        res[1] = a2;

        return res;

    }

    function _getUint2ElemArray(uint256 a1, uint256 a2) internal returns (uint256[] memory) {
        uint256[] memory res = new uint256[](2);
        res[0] = a1;
        res[1] = a2;

        return res;

    }*/

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

    function getSigners(
        OracleUtils.SetPricesParams memory params
    ) external view returns (address[] memory) {
        return _getSigners(myDataStore, params);
    }

    function validateSignerHarness(
        bytes32 SALT,
        bytes memory signature,
        address expectedSigner
    ) external view {
        validateSigner(SALT, myReportInfo, signature, expectedSigner);
    }

    function validateSigner(
        bytes32 salt,
        OracleUtils.ReportInfo memory info,
        bytes memory signature,
        address expectedSigner
    ) internal pure {
        bytes32 digest = ECDSA.toEthSignedMessageHash(
            keccak256(abi.encode(
                salt,
                info.minOracleBlockNumber,
                info.maxOracleBlockNumber,
                info.oracleTimestamp,
                info.blockHash,
                info.token,
                info.tokenOracleType,
                info.precision,
                info.minPrice,
                info.maxPrice
            ))
        );

        address recoveredSigner = ECDSA.recover(digest, signature);
        if (recoveredSigner != expectedSigner) {
            revert Errors.InvalidSignature(recoveredSigner, expectedSigner);
        }
    }

    function hasRoleWrapper(bytes32 role) public view returns (bool) {
        return roleStore.hasRole(msg.sender, role);
    }

    function hasControllerRole() public view returns (bool) {
        return hasRoleWrapper(Role.CONTROLLER);
    }

    function getPriceFeedAddress() public view returns (address) {
        return myDataStore.getAddress(Keys.priceFeedKey(tokensWithPrices.at(0)));
    }

    function getPriceFeedAddress(address token) public view returns (address) {
        return myDataStore.getAddress(Keys.priceFeedKey(token));
    }

    function getTokensWithPricesLength() public view returns (uint256) {
        return tokensWithPrices.length();
    }

    function getTokenAt(uint256 index) public view returns (address) {
        return tokensWithPrices.at(index);
    }

    function getHeartbeatDurationFromDataStore(address token) public view returns (uint256) {
        return myDataStore.getUint(Keys.priceFeedHeartbeatDurationKey(token));
    }

    function getStablePriceFromDataStore(address token) public view returns (uint256) {
        return myDataStore.getUint(Keys.stablePriceKey(token));
    }

    function getPriceFeedMultiplierFromDataStore(address token) public view returns (uint256) {
        return myDataStore.getUint(Keys.priceFeedMultiplierKey(token));
    }

    function getMinOracleSigners() public view returns (uint256) {
        return myDataStore.getUint(Keys.MIN_ORACLE_SIGNERS);
    }

    function validateRefPriceExternal(
        address token,
        uint256 price,
        uint256 refPrice,
        uint256 maxRefPriceDeviationFactor
    ) external pure {
        validateRefPrice(token, price, refPrice, maxRefPriceDeviationFactor);
    }

    function removePrimaryPriceExternal(address token) external {
        _removePrimaryPrice(token);
    }

    function tokensWithPricesContains(address token) external returns (bool) {
        return tokensWithPrices.contains(token);
    }

    function getPriceFeedPriceExternal(address token) external view returns (bool, uint256) {
        return _getPriceFeedPrice(myDataStore, token);
    }

    function setPricesFromPriceFeedsExternal(EventEmitter eventEmitter, address[] memory priceFeedTokens) external {
        _setPricesFromPriceFeeds(myDataStore, eventEmitter, priceFeedTokens);
    }

    function getSaltExternal() external view returns (bytes32) {
        return _getSalt();
    }

    function getDiffFactor(uint256 diff, uint256 refPrice) external returns (uint256) {
        return (diff == 0 || refPrice == 0) ? 0 : diff * (10 ** 30) / refPrice;
    }
}

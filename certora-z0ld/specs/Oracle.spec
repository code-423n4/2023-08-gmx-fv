using PriceFeedA as _PriceFeedA;

///////////////// METHODS //////////////////////

// author: z0ld
methods {

    // OracleHarness
    function getSignerByInfo(uint256, uint256) internal returns (address);
    function validateSignerHarness(bytes32, bytes, address) external;
    function getPriceFeedPriceHarness(address, address) external returns (bool, uint256);
    function setPricesFromPriceFeedsHarness(address, address, address[]) external;
    function setPrimaryPriceHarness(address, uint256, uint256) external;
    function validatePricesHarness(uint256) external returns (uint256, address, uint256, uint256, uint256, uint256, uint256);
    function validatePricesMinBlockNumberArrayHarness() external returns (uint256[]);
    // envfree
    function hasRoleControllerHarness(address) external returns (bool) envfree;
    function getPrimaryPriceMinHarness(address) external returns (uint256) envfree;
    function getPrimaryPriceMaxHarness(address) external returns (uint256) envfree;
    function getPriceFeedAddress(address, address) external returns (address) envfree;
    function addressToBytes32(address) external returns (bytes32) envfree;
    function bytes32ToAddress(bytes32) external returns (address) envfree;
    function getHeartbeatDuration(address, address) external returns (uint256) envfree;
    function getAdjustedPrice(address, address, int256) external returns (uint256) envfree;
    function getMinBlockConfirmations() external returns (uint256) envfree;
    function getMaxPriceAge() external returns (uint256) envfree;
    function getMaxRefPriceDeviationFactor() external returns (uint256) envfree;

    function myTokensArray() external returns (address[]) envfree;
    function myTokensLength() external returns (uint256) envfree;
    function myCompactedMinOracleBlockNumbersLength() external returns (uint256) envfree;
    function myCompactedMaxOracleBlockNumbersArray() external returns (uint256[]) envfree;
    function myCompactedMaxOracleBlockNumbersLength() external returns (uint256) envfree;
    function myCompactedOracleTimestampsArray() external returns (uint256[]) envfree;
    function myCompactedOracleTimestampsLength() external returns (uint256) envfree;
    function myCompactedDecimalsArray() external returns (uint256[]) envfree;
    function myCompactedDecimalsLength() external returns (uint256) envfree;
    function myCompactedMinPricesArray() external returns (uint256[]) envfree;
    function myCompactedMinPricesLength() external returns (uint256) envfree;
    function myCompactedMinPricesIndexesArray() external returns (uint256[]) envfree;
    function myCompactedMinPricesIndexesLength() external returns (uint256) envfree;
    function myCompactedMaxPricesArray() external returns (uint256[]) envfree;
    function myCompactedMaxPricesLength() external returns (uint256) envfree;
    function myCompactedMaxPricesIndexesArray() external returns (uint256[]) envfree;
    function myCompactedMaxPricesIndexesLength() external returns (uint256) envfree;
    function mySignaturesArray() external returns (bytes[]) envfree;
    function mySignaturesLength() external returns (uint256) envfree;
    function myPriceFeedTokensArray() external returns (address[]) envfree;
    function myPriceFeedTokensLength() external returns (uint256) envfree;

    // Oracle
    function setPrices(address, address, OracleUtils.SetPricesParams) internal;
    function setPrimaryPrice(address, Price.Props) external;
    function clearAllPrices() external;
    function getStablePrice(address, address) internal returns (uint256);
    function getPriceFeedMultiplier(address, address) internal returns (uint256);
    function validatePrices(address, OracleUtils.SetPricesParams) external returns (Oracle.ValidatedPrice[]);
    // envfree
    function getTokensWithPricesCount() external returns (uint256) envfree;
    function getTokensWithPrices(uint256, uint256) external returns (address[]) envfree;
    function getPrimaryPrice(address) external returns (Price.Props) envfree;

    // DataStore
    function _.getUint(bytes32) external => DISPATCHER(true);
    function _.getAddress(bytes32) external => DISPATCHER(true);
    function _.getBytes32(bytes32) external => DISPATCHER(true);

    // RoleStore
    function _.hasRole(address,bytes32) external => DISPATCHER(true);

    // OracleStore
    function _.getSigner(uint256) external => DISPATCHER(true);

    // PriceFeed
    function _.latestRoundData() external => DISPATCHER(true);

    // Chain
    function _.arbBlockNumber() external => ghostBlockNumber() expect uint256 ALL;
    function _.arbBlockHash(uint256 blockNumber) external => ghostBlockHash(blockNumber) expect bytes32 ALL;

    // Oracle summaries
    function Oracle._getSalt() internal returns bytes32 => mySalt();

    // Getters
    function OracleHarness.primaryPrices(address) external returns (uint256,uint256);
    function OracleHarness.secondaryPrices(address) external returns (uint256,uint256);
    function OracleHarness.customPrices(address) external returns (uint256,uint256);
    function OracleHarness.getSignerByInfo(uint256, uint256) external returns (address);
}

///////////////// DEFINITIONS /////////////////////

definition PURE_VIEW_FUNCTIONS(method f) returns bool = f.isView || f.isPure;

definition HARNESS_FUNCTIONS(method f) returns bool =
    f.selector == sig:setPricesFromPriceFeedsHarness(address, address, address[]).selector
    || f.selector == sig:setPrimaryPriceHarness(address, uint256, uint256).selector
    || f.selector == sig:validatePricesHarness(uint256).selector
    || f.selector == sig:validatePricesMinBlockNumberArrayHarness().selector
    ;

definition EMPTY_TOKEN_PRICE(address token) returns bool = 
    (ghostTokensWithPricesIndexes[addressToBytes32(token)] == 0) 
    && (ghostPrimaryPricesMin[token] == 0) && (ghostPrimaryPricesMax[token] == 0);

definition NOT_EMPTY_TOKEN_PRICE(address token) returns bool = 
    (ghostTokensWithPricesIndexes[addressToBytes32(token)] != 0) 
    && (ghostPrimaryPricesMin[token] != 0) && (ghostPrimaryPricesMax[token] != 0);

definition MAX_ARRAY_LENGTH() returns uint256 = 0xffffffffffffffffffffffffffffffff;

////////////////// FUNCTIONS //////////////////////

function ghostMedian(uint256[] array) returns uint256 {
    uint256 med;
    uint256 len = array.length;
    require med >= array[0] && med <= array[require_uint256(len-1)];
    return med;
}

function setupValidateParams(env e) {
    require(e.block.timestamp != 0);
    require(e.block.number != 0);

    require(myCompactedMinOracleBlockNumbersLength() < MAX_ARRAY_LENGTH());
    require(myCompactedMaxOracleBlockNumbersLength() < MAX_ARRAY_LENGTH());
    require(myCompactedOracleTimestampsLength() < MAX_ARRAY_LENGTH());
    require(myCompactedDecimalsLength() < MAX_ARRAY_LENGTH());
    require(myCompactedMinPricesLength() < MAX_ARRAY_LENGTH());
    require(myCompactedMinPricesIndexesLength() < MAX_ARRAY_LENGTH());
    require(myCompactedMaxPricesLength() < MAX_ARRAY_LENGTH());
    require(myCompactedMaxPricesIndexesLength() < MAX_ARRAY_LENGTH());
    require(mySignaturesLength() < MAX_ARRAY_LENGTH());
    require(myPriceFeedTokensLength() < MAX_ARRAY_LENGTH());
}

///////////////// GHOSTS & HOOKS //////////////////

ghost mySalt() returns bytes32;

ghost ghostBlockNumber() returns uint256 {
    axiom ghostBlockNumber() != 0;
}

ghost ghostBlockHash(uint256) returns bytes32 {
    axiom forall uint256 num1. forall uint256 num2. 
        num1 != num2 => ghostBlockHash(num1) != ghostBlockHash(num2);
}

// tokensWithPrices

ghost uint256 ghostTokensWithPricesLength {
    axiom ghostTokensWithPricesLength < MAX_ARRAY_LENGTH();
    init_state axiom ghostTokensWithPricesLength == 0;
}

ghost uint256 ghostTokensWithPricesLengthPrev {
    axiom ghostTokensWithPricesLengthPrev < MAX_ARRAY_LENGTH();
    init_state axiom ghostTokensWithPricesLengthPrev == 0;
}

hook Sstore currentContract.tokensWithPrices.(offset 0) uint256 length STORAGE {
    ghostTokensWithPricesLengthPrev = ghostTokensWithPricesLength;
    ghostTokensWithPricesLength = length;
}

hook Sload uint256 length currentContract.tokensWithPrices.(offset 0) STORAGE {
    require ghostTokensWithPricesLength == length;
}

ghost mapping(bytes32 => uint256) ghostTokensWithPricesIndexes {
    init_state axiom forall bytes32 i. ghostTokensWithPricesIndexes[i] == 0;
}

hook Sstore currentContract.tokensWithPrices._inner._indexes[KEY bytes32 value] uint256 index STORAGE {
    ghostTokensWithPricesIndexes[value] = index;
}

hook Sload uint256 index currentContract.tokensWithPrices._inner._indexes[KEY bytes32 value] STORAGE {
    require(ghostTokensWithPricesIndexes[value] == index);
}

ghost mapping(mathint => bytes32) ghostTokensWithPricesValues {
    init_state axiom forall mathint i. ghostTokensWithPricesValues[i] == to_bytes32(0);
}

hook Sstore currentContract.tokensWithPrices._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostTokensWithPricesValues[index] = newValue;
}

hook Sload bytes32 value currentContract.tokensWithPrices._inner._values[INDEX uint256 index] STORAGE {
    require(ghostTokensWithPricesValues[index] == value);
}

// primaryPrices[].min

ghost mapping(address => uint256) ghostPrimaryPricesMin {
    init_state axiom forall address token. ghostPrimaryPricesMin[token] == 0;
}

hook Sstore currentContract.primaryPrices[KEY address token].(offset 0) uint256 min STORAGE {
    ghostPrimaryPricesMin[token] = min;
}

hook Sload uint256 min currentContract.primaryPrices[KEY address token].(offset 0) STORAGE {
    require(ghostPrimaryPricesMin[token] == min);
}

// primaryPrices[].max

ghost mapping(address => uint256) ghostPrimaryPricesMax {
    init_state axiom forall address token. ghostPrimaryPricesMax[token] == 0;
}

hook Sstore currentContract.primaryPrices[KEY address token].(offset 32) uint256 max STORAGE {
    ghostPrimaryPricesMax[token] = max;
}

hook Sload uint256 max currentContract.primaryPrices[KEY address token].(offset 32) STORAGE {
    require(ghostPrimaryPricesMax[token] == max);
}

///////////////// SETUP INVARIANTS ////////////////

//  This is the main invariant stating that the indexes and values always match:
//        values[indexes[v] - 1] = v for all values v in the set
//    and indexes[values[i]] = i+1 for all valid indexes i.

invariant setTokensWithPricesInvariant()
    (forall uint256 index. 0 <= index && index < ghostTokensWithPricesLength => to_mathint(ghostTokensWithPricesIndexes[ghostTokensWithPricesValues[index]]) == index + 1)
    && (forall bytes32 value. ghostTokensWithPricesIndexes[value] == 0 || 
         (ghostTokensWithPricesValues[ghostTokensWithPricesIndexes[value] - 1] == value && ghostTokensWithPricesIndexes[value] >= 1 && ghostTokensWithPricesIndexes[value] <= ghostTokensWithPricesLength)) 
    filtered { f -> !PURE_VIEW_FUNCTIONS(f) && !HARNESS_FUNCTIONS(f) }

///////////////// PROPERTIES //////////////////////

rule validateSignerConsistency() {
    env e1; env e2;
    require e1.msg.value == e2.msg.value;
    
    bytes32 salt1;
    bytes32 salt2;
    address signer1;
    address signer2;
    bytes signature;

    validateSignerHarness(e1, salt1, signature, signer1);
    validateSignerHarness@withrevert(e2, salt2, signature, signer2);

    assert (salt1 == salt2 && signer1 == signer2) => !lastReverted,
        "Revert characteristics of validateSigner are not consistent";
}

// [1] Revert when price in latestRoundData() less than zero
rule latestRoundDataPriceShouldBeGTzero(env e, address dataStore, address token) {

    require(getPriceFeedAddress(dataStore, token) == _PriceFeedA);

    uint80 roundID;
    int256 _price;
    uint256 startedAt;
    uint256 timestamp;
    uint80 answeredInRound;
    roundID, _price, startedAt, timestamp, answeredInRound = _PriceFeedA.latestRoundData(e);

    getPriceFeedPriceHarness@withrevert(e, dataStore, token);
    bool reverted = lastReverted;

    assert(_price <= 0 => reverted);
}

rule validatePricesBasicResultChecks(env e, uint256 index) {

    address[] myTokens = myTokensArray();
    uint256 myTokensLength = myTokensLength();
    uint256 maxPriceAge = getMaxPriceAge();

    setupValidateParams(e);
    require(myTokensLength < MAX_ARRAY_LENGTH());
    require(index < myTokensLength);

    uint256 length; address token; uint256 min; uint256 max; uint256 timestamp; uint256 minBlockNumber; uint256 maxBlockNumber;
    length, token, min, max, timestamp, minBlockNumber, maxBlockNumber = validatePricesHarness@withrevert(e, index);
    bool reverted = lastReverted;

    assert(!reverted => (
        length == myTokensLength
        && token == myTokens[index]
        && min != 0 && max != 0 && min <= max
        && require_uint256(timestamp + maxPriceAge) >= e.block.timestamp
        && minBlockNumber <= maxBlockNumber
        ));

    assert((min == 0 || max == 0 || min > max 
        || (require_uint256(timestamp + maxPriceAge) < e.block.timestamp) 
        || (minBlockNumber > maxBlockNumber)
        ) => reverted
    );
}

// block numbers must be in ascending order
rule validatePricesBlockNumberInAscendingOrder(env e, uint256 index, uint256 indexPrev) {
    
    setupValidateParams(e);

    require(index > 0 && indexPrev > 0);
    require(index < myTokensLength());
    require(indexPrev == require_uint256(index - 1));

    uint256[] minBlockNumber = validatePricesMinBlockNumberArrayHarness@withrevert(e);

    assert(!lastReverted => minBlockNumber[index] >= minBlockNumber[indexPrev]);
    assert(minBlockNumber[index] < minBlockNumber[indexPrev] => lastReverted);
}

rule latestRoundDataTimestampCorrectness(env e, address dataStore, address token) {

    require(getPriceFeedAddress(dataStore, token) == _PriceFeedA);

    uint80 roundID;
    int256 _price;
    uint256 startedAt;
    uint256 timestamp;
    uint80 answeredInRound;
    roundID, _price, startedAt, timestamp, answeredInRound = _PriceFeedA.latestRoundData(e);

    uint256 heartbeatDuration = getHeartbeatDuration(dataStore, token);

    getPriceFeedPriceHarness@withrevert(e, dataStore, token);
    bool reverted = lastReverted;

    assert(e.block.timestamp > timestamp && assert_uint256(e.block.timestamp - timestamp) > heartbeatDuration => reverted);
}

// [] only CONTROLLER could modify state
rule onlyControllerCouldModifyState(env e, method f, calldataarg args) filtered {
    f -> !PURE_VIEW_FUNCTIONS(f) && !HARNESS_FUNCTIONS(f)
} {
    bool isController = hasRoleControllerHarness(e.msg.sender);

    storage before = lastStorage;

    f(e, args);

    storage after = lastStorage;

    assert(before[currentContract] != after[currentContract] => isController);
}

// [] tokensWithPrices and primaryPrices should exist simultaneously
invariant primaryPricesExistsOnlyWithTokensWithPrices(address token) ghostPrimaryPricesMin[token] != 0 || ghostPrimaryPricesMax[token] != 0 
    => ghostTokensWithPricesIndexes[addressToBytes32(token)] != 0 filtered { 
    f -> !PURE_VIEW_FUNCTIONS(f) 
    } { 
        preserved {
            requireInvariant setTokensWithPricesInvariant();
        }
    }

// [] getPriceFeedPrice() return (false, 0) when price feed address is not set
rule getPriceFeedPriceReturnZeroWhenZeroPriceFeedAddress(env e, address dataStore, address token) {

    require(getPriceFeedAddress(dataStore, token) == 0);

    bool result;
    uint256 adjustedPrice;
    result, adjustedPrice = getPriceFeedPriceHarness(e, dataStore, token);

    assert(result == false && adjustedPrice == 0);
}

// [] Supports set prices for several tokens
rule setPricesFromPriceFeedsSupportSeveralTokens(env e, address dataStore, address eventEmitter, address[] priceFeedTokens) {

    uint256 index;
    requireInvariant setTokensWithPricesInvariant();
    require(priceFeedTokens.length < MAX_ARRAY_LENGTH());
    require(index < priceFeedTokens.length);

    require(EMPTY_TOKEN_PRICE(priceFeedTokens[index]));

    setPricesFromPriceFeedsHarness(e, dataStore, eventEmitter, priceFeedTokens);

    satisfy(NOT_EMPTY_TOKEN_PRICE(priceFeedTokens[index]));
}

// [] Should not update non-empty price  
rule setPricesFromPriceFeedsRevertWhenSetTwice(env e, address dataStore, address eventEmitter, address[] priceFeedTokens) {

    uint256 index;
    requireInvariant setTokensWithPricesInvariant();
    require(priceFeedTokens.length < MAX_ARRAY_LENGTH());
    require(index < priceFeedTokens.length);

    require(NOT_EMPTY_TOKEN_PRICE(priceFeedTokens[index]));

    setPricesFromPriceFeedsHarness@withrevert(e, dataStore, eventEmitter, priceFeedTokens);

    assert(lastReverted, "Errors.PriceAlreadySet");
}

// [] Should revert with empty feed price  
rule setPricesFromPriceFeedsRevertsWhenEmpty(env e, address dataStore, address eventEmitter, address[] priceFeedTokens) {

    uint256 index;
    requireInvariant setTokensWithPricesInvariant();
    require(priceFeedTokens.length < MAX_ARRAY_LENGTH());
    require(index < priceFeedTokens.length);

    bool result;
    uint256 price;
    result, price = getPriceFeedPriceHarness(e, dataStore, priceFeedTokens[index]);

    setPricesFromPriceFeedsHarness@withrevert(e, dataStore, eventEmitter, priceFeedTokens);

    assert(result == false => lastReverted, "Errors.EmptyPriceFeed");
}

// [] Set correct price from feed or stable
rule setPricesFromPriceFeedsCorrectness(env e, address dataStore, address eventEmitter, address[] priceFeedTokens) {

    requireInvariant setTokensWithPricesInvariant();
    require(priceFeedTokens.length < MAX_ARRAY_LENGTH());

    uint256 index;
    require(index < priceFeedTokens.length);

    address token;
    require(token == priceFeedTokens[index]);

    require(EMPTY_TOKEN_PRICE(token));

    bool result;
    uint256 price;
    result, price = getPriceFeedPriceHarness(e, dataStore, token);

    uint256 stablePrice = getStablePrice(e, dataStore, token);

    setPricesFromPriceFeedsHarness(e, dataStore, eventEmitter, priceFeedTokens);

    assert(stablePrice > 0 
        ? ghostPrimaryPricesMin[token] == (price < stablePrice ? price : stablePrice)
            && ghostPrimaryPricesMax[token] == (price < stablePrice ? stablePrice : price)
        : ghostPrimaryPricesMin[token] == price && ghostPrimaryPricesMax[token] == price
    );
}

// [] Should not update non-empty price  
rule setPricesRevertWhenSetTwice(env e, address dataStore, address eventEmitter, OracleUtils.SetPricesParams params) {

    setupValidateParams(e);
    require(ghostTokensWithPricesLength != 0);

    setPrices@withrevert(e, dataStore, eventEmitter, params);

    assert(lastReverted, "Errors.NonEmptyTokensWithPrices");
}

// [] Could set correct price
rule setPrimaryPricePossibility(env e, address token, uint256 min, uint256 max) {

    require(token != 0);
    require(min != 0 && max != 0);

    require(EMPTY_TOKEN_PRICE(token));

    setPrimaryPriceHarness(e, token, min, max);

    satisfy(
        ghostTokensWithPricesIndexes[addressToBytes32(token)] != 0
        && ghostPrimaryPricesMin[token] == min 
        && ghostPrimaryPricesMax[token] == max
    );
}

// [] All prices should be cleared 
rule clearAllPricesShouldRemovePrice(env e) {
    
    requireInvariant setTokensWithPricesInvariant();
    require(ghostTokensWithPricesLength != 0);

    address token;
    require(NOT_EMPTY_TOKEN_PRICE(token));

    clearAllPrices(e);

    assert(ghostTokensWithPricesLength == 0 && EMPTY_TOKEN_PRICE(token));
}

// integrity

rule getPriceFeedPriceIntegrity(env e, address dataStore, address token) {
    
    require(getPriceFeedAddress(dataStore, token) == _PriceFeedA);

    uint80 roundID;
    int256 _price;
    uint256 startedAt;
    uint256 timestamp;
    uint80 answeredInRound;
    roundID, _price, startedAt, timestamp, answeredInRound = _PriceFeedA.latestRoundData(e);
    require(_price > 0);
    require(e.block.timestamp == timestamp);

    bool result;
    uint256 price;
    result, price = getPriceFeedPriceHarness(e, dataStore, token);

    assert(result => price == getAdjustedPrice(dataStore, token, _price));
}

rule getPrimaryPriceIntegrity(address token) {

    require(token != 0);

    uint256 min = getPrimaryPriceMinHarness(token);
    uint256 max = getPrimaryPriceMaxHarness(token);

    assert(min == ghostPrimaryPricesMin[token] && max == ghostPrimaryPricesMax[token]);
}

// [] Return zero prices for zero token
rule getPrimaryPriceTokenNotZero(address token) {

    require(token == 0);
    require(ghostPrimaryPricesMin[token] != 0);
    require(ghostPrimaryPricesMax[token] != 0);

    uint256 min = getPrimaryPriceMinHarness(token);
    uint256 max = getPrimaryPriceMaxHarness(token);

    assert(min == 0 && max == 0);
}

// Could not return zero
rule getPriceFeedMultiplierNotZero(env e, address dataStore, address token) {
    assert(getPriceFeedMultiplier(e, dataStore, token) != 0);
}

// [] Revert when empty price
rule getPrimaryPriceRevertWhenEmpty(address token) {

    require(token != 0);

    require(ghostPrimaryPricesMin[token] == 0 || ghostPrimaryPricesMax[token] == 0);
    require(ghostPrimaryPricesMin[token] != ghostPrimaryPricesMax[token]);

    getPrimaryPriceMinHarness@withrevert(token);

    assert(lastReverted);
}

rule getTokensWithPricesCountIntegrity() {
    assert(getTokensWithPricesCount() == ghostTokensWithPricesLength);
}

rule getTokensWithPricesIntegrity(uint256 start, uint256 end) {

    requireInvariant setTokensWithPricesInvariant();

    require(end < ghostTokensWithPricesLength);
    require(start < end);

    uint256 i;
    require(i < assert_uint256(end - start));

    address[] a = getTokensWithPrices(start, end);
    assert(a[i] == bytes32ToAddress(ghostTokensWithPricesValues[start + i]));
}

// possibility

rule getPrimaryPricePossibility(address token) {

    uint256 min = getPrimaryPriceMinHarness(token);
    uint256 max = getPrimaryPriceMaxHarness(token);

    satisfy(min == ghostPrimaryPricesMin[token] && max == ghostPrimaryPricesMax[token]);
}

rule getTokensWithPricesCountPossibility() {
    satisfy(getTokensWithPricesCount() == ghostTokensWithPricesLength);
}

rule getPriceFeedMultiplierPossibility(env e, address dataStore, address token) {
    satisfy(getPriceFeedMultiplier(e, dataStore, token) != 0);
}

rule notRevertedPossibility(env e, method f, calldataarg args) filtered {
    f -> !HARNESS_FUNCTIONS(f)
} {
    f@withrevert(e, args);
    satisfy(!lastReverted); 
}

using RoleStore as ROLE_STORE;
using DataStore as DATA_STORE;
using EventEmitter as EVENT_EMITTER;
using PriceFeedA as PRICE_FEED_A;
using OracleStore as ORACLE_STORE;

// author: neumoxx
methods {
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
    /// Chain
    function _.arbBlockNumber() external => ghostBlockNumber() expect uint256 ALL;
    function _.arbBlockHash(uint256 blockNumber) external => ghostBlockHash(blockNumber) expect bytes32 ALL;
    function _.currentTimestamp() internal => ALWAYS(100000);
    function _.currentBlockNumber() internal => ALWAYS(1000);

    /// Oracle summaries
    function Oracle._getSalt() internal returns bytes32 => mySalt();
    function OracleUtils.validateSigner(bytes32, OracleUtils.ReportInfo memory, bytes memory, address) internal => NONDET;
    function OracleUtils.getUncompactedOracleBlockNumber(uint256[] memory, uint256) internal returns(uint256) => NONDET;
    function OracleUtils.getUncompactedOracleTimestamp(uint256[] memory, uint256) internal returns(uint256) => NONDET;
    function OracleUtils.getUncompactedDecimal(uint256[] memory, uint256) internal returns(uint256) => NONDET;
    function OracleUtils.getUncompactedPrice(uint256[] memory, uint256) internal returns(uint256) => NONDET;
    function OracleUtils.getUncompactedPriceIndex(uint256[] memory, uint256) internal returns(uint256) => NONDET;

    /// Getters:
    function OracleHarness.primaryPrices(address) external returns (uint256,uint256);
    function OracleHarness.secondaryPrices(address) external returns (uint256,uint256);
    function OracleHarness.customPrices(address) external returns (uint256,uint256);
    function OracleHarness.getSignerByInfo(uint256, uint256) external returns (address);
    function OracleHarness.MAX_SIGNERS() external returns (uint256) envfree;
    function OracleHarness.MAX_SIGNER_INDEX() external returns (uint256) envfree;

    /// Harness
    function hasRoleWrapper(bytes32) external returns (bool);
    function hasControllerRole() external returns (bool);
    function getPriceFeedAddress() external returns (address) envfree;
    function getTokensWithPricesLength() external returns (uint256);
    function getTokenAt(uint256) external returns (address) envfree;
    function getSigners(OracleUtils.SetPricesParams) external returns (address[]) envfree;
    function getMinOracleSigners() external returns (uint256) envfree;
    function validateRefPriceExternal(address, uint256, uint256, uint256) external envfree;
    function removePrimaryPriceExternal(address) external;
    function tokensWithPricesContains(address) external returns (bool) envfree;
    function getPriceFeedPriceExternal(address) external returns (bool, uint256);
    function setPricesFromPriceFeedsExternal(address, address[]) external;
}


// DEFINITIONS

// @notice: Functions defined in harness contract
definition notHarnessCall(method f) returns bool =
    (/*&& f.selector != sig:prepareParams(uint256, address[], uint256[], uint256[], uint256[], uint256[],
            uint256[], uint256[], uint256[], uint256[], bytes[], address[]).selector
    && f.selector != sig:prepareParamsSingle(uint256, address, uint256, uint256, uint256, uint256,
            uint256, uint256, uint256, uint256, bytes, address).selector
    && f.selector != sig:prepareParamsDouble(uint256, uint256, address, address, uint256, uint256,
            uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256,
            uint256, uint256, uint256, uint256, bytes, bytes, address, address).selector*/
    f.selector != sig:validateSignerHarness(bytes32, bytes, address).selector
    && f.selector != sig:getSignerByInfo(uint256, uint256).selector
    && f.selector != sig:hasRoleWrapper(bytes32).selector
    && f.selector != sig:hasControllerRole().selector
    && f.selector != sig:getPriceFeedAddress().selector
    && f.selector != sig:getTokensWithPricesLength().selector
    && f.selector != sig:getTokenAt(uint256).selector
    && f.selector != sig:getHeartbeatDurationFromDataStore(address).selector
    && f.selector != sig:getStablePriceFromDataStore(address).selector
    && f.selector != sig:getPriceFeedMultiplierFromDataStore(address).selector
    && f.selector != sig:getMinOracleSigners().selector
    && f.selector != sig:validateRefPriceExternal(address, uint256, uint256, uint256).selector
    && f.selector != sig:removePrimaryPriceExternal(address).selector
    && f.selector != sig:tokensWithPricesContains(address).selector
    && f.selector != sig:getPriceFeedPriceExternal(address).selector
    && f.selector != sig:setPricesFromPriceFeedsExternal(address, address[]).selector);


// FUNCTIONS

function ghostMedian(uint256[] array) returns uint256 {
    uint256 med;
    uint256 len = array.length;
    require med >= array[0] && med <= array[require_uint256(len-1)];
    return med;
}

function constrainSetPricesParams(OracleUtils.SetPricesParams params, address token1) {

    require token1 > 0;

    require params.compactedMinOracleBlockNumbers.length == 1;
    require params.compactedMaxOracleBlockNumbers.length == 1;
    require params.compactedOracleTimestamps.length == 1;
    require params.compactedDecimals.length == 1;
    require params.compactedMinPrices.length == 1;
    require params.compactedMinPricesIndexes.length == 1;
    require params.compactedMaxPrices.length == 1;
    require params.compactedMaxPricesIndexes.length == 1;

}

function constrainEmptySetPricesParams(OracleUtils.SetPricesParams params) {

    require params.signerInfo == 0;
    require params.tokens.length == 0;
    require params.compactedMinOracleBlockNumbers.length == 0;
    require params.compactedMaxOracleBlockNumbers.length == 0;
    require params.compactedOracleTimestamps.length == 0;
    require params.compactedDecimals.length == 0;
    require params.compactedMinPrices.length == 0;
    require params.compactedMinPricesIndexes.length == 0;
    require params.compactedMaxPrices.length == 0;
    require params.compactedMaxPricesIndexes.length == 0;
    require params.signatures.length == 0;
    require params.priceFeedTokens.length == 0;

}


// RULES

// @notice: Consistency check for the execution of function validateSigner
rule validateSignerConsistencyCheck() {
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


// @notice: Consistency check for the execution of function setPrices
rule setPricesConsistencyCheck1() {
    env e;

    bytes32 salt1;
    bytes32 salt2;
    address signer1;
    address signer2;
    bytes signature;

    OracleUtils.SetPricesParams params;
    constrainEmptySetPricesParams(params);

    setPrices@withrevert(e, DATA_STORE, EVENT_EMITTER, params);
    bool lastRev = lastReverted;

    uint80 roundID;
    int256 price;
    uint256 startedAt;
    uint256 timestamp;
    uint80 answeredInRound;

    assert (!hasControllerRole(e)) => lastRev,
        "Revert characteristics of setPrices are not consistent";
}

/*
// @notice: Consistency check for the execution of function setPrices
rule setPricesConsistencyCheck2() {
    env e;

    bytes32 salt1;
    bytes32 salt2;
    address signer1;
    address signer2;
    bytes signature;

    requireInvariant tokensWithPricesEnumerableSetInvariant();

    OracleUtils.SetPricesParams params;
    constrainEmptySetPricesParams(params);

    setPrices@withrevert(e, DATA_STORE, EVENT_EMITTER, params);
    bool lastRev = lastReverted;

    assert (tokensWithPricesGhostLength > 0) => lastRev,
        "Revert characteristics of setPrices are not consistent";
}
*/


// @notice: Consistency check for the execution of function setPrimaryPrice
rule setPrimaryPriceConsistencyCheck() {

    env e;

    address token;
    uint256 minToken;
    uint256 maxToken;
    uint256 minTokenPost;
    uint256 maxTokenPost;
    bool isController = hasControllerRole(e);

    Price.Props props;

    require props.min == minToken;
    require props.max == maxToken;

    setPrimaryPrice@withrevert(e, token, props);
    bool lastRev = lastReverted;

    minTokenPost, maxTokenPost = primaryPrices(e, token);

    assert (e.msg.value > 0 || !isController) <=> lastRev;
    assert !lastRev => minToken == minTokenPost && maxToken == maxTokenPost;

}


// @notice: Consistency check for the execution of function clearAllPrices
rule clearAllPricesConsistencyCheck() {

    env e;

    require getTokensWithPricesLength(e) == 1;

    address token1;

    require token1 == getTokenAt(0);

    bool isController = hasControllerRole(e);

    uint256 minToken1Pre;
    uint256 maxToken1Pre;
    minToken1Pre, maxToken1Pre = primaryPrices(e, token1);

    require (minToken1Pre > 0 && maxToken1Pre > 0);

    clearAllPrices@withrevert(e);
    bool lastRev = lastReverted;

    uint256 minToken1Post;
    uint256 maxToken1Post;
    minToken1Post, maxToken1Post = primaryPrices(e, token1);

    assert (e.msg.value > 0 || !isController) => lastRev;
    assert !lastRev => (minToken1Post == 0 && maxToken1Post == 0);
}


// @notice: Consistency check for the execution of function getTokensWithPricesCount
rule getTokensWithPricesCountConsistencyCheck() {

    env e;

    uint256 length = getTokensWithPricesCount@withrevert(e);
    bool lastRev = lastReverted;

    assert (e.msg.value > 0) <=> lastRev;
    assert length == getTokensWithPricesCount(e);
}


// @notice: Consistency check for the execution of function getTokensWithPrices
rule getTokensWithPricesConsistencyCheck() {

    env e;

    address token1;

    require getTokensWithPricesLength(e) == 1;
    require token1 == getTokenAt(0);

    address[] tokens = getTokensWithPrices@withrevert(e, 0, 1);
    bool lastRev = lastReverted;

    assert (e.msg.value > 0) => lastRev;
    assert !lastRev => tokens.length == 1 && tokens[0] == token1;

}


// @notice: Consistency check for the execution of function getPrimaryPrice
rule getPrimaryPriceConsistencyCheck() {

    env e;

    address token;

    uint256 minTokenPre;
    uint256 maxTokenPre;

    minTokenPre, maxTokenPre = primaryPrices(e, token);

    Price.Props props = getPrimaryPrice@withrevert(e, token);

    bool lastRev = lastReverted;

    assert (e.msg.value > 0 || (token != 0 && (minTokenPre == 0 || maxTokenPre == 0))) <=> lastRev;
    assert !lastRev => (token == 0 <=> (props.min == 0 && props.max == 0));
    assert (!lastRev && token != 0) => (minTokenPre == props.min && maxTokenPre == props.max);

}


// @notice: Consistency check for the execution of function getStablePrice
rule getStablePriceConsistencyCheck() {

    env e;
    address token;

    uint256 res = getStablePrice@withrevert(e, DATA_STORE, token);
    bool lastRev = lastReverted;

    assert (e.msg.value > 0) => lastRev;
    assert !lastRev => getStablePriceFromDataStore(e, token) == res;
}


// @notice: Consistency check for the execution of function getPriceFeedMultiplier
rule getPriceFeedMultiplierConsistencyCheck() {

    env e;
    address token;

    uint256 multiplierPre = getPriceFeedMultiplierFromDataStore(e, token);

    uint256 res = getPriceFeedMultiplier@withrevert(e, DATA_STORE, token);
    bool lastRev = lastReverted;

    assert (e.msg.value > 0 || multiplierPre == 0) => lastRev;
    assert !lastRev =>  multiplierPre == res;
}

/*
// @notice: Consistency check for the execution of function validatePrices
rule validatePricesConsistencyCheck() {

    env e;
    address token1;

    require getTokensWithPricesLength(e) == 1;
    require token1 == getTokenAt(0);

    OracleUtils.SetPricesParams params;
    constrainSetPricesParams(params, token1);


    require params.tokens.length == 0; // we only test _setPricesFromPriceFeeds
    // extra constraints to avoid timeouts
    require params.compactedMinOracleBlockNumbers[0] == require_uint256(e.block.number - 1);
    require params.compactedMaxOracleBlockNumbers[0] == require_uint256(e.block.number + 1);
    require params.compactedOracleTimestamps[0] == require_uint256(e.block.timestamp - 1000);
    require params.compactedMinPrices[0] == 10^18;
    require params.compactedMaxPrices[0] == 10^20;
    require params.compactedDecimals[0] == 18;
    require params.compactedMinPricesIndexes[0] == 0;
    require params.compactedMaxPricesIndexes[0] == 0;
    require params.priceFeedTokens.length == 0;
    require params.signatures.length == 0;

    require getMinOracleSigners() == 0;
    require params.signerInfo == 0; // This is to harcode signers to 0 signers

    Oracle.ValidatedPrice[] prices = validatePrices@withrevert(e, DATA_STORE, params);
    bool lastRev = lastReverted;

    assert (e.msg.value > 0) => lastRev;
    assert !lastRev =>  (
      prices.length == 1 &&
      prices[0].token == token1
    );
}
*/


// @notice: Consistency check for the execution of function getSigners
rule getSignersConsistencyCheck() {

    env e;
    address token1;

    require getTokensWithPricesLength(e) == 1;
    require token1 == getTokenAt(0);

    uint256 signerInfo;
    uint256 signersLength = signerInfo & 0x000000000000000000000000000000000000000000000000000000000000ffff;
    uint256 signerIndex0 = (signerInfo >> 16) & 0x000000000000000000000000000000000000000000000000000000000000ffff;
    uint256 signerIndex1 = (signerInfo >> 32) & 0x000000000000000000000000000000000000000000000000000000000000ffff;

    require signersLength <= 2;

    OracleUtils.SetPricesParams params;
    constrainSetPricesParams(params, token1);

    require params.tokens.length == 0 || params.tokens.length == 1;
    require params.tokens.length == 1 => params.tokens[0] == token1;
    require params.priceFeedTokens.length == 1;
    require params.priceFeedTokens[0] == token1;
    require params.signatures.length == 1;

    require params.signerInfo == signerInfo;

    address[] signers = getSigners@withrevert(params);
    bool lastRev = lastReverted;

    assert (
      signersLength < getMinOracleSigners() ||
      signersLength > MAX_SIGNERS() ||
      (signersLength > 0 && (signerIndex0 >= MAX_SIGNER_INDEX() || ORACLE_STORE.getSigner(e, signerIndex0) == 0)) ||
      (signersLength == 2 && (signerIndex1 >= MAX_SIGNER_INDEX() || ORACLE_STORE.getSigner(e, signerIndex1) == 0)) ||
      (signersLength == 2 && signerIndex0 == signerIndex1)
    ) => lastRev;
    assert !lastRev =>  (
      signers.length == signersLength &&
      signersLength > 0 => ORACLE_STORE.getSigner(e, signerIndex0) == signers[0] &&
      signersLength == 2 => ORACLE_STORE.getSigner(e, signerIndex1) == signers[1]
    );
}


// @notice: Consistency check for the execution of function validateRefPrice
rule validateRefPriceExternalConsistencyCheck() {

    env e;
    address token;
    uint256 price;
    uint256 refPrice;
    uint256 maxRefPriceDeviationFactor;

    mathint diff = price > refPrice ? price - refPrice : refPrice - price;
    uint256 diffFactor = getDiffFactor(e, assert_uint256(diff), refPrice);

    validateRefPriceExternal@withrevert(token, price, refPrice, maxRefPriceDeviationFactor);
    bool lastRev = lastReverted;

    assert (
      diffFactor > maxRefPriceDeviationFactor ||
      (diff > 0 && refPrice == 0) ||
      //diff * 10 ^ 30 > max_uint256
      diff > 115792090000000000000000000000000000000000000000 // max_uint256 / 10 ^30 = (2^256-1) / 10^30 = 1.1579209e+47
    ) <=> lastRev;
}

// @notice: Consistency check for the execution of function removePrimaryPrice
rule removePrimaryPriceExternalConsistencyCheck() {

    env e;
    address token;

    uint256 minTokenPost;
    uint256 maxTokenPost;

    bool containsTokenPre = tokensWithPricesContains(token);

    removePrimaryPriceExternal@withrevert(e, token);
    bool lastRev = lastReverted;

    minTokenPost, maxTokenPost = primaryPrices(e, token);

    assert (e.msg.value > 0) => lastRev;
    assert !lastRev <=> (minTokenPost == 0 && maxTokenPost == 0 && !tokensWithPricesContains(token));
}

// @notice: Consistency check for the execution of function getPriceFeedPrice
// @notice: Catches bug #2
rule getPriceFeedPriceExternalConsistencyCheck1() {

    env e;
    address token;
    uint80 roundID;
    int256 price;
    uint256 startedAt;
    uint256 timestamp;
    uint80 answeredInRound;
    address feed = getPriceFeedAddress();
    require feed == PRICE_FEED_A;
    require getTokensWithPricesLength(e) == 1;
    require getTokenAt(0) == token;
    require e.block.timestamp == 100000; // We fix this to the return of the summary of the _.currentTimestamp() function

    roundID, price, startedAt, timestamp, answeredInRound = PRICE_FEED_A.latestRoundData(e);

    uint256 heartbeatDuration = getHeartbeatDurationFromDataStore(e, token);
    require heartbeatDuration == 10; // try to avoid timeouts by simplifying

    bool res;
    uint256 priceRes;

    res, priceRes = getPriceFeedPriceExternal@withrevert(e, token);
    bool lastRev = lastReverted;

    assert (
      e.msg.value > 0 ||
      price <= 0 ||
      (e.block.timestamp > timestamp && e.block.timestamp - timestamp > to_mathint(heartbeatDuration))
    ) => lastRev;
}

// @notice: Consistency check for the execution of function getPriceFeedPrice
rule getPriceFeedPriceExternalConsistencyCheck2() {

    env e;
    address token;
    uint80 roundID;
    int256 price;
    uint256 startedAt;
    uint256 timestamp;
    uint80 answeredInRound;
    address feed = getPriceFeedAddress(e, token);
    require feed == PRICE_FEED_A;
    require getTokensWithPricesLength(e) == 1;
    require getTokenAt(0) == token;
    require e.block.timestamp == 100000; // We fix this to the return of the summary of the _.currentTimestamp() function

    roundID, price, startedAt, timestamp, answeredInRound = PRICE_FEED_A.latestRoundData(e);
    require price == 10^21;

    uint256 multiplier = getPriceFeedMultiplierFromDataStore(e, token);
    require multiplier == 10^10; // try to avoid timeouts by simplifying

    // mathint expectedPrice = price * multiplier / 10 ^ 30;
    uint256 expectedPrice = 10; // 10^21 * 10^10 / 10^30

    bool res;
    uint256 priceRes;

    res, priceRes = getPriceFeedPriceExternal(e, token);

    assert (
      (feed == 0 => !res && priceRes == 0) &&
      (feed != 0 => res && priceRes == expectedPrice)
    );
}


// @notice: Consistency check for the execution of function setPricesFromPriceFeeds
rule setPricesFromPriceFeedsExternalConsistencyCheck() {

    env e;
    address token;
    address eventEmitter;
    address[] priceFeedTokens;
    require priceFeedTokens.length == 1;
    require priceFeedTokens[0] == token;
    require getTokensWithPricesLength(e) == 1;
    require getTokenAt(0) == token;

    uint256 minPre;
    uint256 maxPre;
    uint256 minPost;
    uint256 maxPost;
    bool hasPriceFeed;
    uint256 price;
    uint256 stablePrice;

    minPre, maxPre = primaryPrices(e, token);
    hasPriceFeed, price = getPriceFeedPriceExternal(e, token);
    stablePrice = getStablePriceFromDataStore(e, token);

    setPricesFromPriceFeedsExternal@withrevert(e, eventEmitter, priceFeedTokens);
    bool lastRev = lastReverted;

    minPost, maxPost = primaryPrices(e, token);

    assert (
      !(minPre == 0 || maxPre == 0) ||
      !hasPriceFeed
    ) => lastRev;
    assert !lastRev => (
      (stablePrice == 0 => minPost == price && maxPost == price) &&
      (stablePrice != 0 => minPost == (
          price < stablePrice ? price : stablePrice) &&
          maxPost == (price < stablePrice ? stablePrice : price
        )
      )
    );
}

// @notice: Min primary price must be less than or equal than max price after any function call (except setPrimaryPrice, see below)
rule minAlwaysLTEMax(method f) filtered {
    f -> (
      notHarnessCall(f) &&
      f.selector != sig:setPrimaryPrice(address, Price.Props).selector
    )
} {

    address token;
    uint256 minPre;
    uint256 maxPre;
    uint256 minPost;
    uint256 maxPost;

    env e;
    calldataarg args;

    minPre, maxPre = primaryPrices(e, token);

    currentContract.f(e, args);

    minPost, maxPost = primaryPrices(e, token);

    assert (minPost != minPre || maxPost != maxPre) => maxPost >= minPost;
}


// @notice Ensure all funtions have at least one non-reverting path
rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}


// GHOSTS

ghost mySalt() returns bytes32;

ghost ghostBlockNumber() returns uint256 {
    axiom ghostBlockNumber() !=0;
}

ghost ghostBlockHash(uint256) returns bytes32 {
    axiom forall uint256 num1. forall uint256 num2.
        num1 != num2 => ghostBlockHash(num1) != ghostBlockHash(num2);
}
/*
// tokensWithPrices

// ghost field for the values array
ghost mapping(mathint => bytes32) tokensWithPricesGhostValues {
    init_state axiom forall mathint x. tokensWithPricesGhostValues[x] == to_bytes32(0);
}
// ghost field for the indexes map
ghost mapping(bytes32 => uint256) tokensWithPricesGhostIndexes {
    init_state axiom forall bytes32 x. tokensWithPricesGhostIndexes[x] == 0;
}
// ghost field for the length of the values array (stored in offset 0)
ghost uint256 tokensWithPricesGhostLength {
    init_state axiom tokensWithPricesGhostLength == 0;
    // assumption: it's infeasible to grow the list to these many elements.
    axiom tokensWithPricesGhostLength < 0xffffffffffffffffffffffffffffffff;
}



// HOOKS
// Store hook to synchronize tokensWithPricesGhostLength with the length of the tokensWithPrices._inner._values array.
// We need to use (offset 0) here, as there is no keyword yet to access the length.

// tokensWithPrices
hook Sstore currentContract.tokensWithPrices.(offset 0) uint256 newLength STORAGE {
    tokensWithPricesGhostLength = newLength;
}
// Store hook to synchronize tokensWithPricesGhostValues array with tokensWithPrices._inner._values.
hook Sstore currentContract.tokensWithPrices._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    tokensWithPricesGhostValues[index] = newValue;
}
// Store hook to synchronize tokensWithPricesGhostIndexes array with tokensWithPrices._inner._indexes.
hook Sstore currentContract.tokensWithPrices._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    tokensWithPricesGhostIndexes[value] = newIndex;
}
hook Sload uint256 length currentContract.tokensWithPrices.(offset 0) STORAGE {
    require tokensWithPricesGhostLength == length;
}
hook Sload bytes32 value currentContract.tokensWithPrices._inner._values[INDEX uint256 index] STORAGE {
    require tokensWithPricesGhostValues[index] == value;
}
hook Sload uint256 index currentContract.tokensWithPrices._inner._indexes[KEY bytes32 value] STORAGE {
    require tokensWithPricesGhostIndexes[value] == index;
}


// INVARIANTS

//  This is the main invariant stating that the indexes and values always match:
//        values[indexes[v] - 1] = v for all values v in the set
//    and indexes[values[i]] = i+1 for all valid indexes i.

invariant tokensWithPricesEnumerableSetInvariant()
    (forall uint256 index. 0 <= index && index < tokensWithPricesGhostLength => to_mathint(tokensWithPricesGhostIndexes[tokensWithPricesGhostValues[index]]) == index + 1)
    && (forall bytes32 value. tokensWithPricesGhostIndexes[value] == 0 ||
         (tokensWithPricesGhostValues[tokensWithPricesGhostIndexes[value] - 1] == value && tokensWithPricesGhostIndexes[value] >= 1 && tokensWithPricesGhostIndexes[value] <= tokensWithPricesGhostLength));
*/

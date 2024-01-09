using DataStore as DATA_STORE;
using EventEmitter as EVENT_EMITTER;

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
    /// Oracle summaries
    function Oracle._getSalt() internal returns bytes32 => mySalt();

    /// Getters:
    function OracleHarness2.primaryPrices(address) external returns (uint256,uint256);
    function OracleHarness2.secondaryPrices(address) external returns (uint256,uint256);
    function OracleHarness2.customPrices(address) external returns (uint256,uint256);
    function OracleHarness2.getSignerByInfo(uint256, uint256) external returns (address);
}


// DEFINITIONS

// @notice: Functions defined in harness contract
definition notHarnessCall(method f) returns bool =
    (f.selector != sig:validateSignerHarness(bytes32, bytes, address).selector
    && f.selector != sig:getSignerByInfo(uint256, uint256).selector);


// FUNCTIONS

function ghostMedian(uint256[] array) returns uint256 {
    uint256 med;
    uint256 len = array.length;
    require med >= array[0] && med <= array[require_uint256(len-1)];
    return med;
}


// RULES

// @notice: Consistency check for the execution of function validatePrices with zero signers and 1 token
rule validatePricesNoSignersOneTokenConsistencyCheck() {

    env e;
    address token1 = 10;

    requireInvariant tokensWithPricesEnumerableSetInvariant();
    require tokensWithPricesGhostLength == 0;

    Oracle.ValidatedPrice[] prices = validatePricesNoSignersOneToken@withrevert(e);
    bool lastRev = lastReverted;

    assert lastReverted;
}

/*
// @notice: Consistency check for the execution of function validatePrices
rule validatePricesConsistencyCheck() {

    env e;
    address token1 = 10;

    requireInvariant tokensWithPricesEnumerableSetInvariant();
    require tokensWithPricesGhostLength == 0;

    OracleUtils.SetPricesParams params;
    require params.signerInfo == 2^16+1;
    require params.tokens.length == 1;
    require params.tokens[0] == token1;

    Oracle.ValidatedPrice[] prices = validatePrices@withrevert(e, DATA_STORE, params);
    bool lastRev = lastReverted;

    uint256 oracleTimestamp = getUncompactedOracleTimestampExternal(e, params.compactedOracleTimestamps, 0);

    assert (e.msg.value > 0) => lastRev;
    assert !lastRev =>  (
      prices.length == 1 &&
      prices[0].token == token1 &&
      prices[0].timestamp == oracleTimestamp
    );
}
*/

// @notice: Consistency check for the execution of function validatePrices with 1 signer and 1 token
rule validatePricesOneSignerOneTokenConsistencyCheck() {

    env e;
    address token1 = 10;

    requireInvariant tokensWithPricesEnumerableSetInvariant();
    require tokensWithPricesGhostLength == 0;

    uint256 maxPriceAge = getMaxOraclePriceAge(e);

    Oracle.ValidatedPrice[] prices = validatePricesOneSignerOneToken@withrevert(e);
    bool lastRev = lastReverted;

    assert (e.msg.value > 0) => lastRev;
    assert !lastRev =>  (
      prices.length == 1 &&
      prices[0].token == token1 &&
      prices[0].min > 0  &&
      prices[0].max > 0 &&
      (prices[0].timestamp + maxPriceAge) < to_mathint(max_uint256)
    );
}

// @notice: Consistency check for the execution of function validatePrices with 1 signer and 2 tokens
rule validatePricesOneSignerTwoTokensConsistencyCheck() {

    env e;
    address token1 = 10;
    address token2 = 20;

    requireInvariant tokensWithPricesEnumerableSetInvariant();
    require tokensWithPricesGhostLength == 0;

    Oracle.ValidatedPrice[] prices = validatePricesOneSignerTwoTokens@withrevert(e);
    bool lastRev = lastReverted;

    assert (e.msg.value > 0) => lastRev;
    assert !lastRev =>  (
      prices.length == 2 &&
      prices[0].token == token1 &&
      prices[1].token == token2 &&
      prices[0].min > 0  &&
      prices[0].max > 0
    );
}


// @notice Ensure all funtions have at least one non-reverting path
rule sanity_satisfy(method f) filtered {
    f -> (
      f.selector != sig:validatePricesNoSignersOneToken().selector &&
      f.selector != sig:validatePricesOneSignerOneToken().selector &&
      f.selector != sig:validatePricesOneSignerTwoTokens().selector
    )
} {
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



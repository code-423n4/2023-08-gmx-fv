
// author: 0xpoolboy
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
    function OracleHarness.primaryPrices(address) external returns (uint256,uint256);
    function OracleHarness.secondaryPrices(address) external returns (uint256,uint256);
    function OracleHarness.customPrices(address) external returns (uint256,uint256);
    function OracleHarness.getSignerByInfo(uint256, uint256) external returns (address);

    function OracleHarness.myPriceFeedTokens() external returns (address[]);
    function OracleHarness.getTokenLength() external returns (uint256) envfree;
    function OracleHarness.getMaxPriceAge() external returns (uint256) envfree;

    function OracleHarness.getPriceFeedMultiplier(address token) external returns (uint256) envfree;
    function OracleHarness.validateRefPriceWrapper(address, uint256, uint256, uint256) external returns (uint256) envfree;

    function OracleHarness.getPrimaryPricesMin(address token) external returns(uint256) envfree;
    function OracleHarness.tokenWithPricesContains(address token) external returns(bool) envfree;

    function OracleUtils.getUncompactedOracleBlockNumber(uint256[] memory, uint256) internal returns (uint256) => NONDET;
    function OracleUtils.getUncompactedOracleTimestamp(uint256[] memory, uint256) internal returns (uint256) => NONDET;
    function OracleUtils.getUncompactedDecimal(uint256[] memory, uint256) internal returns (uint256) => NONDET;
    function OracleUtils.getUncompactedPrice(uint256[] memory, uint256) internal returns (uint256) => NONDET;
    function OracleUtils.getUncompactedPriceIndex(uint256[] memory, uint256) internal returns (uint256) => NONDET;
    function OracleUtils.validateSigner(bytes32, OracleUtils.ReportInfo memory, bytes memory, address) internal => NONDET;
    function _.shouldUseArbSysValues() internal => ALWAYS(false);
}

ghost mySalt() returns bytes32;

ghost ghostBlockNumber() returns uint256 {
    axiom ghostBlockNumber() !=0;
}

ghost ghostBlockHash(uint256) returns bytes32 {
    axiom forall uint256 num1. forall uint256 num2. 
        num1 != num2 => ghostBlockHash(num1) != ghostBlockHash(num2);
}

function ghostMedian(uint256[] array) returns uint256 {
    uint256 med;
    uint256 len = array.length;
    require med >= array[0] && med <= array[require_uint256(len-1)];
    return med;
}

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

//bug3
// from the comments Oracle.sol:31 : zero / negative prices are considered empty / invalid
rule getPriceFeedPriceOnlyReturnsPriceGT0(
    env e,
    address token
) {
    bool hasPriceFeed;
    uint256 price;
    hasPriceFeed, price = getPriceFeedPrice(e, token);
    assert price > 0 <=> hasPriceFeed, "zero or negative prices are considered empty or invalid";
    //assert !hasPriceFeed <=> price == 0;
    //assert (price == 0) <=> !hasPriceFeed;
}

// EnumerableSet.AddressSet internal tokensWithPrices;
ghost mapping(mathint => bytes32) ghostTokensWithPricesValues {
    init_state axiom forall mathint x. ghostTokensWithPricesValues[x] == to_bytes32(0);
}
ghost mapping(bytes32 => uint256) ghostTokensWithPricesIndexes {
    init_state axiom forall bytes32 x. ghostTokensWithPricesIndexes[x] == 0;
}
ghost uint256 ghostTokensWithPricesLength {
    init_state axiom ghostTokensWithPricesLength == 0;
    // assumption: it's infeasible to grow the list to these many elements.
    axiom ghostTokensWithPricesLength < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.tokensWithPrices.(offset 0) uint256 newLength STORAGE {
    ghostTokensWithPricesLength = newLength;
}
hook Sstore currentContract.tokensWithPrices._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostTokensWithPricesValues[index] = newValue;
}
hook Sstore currentContract.tokensWithPrices._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostTokensWithPricesIndexes[value] = newIndex;
}

hook Sload uint256 length currentContract.tokensWithPrices.(offset 0) STORAGE {
    require ghostTokensWithPricesLength == length;
}
hook Sload bytes32 value currentContract.tokensWithPrices._inner._values[INDEX uint256 index] STORAGE {
    require ghostTokensWithPricesValues[index] == value;
}
hook Sload uint256 index currentContract.tokensWithPrices._inner._indexes[KEY bytes32 value] STORAGE {
    require ghostTokensWithPricesIndexes[value] == index;
}

invariant tokensWithPricesSetInvariant()
    (forall uint256 index. 0 <= index && index < ghostTokensWithPricesLength => to_mathint(ghostTokensWithPricesIndexes[ghostTokensWithPricesValues[index]]) == index + 1)
    && (forall bytes32 value. ghostTokensWithPricesIndexes[value] == 0 ||
         (ghostTokensWithPricesValues[ghostTokensWithPricesIndexes[value] - 1] == value && ghostTokensWithPricesIndexes[value] >= 1 && ghostTokensWithPricesIndexes[value] <= ghostTokensWithPricesLength));


invariant tokensWithPricesIsUpToDate(address token)
    //primaryPrices[token] != 0 => tokenWithPrices.contains(token);
    getPrimaryPricesMin(token) != 0 <=> tokenWithPricesContains(token)
    {
        preserved {
            requireInvariant tokensWithPricesSetInvariant;
        }
    }
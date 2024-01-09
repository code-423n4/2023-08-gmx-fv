
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
    function _.latestRoundData() external => CONSTANT;
    //function _.latestRoundData() external => DISPATCHER(true);
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
    function getPriceFeedPriceRaw(address token) external returns(int256) envfree;

    function OracleHarness.myPriceFeedTokens() external returns (address[]);
    function OracleHarness.getTokenLength() external returns (uint256) envfree;
    function OracleHarness.getMaxPriceAge() external returns (uint256) envfree;
    function OracleHarness.getPriceFeedMultiplier(address token) external returns (uint256) envfree;
    function OracleHarness.validateRefPriceWrapper(address, uint256, uint256, uint256) external returns (uint256) envfree;
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

rule sanity_satisfy(method f) filtered {
    f -> f.selector != sig:validatePrices1().selector /*Not used in this spec file*/
} {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

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

rule getPriceFeedPriceOnlyReturnsPriceGT0(
    env e,
    address token
) {
    //uint256 preci = getPriceFeedMultiplier(token);
    //require preci >= 10^30;
    bool hasPriceFeed;
    uint256 price;
    hasPriceFeed, price = getPriceFeedPrice(e, token);
    assert price > 0 => hasPriceFeed;
    //assert !hasPriceFeed <=> price == 0;
    //assert (price == 0) <=> !hasPriceFeed;
}


//bug2
rule getPriceFeedPriceShouldRevertWhenPriceFeedPriceInvalid(
    env e,
    address token
) {
    int rawPrice = getPriceFeedPriceRaw(token);
    bool hasPriceFeed;
    uint256 adjustedPrice;
    hasPriceFeed, adjustedPrice = getPriceFeedPrice(e, token);
    bool getPriceFeedPriceReverted = lastReverted;

    assert (rawPrice <= 0) => getPriceFeedPriceReverted,
        "_getPriceFeedPrice should revert when price is invalid";
}

rule setPrices(
    env e,
    uint256 index
) {
    address token1 = getMyPriceFeedToken(e, 0);
    setPrices(e);
    assert token1 == getMyPriceFeedToken(e, 0);
    //OracleUtils.SetPricesParams params = getParams(e);
    // check for caching issues
    // check not zero

}


//passes
rule priceFeedIsUpToDate(
    env e,
    address token
) {
    uint256 heartbeatDuration = getPriceFeedHeartbeatDuration(e, token);
    uint256 priceFeedPriceTimestamp = getPriceFeedTimestamp(e, token);

    bool hasPriceFeed;
    uint256 price;
    hasPriceFeed, price = getPriceFeedPrice@withrevert(e, token);
    bool getPriceFeedPriceReverted = lastReverted;

    assert (e.block.timestamp > priceFeedPriceTimestamp && e.block.timestamp - priceFeedPriceTimestamp > to_mathint(heartbeatDuration))
        => getPriceFeedPriceReverted;
}

rule validateRefPriceCorrectness(
    address token,
    uint256 price,
    uint256 refPrice,
    uint256 maxRefPriceDeviationFactor
) {
    uint256 diffFactor = validateRefPriceWrapper(token, price, refPrice, maxRefPriceDeviationFactor);

    assert diffFactor <= maxRefPriceDeviationFactor;
}
using DataStore as DataStore;
using OracleStore as OracleStore;

// author: jokrhub
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
    /// Key summaries
    function Keys.priceFeedKey(address) internal returns bytes32 => CONSTANT;
    function Keys.priceFeedHeartbeatDurationKey(address) internal returns bytes32 => CONSTANT;

    /// Getters:
    function OracleHarness.primaryPrices(address) external returns (uint256,uint256);
    function OracleHarness.secondaryPrices(address) external returns (uint256,uint256);
    function OracleHarness.customPrices(address) external returns (uint256,uint256);
    function OracleHarness.getSignerByInfo(uint256, uint256) external returns (address);

    /// Envfree
    function getPrimaryPrice(address) external returns (Price.Props) envfree;
    function setPrimaryPrice(address, Price.Props) external envfree;

    /// Harness
    function getPrimaryPriceHarness(address) external returns (Price.Props) envfree;
    function setContainsHarness(address) external returns (bool) envfree;
    function setLengthHarness() external returns (uint256) envfree;

    function getMyTokens() external returns (address[]) envfree;
    function castToUint256(int256) external returns (uint256) envfree;
    function mulDiv(uint256 price, uint256 precision, uint256 float_precision) external returns (uint256) envfree;
    function getPriceFeedKey(address token) external returns (bytes32) envfree;
    function getPriceFeedHeartbeatDurationKey(address token) external returns (bytes32) envfree;
    function getPriceFeedMultiplierKey(address token) external returns (bytes32) envfree;
    function getTokensWithPricesCount() external returns (uint256) envfree;
    function getTokensWithPrices(uint256 start, uint256 end) external returns (address[]) envfree;
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

rule setPrimaryPriceUnitTest(env e, address token, Price.Props price) {
    require setLengthHarness() == 0;
    setPrimaryPrice(token, price);
    Price.Props expectedPrice = getPrimaryPrice(token);
    bool tokenExists = setContainsHarness(token);
    assert token == 0 => expectedPrice.min == 0 && expectedPrice.max == 0;
    assert token != 0 => expectedPrice.min == price.min && expectedPrice.max == price.max;
    assert tokenExists == true;   

    // assert(isControllerHarness(e));
}

rule getPrimaryPriceShouldRevert(address token) {
    Price.Props price = getPrimaryPriceHarness(token);
    getPrimaryPrice@withrevert(token);
    assert token != 0 && (price.min == 0 || price.max == 0) <=> lastReverted;
}

rule setPricesVerify (env e ) {
    address[] tokens = getMyTokens();
    address token = tokens[0];
    Oracle.ValidatedPrice[] validatedPrices = validatePricesHarness(e);
    Oracle.ValidatedPrice validatedPrice = validatedPrices[0];

    address[] priceFeedTokens = getMyPriceFeedTokens(e);
    require priceFeedTokens.length == 1;
    address priceToken = priceFeedTokens[0];

    bool hasPriceFeed; uint256 price;
    hasPriceFeed, price = getPriceFeedPriceHarness(e, priceToken);
    
    uint256 stablePrice = getStablePrice(e, DataStore, priceToken);

    setPricesVerifyHarness(e);

    Price.Props expectedPrice = getPrimaryPrice(token);
    Price.Props expectedPriceToken = getPrimaryPrice(priceToken);

    uint256 minPrice; uint256 maxPrice;
    if (price < stablePrice) {
        minPrice = price;
        maxPrice = stablePrice;
    }
    else {
        minPrice = stablePrice;
        maxPrice = price;
    }

    assert token != 0 => expectedPrice.min ==  validatedPrice.min && expectedPrice.max == validatedPrice.max;
    assert tokens.length != 0 && priceToken != 0 && stablePrice > 0 => expectedPriceToken.min == minPrice && expectedPriceToken.max == maxPrice;
    // assert(isControllerHarness(e));
}

rule setPricesVerifyShouldRevert(env e) {
    uint256 length = tokenWithPricesLength(e);
    setPricesVerifyHarness@withrevert(e);
    assert length != 0 => lastReverted;
}


rule setPricesUnitTest(env e) {

    address[] tokens = getMyTokens();
    address token = tokens[0];
    Oracle.ValidatedPrice[] validatedPrices = validatePricesHarness(e);
    Oracle.ValidatedPrice validatedPrice = validatedPrices[0];

    setPricesHarness(e);

    Price.Props expectedPrice = getPrimaryPrice(token);
    
    assert token == 0 => expectedPrice.min == 0 && expectedPrice.max == 0;
    assert token != 0 => expectedPrice.min ==  validatedPrice.min && expectedPrice.max == validatedPrice.max;

}

rule setPricesUnitTestMulti (env e) {
    address[] tokens = getMyTokens();
    address token = tokens[0];
    address tokenMul = tokens[1];
    Oracle.ValidatedPrice[] validatedPrices = validatePricesHarness(e);
    Oracle.ValidatedPrice validatedPrice = validatedPrices[0];
    Oracle.ValidatedPrice validatedPriceMul = validatedPrices[1];

    setPricesMultiHarness(e);

    Price.Props expectedPrice = getPrimaryPrice(token);
    Price.Props expectedPriceMul = getPrimaryPrice(tokenMul);
    
    assert token == 0 => expectedPrice.min == 0 && expectedPrice.max == 0;
    assert token != 0 => expectedPrice.min ==  validatedPrice.min && expectedPrice.max == validatedPrice.max;
    assert tokenMul == 0 => expectedPriceMul.min == 0 && expectedPriceMul.max == 0;
    assert tokenMul != 0 => expectedPriceMul.min ==  validatedPriceMul.min && expectedPriceMul.max == validatedPriceMul.max;
}

rule setPricesShouldRevert(env e) {
    Oracle.ValidatedPrice[] validatedPrices = validatePricesHarness(e);
    Oracle.ValidatedPrice validatedPrice = validatedPrices[0];
    bool isEmpty = isEmptyHarness(e, getPrimaryPriceHarness(validatedPrice.token));

    setPricesHarness@withrevert(e);

    assert !isEmpty => lastReverted;
}


rule setPricesFromPriceFeedsUnitTest (env e, address[] priceFeedTokens) {
    require priceFeedTokens.length == 1;
    address token = priceFeedTokens[0];

    bool hasPriceFeed; uint256 price;
    hasPriceFeed, price = getPriceFeedPriceHarness(e, token);
    
    uint256 stablePrice = getStablePrice(e, DataStore, token);

    setPricesFromPriceFeedsHarness(e, priceFeedTokens);

    Price.Props expectedPrice = getPrimaryPrice(token);
    
    uint256 minPrice; uint256 maxPrice;
    if (price < stablePrice) {
        minPrice = price;
        maxPrice = stablePrice;
    }
    else {
        minPrice = stablePrice;
        maxPrice = price;
    }

    assert token == 0 => expectedPrice.min == 0 && expectedPrice.max == 0;
    assert token != 0 && stablePrice > 0 => expectedPrice.min == minPrice && expectedPrice.max == maxPrice;
    assert token != 0 && stablePrice <= 0 => expectedPrice.min == price && expectedPrice.max == price;
}

rule setPricesFromPriceFeedsUnitTestMulti (env e, address[] priceFeedTokens) {
    require priceFeedTokens.length == 2;
    address token = priceFeedTokens[0];
    address tokenMul = priceFeedTokens[1];

    bool hasPriceFeed; uint256 price;
    hasPriceFeed, price = getPriceFeedPriceHarness(e, token);
    
    uint256 stablePrice = getStablePrice(e, DataStore, token);


    bool hasPriceFeedMul; uint256 priceMul;
    hasPriceFeedMul, priceMul = getPriceFeedPriceHarness(e, tokenMul);
    
    uint256 stablePriceMul = getStablePrice(e, DataStore, tokenMul);


    setPricesFromPriceFeedsHarness(e, priceFeedTokens);

    Price.Props expectedPrice = getPrimaryPrice(token);
    Price.Props expectedPriceMul = getPrimaryPrice(tokenMul);
    
    uint256 minPrice; uint256 maxPrice;
    if (price < stablePrice) {
        minPrice = price;
        maxPrice = stablePrice;
    }
    else {
        minPrice = stablePrice;
        maxPrice = price;
    }


    uint256 minPriceMul; uint256 maxPriceMul;
    if (priceMul < stablePriceMul) {
        minPriceMul = priceMul;
        maxPriceMul = stablePriceMul;
    }
    else {
        minPriceMul = stablePriceMul;
        maxPriceMul = priceMul;
    }


    assert token == 0 => expectedPrice.min == 0 && expectedPrice.max == 0;
    assert token != 0 && stablePrice > 0 => expectedPrice.min == minPrice && expectedPrice.max == maxPrice;
    assert token != 0 && stablePrice <= 0 => expectedPrice.min == price && expectedPrice.max == price;

    assert tokenMul == 0 => expectedPriceMul.min == 0 && expectedPriceMul.max == 0;
    assert tokenMul != 0 && stablePriceMul > 0 => expectedPriceMul.min == minPriceMul && expectedPriceMul.max == maxPriceMul;
    assert tokenMul != 0 && stablePriceMul <= 0 => expectedPriceMul.min == priceMul && expectedPriceMul.max == priceMul;
}

rule setPricesFromPriceFeedsShouldRevert (env e, address[] priceFeedTokens) {
    require priceFeedTokens.length == 1;
    address token = priceFeedTokens[0];
    bool isEmpty = isEmptyHarness(e, getPrimaryPriceHarness(token));

    bool hasPriceFeed; uint256 price;
    hasPriceFeed, price = getPriceFeedPriceHarness(e, token);

    setPricesFromPriceFeedsHarness@withrevert(e, priceFeedTokens);

    assert !isEmpty => lastReverted;
    assert !hasPriceFeed => lastReverted;

}


rule getPriceFeedPriceUnitTest(env e, address token) {
    bytes32 _priceFeedKey = getPriceFeedKey(token);
    address priceFeedAddress = DataStore.getAddress(e, _priceFeedKey);

    int256 _price; uint256 timestamp;
    _price, timestamp = getLatestRoundData(e, priceFeedAddress);

    bytes32 _priceFeedHeartbeatDurationKey = getPriceFeedHeartbeatDurationKey(token);
    uint256 heartbeatDuration = DataStore.getUint(e, _priceFeedHeartbeatDurationKey);
    uint256 price = castToUint256(_price);
    uint256 precision = getPriceFeedMultiplier(e, DataStore, token);

    uint256 adjustedPrice = mulDiv(price, precision, 10 ^ 30);

    bool success; uint256 expectedPrice;
    success, expectedPrice = getPriceFeedPriceHarness(e, token);

    assert success == true && adjustedPrice == expectedPrice;
}

rule getPriceFeedPriceShouldRevert(env e, address token) {
    bytes32 _priceFeedKey = getPriceFeedKey(token);
    address priceFeedAddress = DataStore.getAddress(e, _priceFeedKey);

    int256 _price; uint256 timestamp;
    _price, timestamp = getLatestRoundData(e, priceFeedAddress);

    bytes32 _priceFeedHeartbeatDurationKey = getPriceFeedHeartbeatDurationKey(token);
    uint256 heartbeatDuration = DataStore.getUint(e, _priceFeedHeartbeatDurationKey);
    
    uint256 currentTimestamp = getCurrentTimestamp(e);    

    getPriceFeedPriceHarness@withrevert(e, token);

    assert (
        (_price <= 0) || 
        (currentTimestamp > timestamp && assert_uint256(currentTimestamp - timestamp) > heartbeatDuration)
    ) 
    => lastReverted;
}

rule clearAllPricesUnitTest (env e) {
    require getTokensWithPricesCount() == 2;
    address[] tokens = getTokensWithPrices(0, 2);
    assert setContainsHarness(tokens[0]) == false;
    assert setContainsHarness(tokens[1]) == false;

    // assert(isControllerHarness(e));
}

rule getPriceFeedMultiplierUnitTest(env e, address token) {
    bytes32 key = getPriceFeedMultiplierKey(token);
    uint256 multiplier = DataStore.getUint(e, key);

    uint256 expectedMultiplier = getPriceFeedMultiplier@withrevert(e, DataStore, token);

    assert !lastReverted => expectedMultiplier == multiplier;
    assert multiplier == 0 <=> lastReverted;
}

rule getSignersUnitTest (env e) {

    uint256 signerInfo = mySignerInfo(e);
    uint256 singerIndex0 = getSignerIndex(e, signerInfo, 0);
    address signer0 = OracleStore.getSigner(e, singerIndex0);
    address[] expectedSigners =  getSignersHarness(e);

    assert expectedSigners[0] == signer0;
}

// rule getSignersUnitTestMulti (env e) {

//     uint256 signerInfo = mySignerInfo(e);
//     uint256 singerIndex0 = getSignerIndex(e, signerInfo, 0);
//     address signer0 = OracleStore.getSigner(e, singerIndex0);
//     address[] expectedSigners =  getSignersHarness(e);

//     assert expectedSigners[0] == signer0;
// }

//@todo why is this not working
rule getSignersShouldRevert (env e) {

    uint256 signerInfo = mySignerInfo(e);
    uint256 signersCount = getSignersCount(e, signerInfo);
    uint256 singerIndex0 = getSignerIndex(e, signerInfo, 0);
    address signer0 = OracleStore.getSigner(e, singerIndex0);

    uint256 MAX_SIGNERS = getMaxSigners(e);
    uint256 MIN_SIGNERS = getMinSigners(e);
    uint256 MAX_SIGNER_INDEX = getMaxSignerIndex(e);

    address[] expectedSigners =  getSignersHarness@withrevert(e);
    bool getSignersReverted = lastReverted;

    assert (
        signersCount > MAX_SIGNERS ||
        signersCount < MIN_SIGNERS || 
        singerIndex0 >= MAX_SIGNER_INDEX ||
        signer0 == 0
    ) => getSignersReverted;
}   

rule validateRefPriceShouldRevert (env e, address token, uint256 price, uint256 refPrice, uint256 maxRefPriceDeviationFactor) {
    uint256 diff = getDiff(e, price, refPrice);
    uint256 diffFactor = getDiffFactor(e, diff, refPrice);

    validateRefPriceHarness@withrevert(e, token, price, refPrice, maxRefPriceDeviationFactor);

    assert diffFactor > maxRefPriceDeviationFactor => lastReverted;

}

rule validatePricesUnitTest (env e) {   

    address expectedToken = getTokenAt0(e);
    uint256 expectedTimestamp = getUncompactedOracleTimestampAt0(e);
    uint256 expectedMinBlockNumber = getMinUncompactedOracleBlockNumberAt0(e);
    uint256 expectedMaxBlockNumber = getMaxUncompactedOracleBlockNumberAt0(e);

    Oracle.ValidatedPrice[] validatedPrices = validatePricesHarness(e);
    Oracle.ValidatedPrice validatedPrice = validatedPrices[0];
    
    assert expectedToken == validatedPrice.token;
    // assert expectedMin == validatedPrice.min;
    // assert expectedMax == validatedPrice.max;
    assert expectedTimestamp == validatedPrice.timestamp;
    assert expectedMinBlockNumber == validatedPrice.minBlockNumber;
    assert expectedMaxBlockNumber == validatedPrice.maxBlockNumber;
}

// rule validatedPricesShouldVerifyMedians (env e) {

//     require getSignersLength(e) == 1;

//     uint256 precision = getPrecisionAt0(e);
//     uint256 priceIndex = 0;
//     uint256 medianMinPrice = getMinPriceMedian(e, minPrices, precision);

// }
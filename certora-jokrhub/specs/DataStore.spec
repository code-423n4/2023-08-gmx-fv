// author: jokrhub
methods {
    // RoleStore.sol
    function _.hasRole(address, bytes32) external => DISPATCHER(true);
    function uintValues(bytes32) external returns(uint256) envfree;
    function sumReturnInt256Harness(uint256 uintValue, int256 value) external returns (uint256) envfree;
    function negativeCast(int256 value) external returns (uint256) envfree;
    function absHarness(int256 value) external returns (uint256) envfree;
}

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

rule applyDeltaToUintPositiveCoverage (env e, bytes32 key, uint256 value) {
    uint256 prevValue = uintValues(key);
    mathint nextUint = prevValue + value;
    uint256 expectedUint = applyDeltaToUint(e, key, value);
    uint256 currValue = uintValues(key);

    assert currValue == assert_uint256(nextUint) && currValue == expectedUint;
    assert(isControllerHarness(e));   
}

rule applyDeltaToUintCoverage (env e, bytes32 key, int256 value, string errorMessage) {
    uint256 prevValue = uintValues(key);
    uint256 nextUint = sumReturnInt256Harness(prevValue, value);
    uint256 expectedUint = applyDeltaToUint(e, key, value, errorMessage);
    uint256 currValue = uintValues(key);

    assert currValue == nextUint && currValue == expectedUint;
    assert(isControllerHarness(e));   

}

rule applyDeltaToUintShouldRevert (env e, bytes32 key, int256 value) {
    string errorMessage = "error";
    uint256 prevValue = uintValues(key);

    applyDeltaToUint@withrevert(e, key, value, errorMessage);
    bool applyDeltaToUintReverted = lastReverted;

    mathint currentValue = prevValue + value;

    assert (
            ( currentValue <= max_uint ) => 
            ( value < 0 && negativeCast(value) > prevValue) 
        ) || 
        (!isControllerHarness(e)
    ) <=> applyDeltaToUintReverted;
}

rule applyBoundedDeltaToUintCoverage (env e, bytes32 key, int256 value) {
    uint256 prevValue = uintValues(key);
    uint256 nextUint = sumReturnInt256Harness(prevValue, value);
    uint256 expectedUint = applyBoundedDeltaToUint(e, key, value);
    uint256 currValue = uintValues(key);
    
    assert value < 0 && negativeCast(value) > prevValue => currValue == 0 && expectedUint == 0;
    assert !(value < 0 && negativeCast(value) > prevValue) => currValue == nextUint && currValue == expectedUint;
    assert(isControllerHarness(e));   

}

//int
rule setIntCheck (env e, bytes32 key, int256 value) {
    int256 rvalue = setInt(e, key, value);
    assert value == getInt(e, key) && value == rvalue;
    assert(isControllerHarness(e));   

}

rule removeIntCheck (env e, bytes32 key) {
    removeInt(e, key);
    assert getInt(e, key) == 0;
    assert(isControllerHarness(e));   

}

rule incrementIntCheck (env e, bytes32 key, int256 value) {
    int256 pvalue = getInt(e, key);
    int256 rvalue = incrementInt(e, key, value);
    assert (getInt(e, key) == assert_int256(pvalue + value)) && (rvalue == assert_int256(pvalue + value));
    assert(isControllerHarness(e));   

}

rule decrementIntCheck (env e, bytes32 key, int256 value) {
    int256 pvalue = getInt(e, key);
    int256 rvalue = decrementInt(e, key, value);
    assert (getInt(e, key) == assert_int256(pvalue - value)) && (rvalue == assert_int256(pvalue - value));
    assert(isControllerHarness(e));   

}

//uint
rule setUintCheck (env e, bytes32 key, uint256 value) {
    uint256 rvalue = setUint(e, key, value);
    assert value == getUint(e, key) && value == rvalue;
    assert(isControllerHarness(e));   

}

rule removeUintCheck (env e, bytes32 key) {
    removeUint(e, key);
    assert getUint(e, key) == 0;
    assert(isControllerHarness(e));   

}

rule incrementUintCheck (env e, bytes32 key, uint256 value) {
    uint256 pvalue = getUint(e, key);
    uint256 rvalue = incrementUint(e, key, value);
    assert (getUint(e, key) == assert_uint256(pvalue + value)) && (rvalue == assert_uint256(pvalue + value));
    assert(isControllerHarness(e));   

}

rule decrementUintCheck (env e, bytes32 key, uint256 value) {
    uint256 pvalue = getUint(e, key);
    uint256 rvalue = decrementUint(e, key, value);
    assert (getUint(e, key) == assert_uint256(pvalue - value)) && (rvalue == assert_uint256(pvalue - value));
    assert(isControllerHarness(e));   

}

rule setAddressCheck (env e, bytes32 key, address value) {
    address rvalue = setAddress(e, key, value);
    assert getAddress(e, key) == value && rvalue == value;
    assert(isControllerHarness(e));   

}

rule removeAddressCheck (env e, bytes32 key) {
    removeAddress(e, key);
    assert getAddress(e, key) == 0;
    assert(isControllerHarness(e));   

}

rule setBoolCheck (env e, bytes32 key, bool value) {
    bool rvalue = setBool(e, key, value);
    assert getBool(e, key) == value && rvalue == value;
    assert(isControllerHarness(e));   

}

rule removeBoolCheck (env e, bytes32 key) {
    removeBool(e, key);
    assert getBool(e, key) == false;
    assert(isControllerHarness(e));   

}

rule setStringCheck (env e, bytes32 key, string value) {
    string rvalue = setString(e, key, value);
    assert compareStrings(e, getString(e, key), value) && compareStrings(e, rvalue, value);
    assert(isControllerHarness(e));   

}

// rule removeStringCheck (env e, bytes32 key) {
//     removeString(e, key);
//     assert compareStrings(e, getString(e, key), "");
// }

rule setBytes32Check (env e, bytes32 key, bytes32 value) {
    bytes32 rvalue = setBytes32(e, key, value);
    assert getBytes32(e, key) == value && rvalue == value;
    assert(isControllerHarness(e));   

}

rule removeBytes32Check (env e, bytes32 key) {
    removeBytes32(e, key);
    assert getBytes32(e, key) == getBytes0(e);
    assert(isControllerHarness(e));   

}



rule setUintArrayCheck (env e, bytes32 key) {
    uint256[] value = [4];
    setUintArray(e, key, value);
    uint256[] evalue =  getUintArray(e, key);
    assert evalue[0] == 4;
    assert(isControllerHarness(e));   

}

// rule removeUintArrayCheck (env e, bytes32 key) {
//     uint256[] pvalue =  getUintArray(e, key);
//     removeUintArray(e, key);
//     uint256[] evalue =  getUintArray(e, key);
//     assert pvalue[0] == 1 => evalue[0] == 0;
// } 



rule addAddressCheck (env e, bytes32 setKey, address value) {
    require getAddressCount(e, setKey) == 0;
    addAddress(e, setKey, value);
    address[] evalues = getAddressValuesAt(e, setKey, 1, 2);
    assert containsAddress(e, setKey, value);
    // assert evalues[0] == value;
    assert(isControllerHarness(e));   

}

rule removeAddressSetsCheck (env e, bytes32 setKey, address value) {
    removeAddress(e, setKey, value);
    assert(!containsAddress(e, setKey, value));
    assert(isControllerHarness(e));   

}
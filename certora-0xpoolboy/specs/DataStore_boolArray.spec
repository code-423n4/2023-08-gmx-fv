
// author: 0xpoolboy
methods {
    function getBoolArray(bytes32 key) external returns (bool[]) envfree;

    // RoleStore.sol
    function _.hasRole(address, bytes32) external => DISPATCHER(true);
}

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}


/*
 *   These rules were failing with prover error.
 *   However, moving them to a seperate spec file fixed the error
 */

rule getBoolArrayShouldNotRevert(
    bytes32 key
) {
    bool[] returnedValue = getBoolArray@withrevert(key);
    assert !lastReverted;
}

rule setBoolArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    bool[] value,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    bool[] otherValueBefore = getBoolArray(other);

    setBoolArray@withrevert(e, key, value);
    bool setBoolArrayReverted = lastReverted;

    bool[] valueAfter = getBoolArray(key);
    bool[] otherValueAfter = getBoolArray(other);

    assert !isController => setBoolArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !setBoolArrayReverted => (value.length == valueAfter.length
        && index < value.length => valueAfter[index] == value[index]),
        "function should set the value for key and return set value";
}

rule removeBoolArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    bool[] otherValueBefore = getBoolArray(other);

    removeBoolArray@withrevert(e, key);
    bool removeBoolArrayReverted = lastReverted;

    bool[] valueAfter = getBoolArray(key);
    bool[] otherValueAfter = getBoolArray(other);

    assert !isController => removeBoolArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !removeBoolArrayReverted => valueAfter.length == 0,
        "function should delete the array";
}
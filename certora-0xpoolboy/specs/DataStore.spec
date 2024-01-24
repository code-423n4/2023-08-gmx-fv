
// author: 0xpoolboy
methods {
    function getUint(bytes32 key) external returns (uint256) envfree;
    function getInt(bytes32 key) external returns (int256) envfree;
    function getAddress(bytes32 key) external returns (address) envfree;
    function getBool(bytes32 key) external returns (bool) envfree;
    function getString(bytes32 key) external returns (string) envfree;
    function getBytes32(bytes32 key) external returns (bytes32) envfree;
    function getUintArray(bytes32 key) external returns (uint256[]) envfree;
    function getIntArray(bytes32 key) external returns (int256[]) envfree;
    function getAddressArray(bytes32 key) external returns (address[]) envfree;
    // function getBoolArray(bytes32 key) external returns (bool[]) envfree;
    function getStringArray(bytes32 key) external returns (string[]) envfree;
    function getBytes32Array(bytes32 key) external returns (bytes32[]) envfree;
    function containsBytes32(bytes32, bytes32) external returns (bool) envfree;
    function getBytes32Count(bytes32) external returns (uint256) envfree;
    function getBytes32ValuesAt(bytes32, uint256, uint256) external returns (bytes32[]) envfree;
    function containsAddress(bytes32, address) external returns (bool) envfree;
    function getAddressCount(bytes32) external returns (uint256) envfree;
    function getAddressValuesAt(bytes32, uint256, uint256) external returns (address[]) envfree;
    function containsUint(bytes32, uint256) external returns (bool) envfree;
    function getUintCount(bytes32) external returns (uint256) envfree;
    function getUintValuesAt(bytes32, uint256, uint256) external returns (uint256[]) envfree;

    function removeBytes32(bytes32, bytes32) external;

    // RoleStore.sol
    function _.hasRole(address, bytes32) external => DISPATCHER(true);
}

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

// UINT
rule getUintShouldNotRevert(
    bytes32 key
) {
    uint256 returnedValue = getUint@withrevert(key);
    assert !lastReverted;
}

/* setUint
    Under the condition: isController(e)
    - sets correct value
    - does not affect values, for other keys
    - does not revert
    otherwise revert
 */
rule setUintCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 value
) {
    require (other != key);

    bool isController = isController(e);
    uint256 otherValueBefore = getUint(other);

    uint256 returnedValue = setUint@withrevert(e, key, value);
    bool setUintReverted = lastReverted;

    uint256 valueAfter = getUint(key);
    uint256 otherValueAfter = getUint(other);

    assert setUintReverted <=> !isController,
        "setUint should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "setUint should not affect other keys/values.";
    assert !setUintReverted => (value == returnedValue && value == valueAfter),
        "setUint should set the value for key and return set value";
}

rule removeUintCorrectness(
    env e,
    bytes32 key,
    bytes32 other
) {
    require (other != key);

    bool isController = isController(e);
    uint256 otherValueBefore = getUint(other);

    removeUint@withrevert(e, key);
    bool removeUintReverted = lastReverted;

    uint256 valueAfter = getUint(key);
    uint256 otherValueAfter = getUint(other);

    assert removeUintReverted <=> !isController,
        "removeUint should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "removeUint should not affect other keys/values.";
    assert !removeUintReverted => valueAfter == 0,
        "removeUint should set the value for key to zero";
}

// bug1
rule applyDeltaToUint_intValue_Correctness(
    env e,
    bytes32 key,
    bytes32 other,
    int256 value
) {
    require (other != key);

    bool isController = isController(e);
    mathint valueBefore = getUint(key);
    mathint otherValueBefore = getUint(other);

    uint256 returnedValue = applyDeltaToUint@withrevert(e, key, value, "");
    bool applyDeltaToUintReverted = lastReverted;

    mathint valueAfter = getUint(key);
    mathint otherValueAfter = getUint(other);


    // when the function reverted, then the new result would have been negative
    //assert ((value < 0) && (oldValue < to_mathint(-1 * value))) => lastReverted;
    assert (isController && (0 <= valueBefore + to_mathint(value)) && (valueBefore + to_mathint(value) < 2^256) && (to_mathint(value) != -2^255/*MININT*/))
           <=> !applyDeltaToUintReverted,
        "function should only revert iff caller does not hold controller role or when an overflow occures";
    //assert ((value < 0 && value > -1 * 2^127) && (valueBefore >= to_mathint(-1 * value))) => !lastReverted;
    //assert (value >=0 && to_mathint(value)+valueBefore < 2^256)  => !lastReverted;
    //assert (oldValue + to_mathint(value) < 0) => lastReverted;
    //assert (value != 0 && oldValue + value == oldValue) => lastReverted;
    assert !applyDeltaToUintReverted => (valueAfter == valueBefore + to_mathint(value) && to_mathint(returnedValue) == valueAfter),
        "function should set and return correct value";
}

rule applyDeltaToUint_uintValue_Correctness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 value
) {
    require (other != key);

    bool isController = isController(e);
    mathint valueBefore = getUint(key);
    mathint otherValueBefore = getUint(other);

    uint256 returnedValue = applyDeltaToUint@withrevert(e, key, value);
    bool applyDeltaToUintReverted = lastReverted;

    mathint valueAfter = getUint(key);
    mathint otherValueAfter = getUint(other);

    assert applyDeltaToUintReverted <=> !isController || valueBefore + to_mathint(value) >= 2^256,
        "applyDeltaToUint should only revert iff caller does not have controller role or a overflow occured";
    assert otherValueBefore == otherValueAfter,
        "applyDeltaToUint should not affect other keys/values.";
    assert !applyDeltaToUintReverted => (valueAfter == valueBefore + to_mathint(value) && returnedValue == assert_uint256(valueAfter)),
        "applyDeltaToUint should set the value correctly";
}


rule applyBoundedDeltaToUintCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    int256 value
) {
    require (other != key);

    bool isController = isController(e);
    mathint valueBefore = getUint(key);
    mathint otherValueBefore = getUint(other);

    uint256 returnedValue = applyBoundedDeltaToUint@withrevert(e, key, value);
    bool applyBoundedDeltaToUintReverted = lastReverted;

    mathint valueAfter = getUint(key);
    mathint otherValueAfter = getUint(other);

    assert !isController => applyBoundedDeltaToUintReverted, "If caller does not hold the controller role, function should revert";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert (!applyBoundedDeltaToUintReverted && value < 0 && valueBefore + to_mathint(value) < 0) => valueAfter == 0 && assert_uint256(returnedValue) == 0,
        "function should set the value to 0 and return 0, if interger underflow occures";
    assert (!applyBoundedDeltaToUintReverted && valueBefore + to_mathint(value) >= 0)=> (valueAfter == valueBefore + to_mathint(value) && returnedValue == assert_uint256(valueAfter)),
        "applyBoundedDeltaToUint should set the value correctly";
}

rule incrementUintCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 value
) {
    require (other != key);

    bool isController = isController(e);
    mathint valueBefore = getUint(key);
    mathint otherValueBefore = getUint(other);

    uint256 returnedValue = incrementUint@withrevert(e, key, value);
    bool incrementUintReverted = lastReverted;

    mathint valueAfter = getUint(key);
    mathint otherValueAfter = getUint(other);

    assert (!isController || valueBefore + to_mathint(value) >= 2^256) <=> incrementUintReverted,
        "function should only revert iff caller does not hold controller role or an overflow occures";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !incrementUintReverted => (valueAfter == valueBefore + to_mathint(value) && to_mathint(returnedValue) == valueAfter),
        "function should increment value by correct ammount and should return that value";
}

rule decrementUintCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 value
) {
    require (other != key);

    bool isController = isController(e);
    mathint valueBefore = getUint(key);
    mathint otherValueBefore = getUint(other);

    uint256 returnedValue = decrementUint@withrevert(e, key, value);
    bool decrementUintReverted = lastReverted;

    mathint valueAfter = getUint(key);
    mathint otherValueAfter = getUint(other);

    assert (!isController || valueBefore - to_mathint(value) < 0) <=> decrementUintReverted,
        "function should only revert iff caller does not hold controller role or an overflow occures";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !decrementUintReverted => (valueAfter == valueBefore - to_mathint(value) && to_mathint(returnedValue) == valueAfter),
        "function should decrement value by correct ammount and should return that value";
}

/*----------------------------------------------*/
// INT
rule getIntShouldNotRevert(
    bytes32 key
) {
    int256 returnedValue = getInt@withrevert(key);
    assert !lastReverted;
}

rule setIntCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    int256 value
) {
    require (other != key);

    bool isController = isController(e);
    int256 otherValueBefore = getInt(other);

    int256 returnedValue = setInt@withrevert(e, key, value);
    bool setIntReverted = lastReverted;

    int256 valueAfter = getInt(key);
    int256 otherValueAfter = getInt(other);

    assert setIntReverted <=> !isController,
        "function should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !setIntReverted => (value == returnedValue && value == valueAfter),
        "function should set the value for key and return set value";
}

rule removeIntCorrectness(
    env e,
    bytes32 key,
    bytes32 other
) {
    require (other != key);

    bool isController = isController(e);
    int256 otherValueBefore = getInt(other);

    removeInt@withrevert(e, key);
    bool removeIntReverted = lastReverted;

    int256 valueAfter = getInt(key);
    int256 otherValueAfter = getInt(other);

    assert removeIntReverted <=> !isController,
        "removeInt should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "removeInt should not affect other keys/values.";
    assert !removeIntReverted => valueAfter == 0,
        "removeUint should set the value for key to zero";
}

//FIXME gas optimization possible, see below
rule applyDeltaToIntCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    int256 value
) {
    require (other != key);

    bool isController = isController(e);
    mathint valueBefore = getInt(key);
    mathint otherValueBefore = getInt(other);

    int256 returnedValue = applyDeltaToInt@withrevert(e, key, value);
    bool applyDeltaToIntReverted = lastReverted;

    mathint valueAfter = getInt(key);
    mathint otherValueAfter = getInt(other);

    assert (isController && -2^255 <= valueBefore + to_mathint(value) && valueBefore + to_mathint(value) < 2^255)
           <=> !applyDeltaToIntReverted, "function should only revert iif caller does not hold controller role or an overflow occures";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values";
    assert !applyDeltaToIntReverted => (valueAfter == valueBefore + to_mathint(value) && to_mathint(returnedValue) == valueAfter),
        "function should set and return correct value";
}

// FIXME NOTE: Gas optimization possible:
// ERROR is:
// if (value < 0 && (-value).toUint256() > uintValue) {
// if (value < 0 && (-value).toUint256() => uintValue) {
// this is equal, function below proved it.
/*
rule itsTheSame(
    env e,
    bytes32 key,
    int256 value
) {
    require isController(e);
    storage initState = lastStorage;

    uint256 val = applyBoundedDeltaToUint@withrevert(e, key, value);
    bool  origRev = lastReverted;

    uint256 valErr = applyBoundedDeltaToUintERROR@withrevert(e, key, value) at initState;
    bool  errRev = lastReverted;

    assert origRev <=> errRev, "if one of them reverts, the other one should too";
    assert !origRev => (val == valErr), "both the function behave the same way";
}*/

rule incrementIntCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    int256 value
) {
    require (other != key);

    bool isController = isController(e);
    mathint valueBefore = getInt(key);
    mathint otherValueBefore = getInt(other);

    int256 returnedValue = incrementInt@withrevert(e, key, value);
    bool incrementIntReverted = lastReverted;

    mathint valueAfter = getInt(key);
    mathint otherValueAfter = getInt(other);

    assert (isController && -2^255 <= valueBefore + to_mathint(value) && valueBefore + to_mathint(value) < 2^255)
           <=> !incrementIntReverted, "function should only revert iif caller does not hold controller role or an overflow occures";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values";
    assert !incrementIntReverted => (valueAfter == valueBefore + to_mathint(value) && to_mathint(returnedValue) == valueAfter),
        "function should increment value by correct ammount and should return that value";
}

rule decrementIntCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    int256 value
) {
    require (other != key);

    bool isController = isController(e);
    mathint valueBefore = getInt(key);
    mathint otherValueBefore = getInt(other);

    int256 returnedValue = decrementInt@withrevert(e, key, value);
    bool decrementIntReverted = lastReverted;

    mathint valueAfter = getInt(key);
    mathint otherValueAfter = getInt(other);

    assert (isController && -2^255 <= valueBefore - to_mathint(value) && valueBefore - to_mathint(value) < 2^255) <=> !decrementIntReverted,
        "function should only revert iff caller does not hold controller role or an overflow occures";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !decrementIntReverted => (valueAfter == valueBefore - to_mathint(value) && to_mathint(returnedValue) == valueAfter),
        "function should decrement value by correct ammount and should return that value";
}

/*----------------------------------------------*/
// ADDRESS
rule getAddressShouldNotRevert(
    bytes32 key
) {
    address returnedValue = getAddress@withrevert(key);
    assert !lastReverted;
}

rule setAddressCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    address value
) {
    require (other != key);

    bool isController = isController(e);
    address otherValueBefore = getAddress(other);

    address returnedValue = setAddress@withrevert(e, key, value);
    bool setAddressReverted = lastReverted;

    address valueAfter = getAddress(key);
    address otherValueAfter = getAddress(other);

    assert setAddressReverted <=> !isController,
        "function should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !setAddressReverted => (value == returnedValue && value == valueAfter),
        "function should set the value for key and return set value";
}

rule removeAddressCorrectness(
    env e,
    bytes32 key,
    bytes32 other
) {
    require (other != key);

    bool isController = isController(e);
    address otherValueBefore = getAddress(other);

    removeAddress@withrevert(e, key);
    bool removeAddressReverted = lastReverted;

    address valueAfter = getAddress(key);
    address otherValueAfter = getAddress(other);

    assert removeAddressReverted <=> !isController,
        "function should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !removeAddressReverted => valueAfter == 0,
        "function should set the value for key to zero";
}
/*----------------------------------------------*/
// BOOL
rule getBoolShouldNotRevert(
    bytes32 key
) {
    bool returnedValue = getBool@withrevert(key);
    assert !lastReverted;
}

rule setBoolCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    bool value
) {
    require (other != key);

    bool isController = isController(e);
    bool otherValueBefore = getBool(other);

    bool returnedValue = setBool@withrevert(e, key, value);
    bool setBoolReverted = lastReverted;

    bool valueAfter = getBool(key);
    bool otherValueAfter = getBool(other);

    assert setBoolReverted <=> !isController,
        "function should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !setBoolReverted => (value == returnedValue && value == valueAfter),
        "function should set the value for key and return set value";
}

rule removeBoolCorrectness(
    env e,
    bytes32 key,
    bytes32 other
) {
    require (other != key);

    bool isController = isController(e);
    bool otherValueBefore = getBool(other);

    removeBool@withrevert(e, key);
    bool removeBoolReverted = lastReverted;

    bool valueAfter = getBool(key);
    bool otherValueAfter = getBool(other);

    assert removeBoolReverted <=> !isController,
        "function should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !removeBoolReverted => valueAfter == false,
        "function should set the value for key to zero";
}
/*----------------------------------------------*/
// STRING FIXME
/* THIS REVERTS, AND I DON'T KNOW WHY
rule getStringShouldNotRevert(
    bytes32 key
) {
    string returnedValue = getString@withrevert(key);
    assert !lastReverted;
}*/

// STRING FIXME
rule setStringCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    string value,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    string otherValueBefore = getString(other);

    string returnedValue = setString@withrevert(e, key, value);
    bool setStringReverted = lastReverted;

    string valueAfter = getString(key);
    string otherValueAfter = getString(other);

    assert !isController => setStringReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueBefore.length => otherValueBefore[index] == otherValueAfter[index],
        "function should not affect other keys/values.";
    assert !setStringReverted => (
               (value.length == returnedValue.length) /*&&  value.length == valueAfter.length)*/ // FAILS
            /*&& (index < value.length => (value[index] == returnedValue[index] && value[index] == valueAfter[index]))*/ // FAILS
        ), "function should set the value for key and return set value";
}

rule removeStringCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    string otherValueBefore = getString(other);

    removeString@withrevert(e, key);
    bool removeStringReverted = lastReverted;

    string valueAfter = getString(key);
    string otherValueAfter = getString(other);

    assert !isController => removeStringReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueBefore.length => otherValueBefore[index] == otherValueAfter[index],
        "function should not affect other keys/values.";
    assert !removeStringReverted => valueAfter.length == 0,
        "function should set the value for key to zero";
}

/*----------------------------------------------*/
// BYTES32
rule getBytes32ShouldNotRevert(
    bytes32 key
) {
    bytes32 returnedValue = getBytes32@withrevert(key);
    assert !lastReverted;
}

rule setBytes32Correctness(
    env e,
    bytes32 key,
    bytes32 other,
    bytes32 value
) {
    require (other != key);

    bool isController = isController(e);
    bytes32 otherValueBefore = getBytes32(other);

    bytes32 returnedValue = setBytes32@withrevert(e, key, value);
    bool setBytes32Reverted = lastReverted;

    bytes32 valueAfter = getBytes32(key);
    bytes32 otherValueAfter = getBytes32(other);

    assert setBytes32Reverted <=> !isController,
        "function should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !setBytes32Reverted => (value == returnedValue && value == valueAfter),
        "function should set the value for key and return set value";
}

rule removeBytes32Correctness(
    env e,
    bytes32 key,
    bytes32 other
) {
    require (other != key);

    bool isController = isController(e);
    bytes32 otherValueBefore = getBytes32(other);

    removeBytes32@withrevert(e, key);
    bool removeBytes32Reverted = lastReverted;

    bytes32 valueAfter = getBytes32(key);
    bytes32 otherValueAfter = getBytes32(other);

    assert removeBytes32Reverted <=> !isController,
        "function should only revert iff caller does not have controller role";
    assert otherValueBefore == otherValueAfter,
        "function should not affect other keys/values.";
    assert !removeBytes32Reverted => valueAfter == to_bytes32(0x0),
        "function should set the value for key to zero";
}

/*----------------------------------------------*/
// ARRAYS

rule getUintArrayShouldNotRevert(
    bytes32 key
) {
    uint256[] returnedValue = getUintArray@withrevert(key);
    assert !lastReverted;
}

rule setUintArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256[] value,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    uint256[] otherValueBefore = getUintArray(other);

    setUintArray@withrevert(e, key, value);
    bool setUintArrayReverted = lastReverted;

    uint256[] valueAfter = getUintArray(key);
    uint256[] otherValueAfter = getUintArray(other);

    assert !isController => setUintArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !setUintArrayReverted => (value.length == valueAfter.length
        && index < value.length => valueAfter[index] == value[index]),
        "function should set the value for key and return set value";
}

rule removeUintArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    uint256[] otherValueBefore = getUintArray(other);

    removeUintArray@withrevert(e, key);
    bool removeUintArrayReverted = lastReverted;

    uint256[] valueAfter = getUintArray(key);
    uint256[] otherValueAfter = getUintArray(other);

    assert !isController => removeUintArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !removeUintArrayReverted => valueAfter.length == 0,
        "function should delete the array";
}

rule getIntArrayShouldNotRevert(
    bytes32 key
) {
    int256[] returnedValue = getIntArray@withrevert(key);
    assert !lastReverted;
}

rule setIntArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    int256[] value,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    int256[] otherValueBefore = getIntArray(other);

    setIntArray@withrevert(e, key, value);
    bool setIntArrayReverted = lastReverted;

    int256[] valueAfter = getIntArray(key);
    int256[] otherValueAfter = getIntArray(other);

    assert !isController => setIntArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !setIntArrayReverted => (value.length == valueAfter.length
        && index < value.length => valueAfter[index] == value[index]),
        "function should set the value for key and return set value";
}

rule removeIntArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    int256[] otherValueBefore = getIntArray(other);

    removeIntArray@withrevert(e, key);
    bool removeIntArrayReverted = lastReverted;

    int256[] valueAfter = getIntArray(key);
    int256[] otherValueAfter = getIntArray(other);

    assert !isController => removeIntArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !removeIntArrayReverted => valueAfter.length == 0,
        "function should delete the array";
}

rule getAddressArrayShouldNotRevert(
    bytes32 key
) {
    address[] returnedValue = getAddressArray@withrevert(key);
    assert !lastReverted;
}

rule setAddressArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    address[] value,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    address[] otherValueBefore = getAddressArray(other);

    setAddressArray@withrevert(e, key, value);
    bool setAddressArrayReverted = lastReverted;

    address[] valueAfter = getAddressArray(key);
    address[] otherValueAfter = getAddressArray(other);

    assert !isController => setAddressArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !setAddressArrayReverted => (value.length == valueAfter.length
        && index < value.length => valueAfter[index] == value[index]),
        "function should set the value for key and return set value";
}

rule removeAddressArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    address[] otherValueBefore = getAddressArray(other);

    removeAddressArray@withrevert(e, key);
    bool removeAddressArrayReverted = lastReverted;

    address[] valueAfter = getAddressArray(key);
    address[] otherValueAfter = getAddressArray(other);

    assert !isController => removeAddressArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !removeAddressArrayReverted => valueAfter.length == 0,
        "function should delete the array";
}

/*
//FIXME fails because of prover error
rule getBoolArrayShouldNotRevert(
    bytes32 key
) {
    bool[] returnedValue = getBoolArray@withrevert(key);
    assert !lastReverted;
}

//FIXME fails because of prover error
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

//FIXME fails because of prover error
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
*/

rule getBytes32ArrayShouldNotRevert(
    bytes32 key
) {
    bytes32[] returnedValue = getBytes32Array@withrevert(key);
    assert !lastReverted;
}

rule setBytes32ArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    bytes32[] value,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    bytes32[] otherValueBefore = getBytes32Array(other);

    setBytes32Array@withrevert(e, key, value);
    bool setBytes32ArrayReverted = lastReverted;

    bytes32[] valueAfter = getBytes32Array(key);
    bytes32[] otherValueAfter = getBytes32Array(other);

    assert !isController => setBytes32ArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !setBytes32ArrayReverted => (value.length == valueAfter.length
        && index < value.length => valueAfter[index] == value[index]),
        "function should set the value for key and return set value";
}

rule removeBytes32ArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 index
) {
    require (other != key);

    bool isController = isController(e);
    bytes32[] otherValueBefore = getBytes32Array(other);

    removeBytes32Array@withrevert(e, key);
    bool removeBytes32ArrayReverted = lastReverted;

    bytes32[] valueAfter = getBytes32Array(key);
    bytes32[] otherValueAfter = getBytes32Array(other);

    assert !isController => removeBytes32ArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
        && index < otherValueAfter.length => otherValueAfter[index] == otherValueBefore[index],
        "function should not affect other keys/values.";
    assert !removeBytes32ArrayReverted => valueAfter.length == 0,
        "function should delete the array";
}

/* FIXME StringArray - needs work-around
rule getStringArrayShouldNotRevert(
    bytes32 key
) {
    getStringArray@withrevert(key);
    assert !lastReverted;
}

rule removeStringArrayCorrectness(
    env e,
    bytes32 key,
    bytes32 other,
    uint256 indexX,
    uint256 indexY
) {
    require (other != key);

    bool isController = isController(e);
    string[] otherValueBefore = getStringArray(other);

    removeStringArray@withrevert(e, key);
    bool removeStringArrayReverted = lastReverted;

    string[] valueAfter = getStringArray(key);
    string[] otherValueAfter = getStringArray(other);

    assert !isController => removeStringArrayReverted,
        "function should revert if caller does not have controller role";
    assert otherValueBefore.length == otherValueAfter.length
       && indexX < otherValueAfter.length => (indexY < otherValueAfter[indexX].length => otherValueAfter[indexX][indexY] == otherValueBefore[indexX][indexY]),
       "function should not affect other keys/values.";
    assert !removeStringArrayReverted => valueAfter.length == 0,
       "function should delete the array";
    assert removeStringArrayReverted;
}
*/
rule removeStringArrayShouldRevertWhenNotController(
    env e,
    bytes32 key
) {
    bool isController = isController(e);

    removeStringArray@withrevert(e, key);
    bool removeStringArrayReverted = lastReverted;

    assert !isController => removeStringArrayReverted,
        "function should revert if caller does not have controller role";
}

/// SETS

rule containsBytes32SShouldNotRevert(
    bytes32 setKey,
    bytes32 value
) {
    bool returnedValue = containsBytes32(setKey, value);
    assert !lastReverted;
}

rule getBytes32CountShouldNotRevert(
    bytes32 setKey
) {
    uint256 returnedValue = getBytes32Count(setKey);
    assert !lastReverted;
}

rule addBytes32Correctness(
    env e,
    bytes32 setKey,
    bytes32 otherKey,
    bytes32 value,
    bytes32 otherValue
) {
    require (otherKey != setKey);

    bool isController = isController(e);
    bool containsValue = containsBytes32(setKey, value);

    uint256 countBefore = getBytes32Count(setKey);
    uint256 otherCountBefore = getBytes32Count(otherKey);
    bool otherContainsValueBefore = containsBytes32(otherKey, otherValue);

    addBytes32@withrevert(e, setKey, value);
    bool addBytes32Reverted = lastReverted;

    uint256 countAfter = getBytes32Count(setKey);
    uint256 otherCountAfter = getBytes32Count(otherKey);
    bool otherContainsValueAfter = containsBytes32(otherKey, otherValue);

    assert !isController => addBytes32Reverted;
    assert !addBytes32Reverted => (
           (!containsValue => (countAfter == require_uint256(countBefore + 1)))
        || ( containsValue => (countAfter == countBefore)));
    assert otherCountBefore == otherCountAfter && otherContainsValueAfter == otherContainsValueBefore;
}


rule removeBytes32SetCorrectness(
    env e,
    bytes32 setKey,
    bytes32 otherKey,
    bytes32 value,
    bytes32 otherValue
) {
    require (otherKey != setKey);
    requireInvariant bytes32SetsInvariant();

    bool isController = isController(e);
    bool containsValue = containsBytes32(setKey, value);

    uint256 countBefore = getBytes32Count(setKey);
    uint256 otherCountBefore = getBytes32Count(otherKey);
    bool otherContainsValueBefore = containsBytes32(otherKey, otherValue);
    bool otherValueContainedInSetBefore = containsBytes32(setKey, otherValue);

    removeBytes32@withrevert(e, setKey, value);
    bool removeBytes32Reverted = lastReverted;

    uint256 countAfter = getBytes32Count(setKey);
    uint256 otherCountAfter = getBytes32Count(otherKey);
    bool otherContainsValueAfter = containsBytes32(otherKey, otherValue);
    bool otherValueContainedInSetAfter = containsBytes32(setKey, otherValue);

    assert !isController => removeBytes32Reverted;
    assert !removeBytes32Reverted => (
           ( containsValue => (countAfter == require_uint256(countBefore - 1)))
        || (!containsValue => (countAfter == countBefore)));

    assert (otherValue != value) => (otherValueContainedInSetAfter == otherValueContainedInSetBefore);
    assert otherCountBefore == otherCountAfter && otherContainsValueAfter == otherContainsValueBefore;
}

rule getBytes32ValuesAtCorrectness(
    env e,
    bytes32 setKey,
    uint256 start,
    uint256 end,
    bytes32 anyKey,
    bytes32 anyValue
) {
    bool containsValueBefore = containsBytes32(anyKey, anyValue);
    uint256 countBefore = getBytes32Count(setKey);

    bytes32[] returnedValues = getBytes32ValuesAt(setKey, start, end);

    bool containsValueAfter = containsBytes32(anyKey, anyValue);

    assert containsValueBefore == containsValueAfter,
        "function should not change any keys/values";
    assert returnedValues.length <= getBytes32Count(setKey),
        "function should not return more elements than are in set";
    assert (start <= end && end <= countBefore) => returnedValues.length == assert_uint256(end - start),
        "function should return correct number of elements";
}

// address SET
rule containsAddressSShouldNotRevert(
    bytes32 setKey,
    address value
) {
    bool returnedValue = containsAddress(setKey, value);
    assert !lastReverted;
}

rule getAddressCountShouldNotRevert(
    bytes32 setKey
) {
    uint256 returnedValue = getAddressCount(setKey);
    assert !lastReverted;
}

rule addAddressCorrectness(
    env e,
    bytes32 setKey,
    bytes32 otherKey,
    address value,
    address otherValue
) {
    require (otherKey != setKey);

    bool isController = isController(e);
    bool containsValue = containsAddress(setKey, value);

    uint256 countBefore = getAddressCount(setKey);
    uint256 otherCountBefore = getAddressCount(otherKey);
    bool otherContainsValueBefore = containsAddress(otherKey, otherValue);

    addAddress@withrevert(e, setKey, value);
    bool addAddressReverted = lastReverted;

    uint256 countAfter = getAddressCount(setKey);
    uint256 otherCountAfter = getAddressCount(otherKey);
    bool otherContainsValueAfter = containsAddress(otherKey, otherValue);

    assert !isController => addAddressReverted;
    assert !addAddressReverted => (
           (!containsValue => (countAfter == require_uint256(countBefore + 1)))
        || ( containsValue => (countAfter == countBefore)));
    assert otherCountBefore == otherCountAfter && otherContainsValueAfter == otherContainsValueBefore;
}


rule removeAddressSetCorrectness(
    env e,
    bytes32 setKey,
    bytes32 otherKey,
    address value,
    address otherValue
) {
    require (otherKey != setKey);
    requireInvariant addressSetsInvariant();

    bool isController = isController(e);
    bool containsValue = containsAddress(setKey, value);

    uint256 countBefore = getAddressCount(setKey);
    uint256 otherCountBefore = getAddressCount(otherKey);
    bool otherContainsValueBefore = containsAddress(otherKey, otherValue);
    bool otherValueContainedInSetBefore = containsAddress(setKey, otherValue);

    removeAddress@withrevert(e, setKey, value);
    bool removeAddressReverted = lastReverted;

    uint256 countAfter = getAddressCount(setKey);
    uint256 otherCountAfter = getAddressCount(otherKey);
    bool otherContainsValueAfter = containsAddress(otherKey, otherValue);
    bool otherValueContainedInSetAfter = containsAddress(setKey, otherValue);

    assert !isController => removeAddressReverted;
    assert !removeAddressReverted => (
           ( containsValue => (countAfter == require_uint256(countBefore - 1)))
        || (!containsValue => (countAfter == countBefore)));

    assert (otherValue != value) => (otherValueContainedInSetAfter == otherValueContainedInSetBefore);
    assert otherCountBefore == otherCountAfter && otherContainsValueAfter == otherContainsValueBefore;
}

rule getAddressValuesAtCorrectness(
    env e,
    bytes32 setKey,
    uint256 start,
    uint256 end,
    bytes32 anyKey,
    address anyValue
) {
    bool containsValueBefore = containsAddress(anyKey, anyValue);
    uint256 countBefore = getAddressCount(setKey);

    address[] returnedValues = getAddressValuesAt(setKey, start, end);

    bool containsValueAfter = containsAddress(anyKey, anyValue);

    assert containsValueBefore == containsValueAfter;
    assert returnedValues.length <= getAddressCount(setKey);
    assert (start == 0 && end == countBefore) => returnedValues.length == end;
}

//----------------
// uint SET
rule containsUintSShouldNotRevert(
    bytes32 setKey,
    uint256 value
) {
    bool returnedValue = containsUint(setKey, value);
    assert !lastReverted;
}

rule getUintCountShouldNotRevert(
    bytes32 setKey
) {
    uint256 returnedValue = getUintCount(setKey);
    assert !lastReverted;
}

rule addUintCorrectness(
    env e,
    bytes32 setKey,
    bytes32 otherKey,
    uint256 value,
    uint256 otherValue
) {
    require (otherKey != setKey);

    bool isController = isController(e);
    bool containsValue = containsUint(setKey, value);

    uint256 countBefore = getUintCount(setKey);
    uint256 otherCountBefore = getUintCount(otherKey);
    bool otherContainsValueBefore = containsUint(otherKey, otherValue);

    addUint@withrevert(e, setKey, value);
    bool addUintReverted = lastReverted;

    uint256 countAfter = getUintCount(setKey);
    uint256 otherCountAfter = getUintCount(otherKey);
    bool otherContainsValueAfter = containsUint(otherKey, otherValue);

    assert !isController => addUintReverted;
    assert !addUintReverted => (
           (!containsValue => (countAfter == require_uint256(countBefore + 1)))
        || ( containsValue => (countAfter == countBefore)));
    assert otherCountBefore == otherCountAfter && otherContainsValueAfter == otherContainsValueBefore;
}


rule removeUintSetCorrectness(
    env e,
    bytes32 setKey,
    bytes32 otherKey,
    uint256 value,
    uint256 otherValue
) {
    require (otherKey != setKey);
    requireInvariant uintSetsInvariant();

    bool isController = isController(e);
    bool containsValue = containsUint(setKey, value);

    uint256 countBefore = getUintCount(setKey);
    uint256 otherCountBefore = getUintCount(otherKey);
    bool otherContainsValueBefore = containsUint(otherKey, otherValue);
    bool otherValueContainedInSetBefore = containsUint(setKey, otherValue);

    removeUint@withrevert(e, setKey, value);
    bool removeUintReverted = lastReverted;

    uint256 countAfter = getUintCount(setKey);
    uint256 otherCountAfter = getUintCount(otherKey);
    bool otherContainsValueAfter = containsUint(otherKey, otherValue);
    bool otherValueContainedInSetAfter = containsUint(setKey, otherValue);

    assert !isController => removeUintReverted;
    assert !removeUintReverted => (
           ( containsValue => (countAfter == require_uint256(countBefore - 1)))
        || (!containsValue => (countAfter == countBefore)));
    assert (otherValue != value) => (otherValueContainedInSetAfter == otherValueContainedInSetBefore);
    assert otherCountBefore == otherCountAfter && otherContainsValueAfter == otherContainsValueBefore;
}

rule getUintValuesAtCorrectness(
    env e,
    bytes32 setKey,
    uint256 start,
    uint256 end,
    bytes32 anyKey,
    uint256 anyValue
) {
    bool containsValueBefore = containsUint(anyKey, anyValue);
    uint256 countBefore = getUintCount(setKey);

    uint256[] returnedValues = getUintValuesAt(setKey, start, end);

    bool containsValueAfter = containsUint(anyKey, anyValue);

    assert containsValueBefore == containsValueAfter;
    assert returnedValues.length <= getUintCount(setKey);
    assert (start == 0 && end == countBefore) => returnedValues.length == end;
}

// GHOST COPIES
// Bytes32Sets ghost copies
ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostBytes32Values {
    init_state axiom forall bytes32 k. forall mathint x. ghostBytes32Values[k][x] == to_bytes32(0);
}
ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostBytes32Indexes {
    init_state axiom forall bytes32 k. forall bytes32 x. ghostBytes32Indexes[k][x] == 0;
}
ghost mapping(bytes32 => uint256) ghostBytes32Length {
    init_state axiom forall bytes32 k. ghostBytes32Length[k] == 0;
    // assumption: it's infeasible to grow the list to these many elements.
    axiom forall bytes32 k. ghostBytes32Length[k] < 0xffffffffffffffffffffffffffffffff;
}

// AddressSets ghost copies
ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostAddressValues {
    init_state axiom forall bytes32 k. forall mathint x. ghostAddressValues[k][x] == to_bytes32(0);
}
ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostAddressIndexes {
    init_state axiom forall bytes32 k. forall bytes32 x. ghostAddressIndexes[k][x] == 0;
}
ghost mapping(bytes32 => uint256) ghostAddressLength {
    init_state axiom forall bytes32 k. ghostAddressLength[k] == 0;
    // assumption: it's infeasible to grow the list to these many elements.
    axiom forall bytes32 k. ghostAddressLength[k] < 0xffffffffffffffffffffffffffffffff;
}

// UintSets ghost copies
ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostUintValues {
    init_state axiom forall bytes32 k. forall mathint x. ghostUintValues[k][x] == to_bytes32(0);
}
ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostUintIndexes {
    init_state axiom forall bytes32 k. forall bytes32 x. ghostUintIndexes[k][x] == 0;
}
ghost mapping(bytes32 => uint256) ghostUintLength {
    init_state axiom forall bytes32 k. ghostUintLength[k] == 0;
    // assumption: it's infeasible to grow the list to these many elements.
    axiom forall bytes32 k. ghostUintLength[k] < 0xffffffffffffffffffffffffffffffff;
}


// HOOKS
// Bytes32Sets hooks
hook Sstore currentContract.bytes32Sets[KEY bytes32 setKey].(offset 0) uint256 newLength STORAGE {
    ghostBytes32Length[setKey] = newLength;
}

hook Sstore currentContract.bytes32Sets[KEY bytes32 setKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostBytes32Values[setKey][index] = newValue;
}
hook Sstore currentContract.bytes32Sets[KEY bytes32 setKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostBytes32Indexes[setKey][value] = newIndex;
}

hook Sload uint256 length currentContract.bytes32Sets[KEY bytes32 setKey].(offset 0) STORAGE {
    require ghostBytes32Length[setKey] == length;
}
hook Sload bytes32 value currentContract.bytes32Sets[KEY bytes32 setKey]._inner._values[INDEX uint256 index] STORAGE {
    require ghostBytes32Values[setKey][index] == value;
}
hook Sload uint256 index currentContract.bytes32Sets[KEY bytes32 setKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require ghostBytes32Indexes[setKey][value] == index;
}
// AddressSets hooks
hook Sstore currentContract.addressSets[KEY bytes32 setKey].(offset 0) uint256 newLength STORAGE {
    ghostAddressLength[setKey] = newLength;
}

hook Sstore currentContract.addressSets[KEY bytes32 setKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostAddressValues[setKey][index] = newValue;
}
hook Sstore currentContract.addressSets[KEY bytes32 setKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostAddressIndexes[setKey][value] = newIndex;
}

hook Sload uint256 length currentContract.addressSets[KEY bytes32 setKey].(offset 0) STORAGE {
    require ghostAddressLength[setKey] == length;
}
hook Sload bytes32 value currentContract.addressSets[KEY bytes32 setKey]._inner._values[INDEX uint256 index] STORAGE {
    require ghostAddressValues[setKey][index] == value;
}
hook Sload uint256 index currentContract.addressSets[KEY bytes32 setKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require ghostAddressIndexes[setKey][value] == index;
}
// UintSets hooks
hook Sstore currentContract.uintSets[KEY bytes32 setKey].(offset 0) uint256 newLength STORAGE {
    ghostUintLength[setKey] = newLength;
}

hook Sstore currentContract.uintSets[KEY bytes32 setKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostUintValues[setKey][index] = newValue;
}
hook Sstore currentContract.uintSets[KEY bytes32 setKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostUintIndexes[setKey][value] = newIndex;
}

hook Sload uint256 length currentContract.uintSets[KEY bytes32 setKey].(offset 0) STORAGE {
    require ghostUintLength[setKey] == length;
}
hook Sload bytes32 value currentContract.uintSets[KEY bytes32 setKey]._inner._values[INDEX uint256 index] STORAGE {
    require ghostUintValues[setKey][index] == value;
}
hook Sload uint256 index currentContract.uintSets[KEY bytes32 setKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require ghostUintIndexes[setKey][value] == index;
}

// INVARIANTS
invariant bytes32SetsInvariant()
    forall bytes32 setKey .(
        (forall uint256 index. 0 <= index && index < ghostBytes32Length[setKey] => to_mathint(ghostBytes32Indexes[setKey][ghostBytes32Values[setKey][index]]) == index + 1)
     && (forall bytes32 value. ghostBytes32Indexes[setKey][value] == 0 ||
         (ghostBytes32Values[setKey][ghostBytes32Indexes[setKey][value] - 1] == value && ghostBytes32Indexes[setKey][value] >= 1 && ghostBytes32Indexes[setKey][value] <= ghostBytes32Length[setKey])))
    filtered {
        // added filter to prevent certora prover error
        f -> f.selector != sig:setBoolArray(bytes32, bool[]).selector
    }

invariant addressSetsInvariant()
    forall bytes32 setKey .(
        (forall uint256 index. 0 <= index && index < ghostAddressLength[setKey] => to_mathint(ghostAddressIndexes[setKey][ghostAddressValues[setKey][index]]) == index + 1)
     && (forall bytes32 value. ghostAddressIndexes[setKey][value] == 0 ||
         (ghostAddressValues[setKey][ghostAddressIndexes[setKey][value] - 1] == value && ghostAddressIndexes[setKey][value] >= 1 && ghostAddressIndexes[setKey][value] <= ghostAddressLength[setKey])))
    filtered {
        // added filter to prevent certora prover error
        f -> f.selector != sig:setBoolArray(bytes32, bool[]).selector
    }

invariant uintSetsInvariant()
    forall bytes32 setKey .(
        (forall uint256 index. 0 <= index && index < ghostUintLength[setKey] => to_mathint(ghostUintIndexes[setKey][ghostUintValues[setKey][index]]) == index + 1)
     && (forall bytes32 value. ghostUintIndexes[setKey][value] == 0 ||
         (ghostUintValues[setKey][ghostUintIndexes[setKey][value] - 1] == value && ghostUintIndexes[setKey][value] >= 1 && ghostUintIndexes[setKey][value] <= ghostUintLength[setKey])))
    filtered {
        // added filter to prevent certora prover error
        f -> f.selector != sig:setBoolArray(bytes32, bool[]).selector
    }
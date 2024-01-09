using RoleStore as ROLE_STORE;

// author: neumoxx
methods {

    function getUint(bytes32) external returns (uint256) envfree;
    function setUint(bytes32, uint256) external returns (uint256);
    function removeUint(bytes32) external;
    function applyDeltaToUint(bytes32, int256, string) external returns (uint256);
    function applyDeltaToUint(bytes32, uint256) external returns (uint256);
    function applyBoundedDeltaToUint(bytes32, int256) external returns (uint256);
    function incrementUint(bytes32, uint256) external returns (uint256);
    function decrementUint(bytes32, uint256) external returns (uint256);
    function getInt(bytes32) external returns (int256) envfree;
    function setInt(bytes32, int256) external returns (int256);
    function removeInt(bytes32) external;
    function applyDeltaToInt(bytes32, int256) external returns (int256);
    function incrementInt(bytes32, int256) external returns (int256);
    function decrementInt(bytes32, int256) external returns (int256);
    function getAddress(bytes32) external returns (address) envfree;
    function setAddress(bytes32, address) external returns (address);
    function removeAddress(bytes32) external;
    function getBool(bytes32) external returns (bool) envfree;
    function setBool(bytes32, bool) external returns (bool);
    function removeBool(bytes32) external;
    function getString(bytes32) external returns (string) envfree;
    function setString(bytes32, string) external returns (string);
    function removeString(bytes32) external;
    function getBytes32(bytes32) external returns (bytes32) envfree;
    function setBytes32(bytes32, bytes32) external returns (bytes32);
    function removeBytes32(bytes32) external;
    function getUintArray(bytes32) external returns (uint256[]) envfree;
    function setUintArray(bytes32, uint256[]) external;
    function removeUintArray(bytes32) external;
    function getIntArray(bytes32) external returns (int256[]) envfree;
    function setIntArray(bytes32, int256[]) external;
    function removeIntArray(bytes32) external;
    function getAddressArray(bytes32) external returns (address[]) envfree;
    function setAddressArray(bytes32, address[]) external;
    function removeAddressArray(bytes32) external;
    function getBoolArray(bytes32) external returns (bool[]) envfree;
    function setBoolArray(bytes32, bool[]) external;
    function removeBoolArray(bytes32) external;
    function getStringArray(bytes32) external returns (string[]) envfree;
    function removeStringArray(bytes32) external;
    function getBytes32Array(bytes32) external returns (bytes32[]) envfree;
    function setBytes32Array(bytes32, bytes32[]) external;
    function removeBytes32Array(bytes32) external;

    function containsBytes32(bytes32, bytes32) external returns (bool) envfree;
    function getBytes32Count(bytes32) external returns (uint256) envfree;
    function getBytes32ValuesAt(bytes32, uint256, uint256) external returns (bytes32[]) envfree;
    function addBytes32(bytes32, bytes32) external;
    function removeBytes32(bytes32, bytes32) external;
    function containsAddress(bytes32, address) external returns (bool) envfree;
    function getAddressCount(bytes32) external returns (uint256) envfree;
    function getAddressValuesAt(bytes32, uint256, uint256) external returns (address[]) envfree;
    function addAddress(bytes32, address) external;
    function removeAddress(bytes32, address) external;
    function containsUint(bytes32, uint256) external returns (bool) envfree;
    function getUintCount(bytes32) external returns (uint256) envfree;
    function getUintValuesAt(bytes32, uint256, uint256) external returns (uint256[]) envfree;
    function addUint(bytes32, uint256) external;
    function removeUint(bytes32, uint256) external;

    // harness
    function maxInt256() external returns (int256) envfree;
    function minInt256() external returns (int256) envfree;
    function stringLength(string) external returns (uint256) envfree;
    function stringsEqual(string, string) external returns (bool) envfree;
    function uintArraysEqual(uint[], uint[]) external returns (bool) envfree;
    function intArraysEqual(int[], int[]) external returns (bool) envfree;
    function addressArraysEqual(address[], address[]) external returns (bool) envfree;
    function boolArraysEqual(bool[], bool[]) external returns (bool) envfree;
    function stringArraysEqual(string[], bytes32) external returns (bool) envfree;
    function bytes32ArraysEqual(bytes32[], bytes32[]) external returns (bool) envfree;
    function applyDeltaToUintRevertCondition(bytes32, int256) external returns (bool) envfree;

    // RoleStore.sol
    function _.hasRole(address, bytes32) external => DISPATCHER(true);
}


// DEFINITION

// @notice: Functions defined in harness contract
definition notHarnessCall(method f) returns bool =
    (f.selector != sig:maxInt256().selector
    && f.selector != sig:minInt256().selector
    && f.selector != sig:stringLength(string).selector
    && f.selector != sig:stringsEqual(string, string).selector
    && f.selector != sig:uintArraysEqual(uint[], uint[]).selector
    && f.selector != sig:intArraysEqual(int[], int[]).selector
    && f.selector != sig:addressArraysEqual(address[], address[]).selector
    && f.selector != sig:boolArraysEqual(bool[], bool[]).selector
    && f.selector != sig:stringArraysEqual(string[], bytes32).selector
    && f.selector != sig:bytes32ArraysEqual(bytes32[], bytes32[]).selector);


// RULES

// @notice: Consistency check for the execution of functions setUint and getUint
rule uintConsistencyChecks1(env e) {

    bytes32 key;
    uint256 value;
    int256 intValue;

    bool isController = hasControllerRole(e);

    // setUint & getUint
    setUint@withrevert(e, key, value);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => value == getUint(key);

}

// @notice: Consistency check for the execution of function removeUint
rule uintConsistencyChecks2(env e) {

    bytes32 key;
    uint256 value;
    int256 intValue;

    bool isController = hasControllerRole(e);

    // removeUint
    removeUint@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => 0 == getUint(key);

}

// @notice: Consistency check for the execution of function applyDeltaToUint with error message
// @notice: Catches bug #1
rule uintConsistencyChecks3(env e) {

    bytes32 key;
    uint256 value;
    int256 intValue;
    string errorMessage = "error";

    bool isController = hasControllerRole(e);

    // applyDeltaToUint (int)
    uint256 cachedValue1 = getUint(key);
    bool revertCondition = applyDeltaToUintRevertCondition@withrevert(key, intValue);
    revertCondition = revertCondition || lastReverted;
    applyDeltaToUint@withrevert(e, key, intValue, errorMessage);
    bool lastRev = lastReverted;
    assert (
      e.msg.value > 0 ||
      !isController ||
      revertCondition ||
      cachedValue1 + intValue < 0 ||
      cachedValue1 + intValue > max_uint256
    ) <=> lastRev;
    uint256 res1 = require_uint256(cachedValue1 + intValue);
    assert !lastRev => getUint(key) == res1;

}

// @notice: Consistency check for the execution of function applyDeltaToUint without error message
rule uintConsistencyChecks4(env e) {

    bytes32 key;
    uint256 value;
    int256 intValue;

    bool isController = hasControllerRole(e);

    // applyDeltaToUint (uint)
    uint256 cachedValue2 = getUint(key);
    applyDeltaToUint@withrevert(e, key, value);
    bool lastRev = lastReverted;
    assert lastRev <=> (
      e.msg.value > 0 ||
      !isController ||
      (cachedValue2 + value > to_mathint(max_uint256))
    );
    uint256 res2 = require_uint256(cachedValue2 + value);
    assert !lastRev => getUint(key) == res2;

}

// @notice: Consistency check for the execution of function applyBoundedDeltaToUint
rule uintConsistencyChecks5(env e) {

    bytes32 key;
    uint256 value;
    int256 intValue;

    bool isController = hasControllerRole(e);

    // applyBoundedDeltaToUint
    uint256 cachedValue3 = getUint(key);
    bool revertCondition = applyDeltaToUintRevertCondition@withrevert(key, intValue);
    revertCondition = lastReverted;
    applyBoundedDeltaToUint@withrevert(e, key, intValue);
    bool lastRev = lastReverted;
    uint256 res3 = require_uint256(cachedValue3 + intValue);
    assert lastRev <=> (
      e.msg.value > 0 ||
      !isController ||
      revertCondition ||
      cachedValue3 + intValue < 0 ||
      cachedValue3 + intValue > max_uint256
    );
    assert !lastRev => (
      !(intValue < 0 && -1*intValue > to_mathint(cachedValue3)) => getUint(key) == res3 &&
      (intValue < 0 && -1*intValue > to_mathint(cachedValue3)) => getUint(key) == 0
    );

}

// @notice: Consistency check for the execution of function incrementUint
rule uintConsistencyChecks6(env e) {

    bytes32 key;
    uint256 value;
    int256 intValue;

    bool isController = hasControllerRole(e);

    // incrementUint
    uint256 cachedValue4 = getUint(key);
    incrementUint@withrevert(e, key, value);
    assert lastReverted <=> (
      e.msg.value > 0 ||
      !isController ||
      (cachedValue4 + value > to_mathint(max_uint256))
    );
    uint256 res4 = require_uint256(cachedValue4 + value);
    assert !lastReverted => getUint(key) == res4;

}

// @notice: Consistency check for the execution of function decrementUint
rule uintConsistencyChecks7(env e) {

    bytes32 key;
    uint256 value;
    int256 intValue;

    bool isController = hasControllerRole(e);

    // decrementUint
    uint256 cachedValue5 = getUint(key);
    decrementUint@withrevert(e, key, value);
    assert lastReverted <=> (
      e.msg.value > 0 ||
      !isController ||
      (cachedValue5 - value < to_mathint(0))
    );
    uint256 res5 = require_uint256(cachedValue5 - value);
    assert !lastReverted => getUint(key) == res5;

}

// @notice: Consistency check for the execution of functions setInt and getInt
rule intConsistencyChecks1(env e) {

    bytes32 key;
    int256 value;

    bool isController = hasControllerRole(e);

    // setInt & getInt
    setInt@withrevert(e, key, value);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => value == getInt(key);

}

// @notice: Consistency check for the execution of function removeInt
rule intConsistencyChecks2(env e) {

    bytes32 key;
    int256 value;

    bool isController = hasControllerRole(e);

    // removeInt
    removeInt@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => 0 == getInt(key);

}

// @notice: Consistency check for the execution of function applyDeltaToInt
rule intConsistencyChecks3(env e) {

    int256 max_int256 = maxInt256();
    int256 min_int256 = minInt256();

    bytes32 key;
    int256 value;

    bool isController = hasControllerRole(e);

    // applyDeltaToInt
    int256 cachedValue1 = getInt(key);
    applyDeltaToInt@withrevert(e, key, value);
    assert lastReverted <=> (
      e.msg.value > 0 ||
      !isController ||
      (value + cachedValue1 > to_mathint(max_int256)) ||
      (value + cachedValue1 < to_mathint(min_int256))
    );
    int256 res1 = require_int256(cachedValue1 + value);
    assert !lastReverted => getInt(key) == res1;

}

// @notice: Consistency check for the execution of function incrementInt
rule intConsistencyChecks4(env e) {

    int256 max_int256 = maxInt256();
    int256 min_int256 = minInt256();

    bytes32 key;
    int256 value;

    bool isController = hasControllerRole(e);

    // incrementInt
    int256 cachedValue2 = getInt(key);
    incrementInt@withrevert(e, key, value);
    assert lastReverted <=> (
      e.msg.value > 0 ||
      !isController ||
      (cachedValue2 + value > to_mathint(max_int256)) ||
      (cachedValue2 + value < to_mathint(min_int256))
    );
    int256 res2 = require_int256(cachedValue2 + value);
    assert !lastReverted => getInt(key) == res2;

}

// @notice: Consistency check for the execution of function decrementInt
rule intConsistencyChecks5(env e) {

    int256 max_int256 = maxInt256();
    int256 min_int256 = minInt256();

    bytes32 key;
    int256 value;

    bool isController = hasControllerRole(e);

    // decrementInt
    int256 cachedValue3 = getInt(key);
    decrementInt@withrevert(e, key, value);
    bool lastRev = lastReverted;
    assert lastRev <=> (
      e.msg.value > 0 ||
      !isController ||
      (cachedValue3 - value > to_mathint(max_int256)) ||
      (cachedValue3 - value < to_mathint(min_int256))
    );
    int256 res3 = require_int256(cachedValue3 - value);
    assert !lastRev => getInt(key) == res3;

}

// @notice: Consistency check for the execution of functions setAddress and getAddress
rule addressConsistencyChecks1(env e) {

    bytes32 key;
    address value;

    bool isController = hasControllerRole(e);

    // setAddress & getAddress
    setAddress@withrevert(e, key, value);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => value == getAddress(key);

}

// @notice: Consistency check for the execution of function removeAddress
rule addressConsistencyChecks2(env e) {

    bytes32 key;
    address value;

    bool isController = hasControllerRole(e);

    // removeAddress
    removeAddress@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => 0 == getAddress(key);

}

// @notice: Consistency check for the execution of functions setBool and getBool
rule boolConsistencyChecks1(env e) {

    bytes32 key;
    bool value;

    bool isController = hasControllerRole(e);

    // setBool & getBool
    setBool@withrevert(e, key, value);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => value == getBool(key);

}

// @notice: Consistency check for the execution of function removeBool
rule boolConsistencyChecks2(env e) {

    bytes32 key;
    bool value;

    bool isController = hasControllerRole(e);

    // removeBool
    removeBool@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => false == getBool(key);

}

// @notice: Consistency check for the execution of functions setString and getString
rule stringConsistencyChecks1(env e) {

    bytes32 key;
    string value;

    require stringLength(value) < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // setString & getString
    setString@withrevert(e, key, value);
    bool lastRev1 = lastReverted;
    string valueAfterSet = getString(key);
    assert (e.msg.value > 0 || !isController) <=> lastRev1;
    //assert !lastRev1 => stringsEqual(value, valueAfterSet);

}

// @notice: Consistency check for the execution of function removeString
rule stringConsistencyChecks2(env e) {

    bytes32 key;
    string value;

    require stringLength(value) < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // removeString
    removeString@withrevert(e, key);
    bool lastRev2 = lastReverted;
    assert (e.msg.value > 0 || !isController) => lastRev2;
    assert !lastRev2 => stringLength(getString(key)) == 0;

}

// @notice: Consistency check for the execution of functions setBytes32 and getBytes32
rule bytes32ConsistencyChecks1(env e) {

    bytes32 key;
    bytes32 value;

    bool isController = hasControllerRole(e);

    // setBytes32 & getBytes32
    setBytes32@withrevert(e, key, value);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => value == getBytes32(key);

}

// @notice: Consistency check for the execution of function removeBytes32
rule bytes32ConsistencyChecks2(env e) {

    bytes32 key;
    bytes32 value;

    bool isController = hasControllerRole(e);

    // removeBytes32
    removeBytes32@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => to_bytes32(0) == getBytes32(key);

}

// @notice: Consistency check for the execution of functions setUintArray and getUintArray
rule uintArrayConsistencyChecks1(env e) {

    bytes32 key;
    uint256[] value;
    uint256[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // setUintArray & getUintArray
    setUintArray@withrevert(e, key, value);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => uintArraysEqual(value, getUintArray(key));

}

// @notice: Consistency check for the execution of function removeUintArray
rule uintArrayConsistencyChecks2(env e) {

    bytes32 key;
    uint256[] value;
    uint256[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // removeStringUintArray
    removeUintArray@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => uintArraysEqual(emptyArray, getUintArray(key));

}

// @notice: Consistency check for the execution of functions setIntArray and getIntArray
rule intArrayConsistencyChecks1(env e) {

    bytes32 key;
    int256[] value;
    int256[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // setIntArray & getIntArray
    setIntArray@withrevert(e, key, value);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => intArraysEqual(value, getIntArray(key));

}

// @notice: Consistency check for the execution of function removeIntArray
rule intArrayConsistencyChecks2(env e) {

    bytes32 key;
    int256[] value;
    int256[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // removeIntArray
    removeIntArray@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => intArraysEqual(emptyArray, getIntArray(key));

}

// @notice: Consistency check for the execution of functions setAddressArray and getAddressArray
rule addressArrayConsistencyChecks1(env e) {

    bytes32 key;
    address[] value;
    address[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // setAddressArray & getAddressArray
    setAddressArray@withrevert(e, key, value);
    assert (e.msg.value > 0 || !isController) => lastReverted;
    assert !lastReverted => addressArraysEqual(value, getAddressArray(key));

}

// @notice: Consistency check for the execution of function removeAddressArray
rule addressArrayConsistencyChecks2(env e) {

    bytes32 key;
    address[] value;
    address[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // removeAddressArray
    removeAddressArray@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => addressArraysEqual(emptyArray, getAddressArray(key));

}

// @notice: Consistency check for the execution of functions setBoolArray and getBoolArray
rule boolArrayConsistencyChecks1(env e) {

    bytes32 key;
    bool[] value;
    bool[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // setBoolArray & getBoolArray
    setBoolArray@withrevert(e, key, value);
    assert (e.msg.value > 0 || !isController) => lastReverted;
    assert !lastReverted => boolArraysEqual(value, getBoolArray(key));

}

// @notice: Consistency check for the execution of function removeBoolArray
rule boolArrayConsistencyChecks2(env e) {

    bytes32 key;
    bool[] value;
    bool[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // removeBoolArray
    removeBoolArray@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => boolArraysEqual(emptyArray, getBoolArray(key));

}

// @notice: Consistency check for the execution of functions getStringArray and removeStringArray
rule stringArrayConsistencyChecks(env e) {

    bytes32 key;
    string[] value;
    string[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // getStringArray & removeStringArray
    removeStringArray@withrevert(e, key);
    assert (e.msg.value > 0 || !isController) => lastReverted;
    assert !lastReverted => stringArraysEqual(emptyArray, key);

}

// @notice: Consistency check for the execution of functions setBytes32Array and getBytes32Array
rule bytes32ArrayConsistencyChecks1(env e) {

    bytes32 key;
    bytes32[] value;
    bytes32[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // setBytes32Array & getBytes32Array
    setBytes32Array@withrevert(e, key, value);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => bytes32ArraysEqual(value, getBytes32Array(key));

}

// @notice: Consistency check for the execution of function removeBytes32Array
rule bytes32ArrayConsistencyChecks2(env e) {

    bytes32 key;
    bytes32[] value;
    bytes32[] emptyArray;

    require emptyArray.length == 0;
    require value.length < 10; // make rule less computationally intensive

    bool isController = hasControllerRole(e);

    // removeBytes32Array
    removeBytes32Array@withrevert(e, key);
    assert lastReverted <=> (e.msg.value > 0 || !isController);
    assert !lastReverted => bytes32ArraysEqual(emptyArray, getBytes32Array(key));

}

// @notice: Consistency check for the execution of functions addBytes32 and containsBytes32
rule bytes32SetsConsistencyChecks1(env e) {

    bytes32 key;
    bytes32 value;

    requireInvariant bytes32SetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // addBytes32 & containsBytes32
    addBytes32@withrevert(e, key, value);
    bool lastRev1 = lastReverted;
    bool contained1 = containsBytes32(key, value);
    assert lastRev1 <=> (e.msg.value > 0 || !isController);
    assert !lastRev1 => contained1;

}

// @notice: Consistency check for the execution of function getBytes32Count
rule bytes32SetsConsistencyChecks2(env e) {

    bytes32 key;
    bytes32 value;

    requireInvariant bytes32SetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // getBytes32Count
    addBytes32(e, key, value);
    uint256 length = getBytes32Count@withrevert(key);
    assert !lastReverted;
    assert length > 0;

}

// @notice: Consistency check for the execution of function removeBytes32
rule bytes32SetsConsistencyChecks3(env e) {

    bytes32 key;
    bytes32 value;

    requireInvariant bytes32SetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // removeBytes32
    removeBytes32@withrevert(e, key, value);
    bool lastRev2 = lastReverted;
    bool contained2 = containsBytes32(key, value);
    assert (e.msg.value > 0 || !isController) => lastRev2;
    assert !lastRev2 => !contained2;

}

// @notice: Consistency check for the execution of functions addAddress and containsAddress
rule addressSetsConsistencyChecks1(env e) {

    bytes32 key;
    address value;

    requireInvariant addressSetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // addAddress & containsAddress
    addAddress@withrevert(e, key, value);
    bool lastRev1 = lastReverted;
    bool contained1 = containsAddress(key, value);
    assert lastRev1 <=> (e.msg.value > 0 || !isController);
    assert !lastRev1 => contained1;

}

// @notice: Consistency check for the execution of function getAddressCount
rule addressSetsConsistencyChecks2(env e) {

    bytes32 key;
    address value;

    requireInvariant addressSetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // getAddressCount
    addAddress(e, key, value);
    uint256 length = getAddressCount@withrevert(key);
    assert !lastReverted;
    assert length > 0;

}

// @notice: Consistency check for the execution of function removeAddress
rule addressSetsConsistencyChecks3(env e) {

    bytes32 key;
    address value;

    requireInvariant addressSetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // removeAddress
    removeAddress@withrevert(e, key, value);
    bool lastRev2 = lastReverted;
    bool contained2 = containsAddress(key, value);
    assert (e.msg.value > 0 || !isController) => lastRev2;
    assert !lastRev2 => !contained2;

}

// @notice: Consistency check for the execution of functions addUint and containsUint
rule uintSetsConsistencyChecks1(env e) {

    bytes32 key;
    uint value;

    requireInvariant uintSetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // addUint & containsUint
    addUint@withrevert(e, key, value);
    bool lastRev1 = lastReverted;
    bool contained1 = containsUint(key, value);
    assert lastRev1 <=> (e.msg.value > 0 || !isController);
    assert !lastRev1 => contained1;

}

// @notice: Consistency check for the execution of function getUintCount
rule uintSetsConsistencyChecks2(env e) {

    bytes32 key;
    uint value;

    requireInvariant uintSetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // getUintCount
    addUint(e, key, value);
    uint256 length = getUintCount@withrevert(key);
    assert !lastReverted;
    assert length > 0;

}

// @notice: Consistency check for the execution of function removeUint
rule uintSetsConsistencyChecks3(env e) {

    bytes32 key;
    uint value;

    requireInvariant uintSetsEnumerableSetInvariant();

    bool isController = hasControllerRole(e);

    // removeUint
    removeUint@withrevert(e, key, value);
    bool lastRev2 = lastReverted;
    bool contained2 = containsUint(key, value);
    assert (e.msg.value > 0 || !isController) => lastRev2;
    assert !lastRev2 => !contained2;

}

// @notice: Ensure all funtions have at least one non-reverting path
rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}


// GHOST COPIES:
// For every storage variable we add a ghost field that is kept synchronized by hooks.
// The ghost fields can be accessed by the spec, even inside quantifiers.

// bytes32Sets

// ghost field for the values array
ghost mapping(bytes32 => mapping(mathint => bytes32)) bytes32SetsGhostValues {
    init_state axiom forall bytes32 x. forall mathint y. bytes32SetsGhostValues[x][y] == to_bytes32(0);
}
// ghost field for the indexes map
ghost mapping(bytes32 => mapping(bytes32 => uint256)) bytes32SetsGhostIndexes {
    init_state axiom forall bytes32 x. forall bytes32 y. bytes32SetsGhostIndexes[x][y] == 0;
    axiom forall bytes32 x. forall bytes32 y. bytes32SetsGhostIndexes[x][y] > 0 => bytes32SetsGhostValues[x][bytes32SetsGhostIndexes[x][y]] == y;
}
// ghost field for the length of the values array (stored in offset 0)
ghost mapping(bytes32 => uint256) bytes32SetsGhostLength {
    // assumption: it's infeasible to grow the list to these many elements.
    init_state axiom forall bytes32 role. bytes32SetsGhostLength[role] == 0;
    axiom forall bytes32 x. bytes32SetsGhostLength[x] < 0xffffffffffffffffffffffffffffffff;
}

// addressSets
ghost mapping(bytes32 => mapping(mathint => bytes32)) addressSetsGhostValues {
    init_state axiom forall bytes32 x. forall mathint y. addressSetsGhostValues[x][y] == to_bytes32(0);
    axiom forall bytes32 x. forall mathint y. (addressSetsGhostValues[x][y] & to_bytes32(2^160 - 1  )) == addressSetsGhostValues[x][y];
}
// ghost field for the indexes map
ghost mapping(bytes32 => mapping(bytes32 => uint256)) addressSetsGhostIndexes {
    init_state axiom forall bytes32 x. forall bytes32 y. addressSetsGhostIndexes[x][y] == 0;
    axiom forall bytes32 x. forall bytes32 y. addressSetsGhostIndexes[x][y] > 0 => addressSetsGhostValues[x][addressSetsGhostIndexes[x][y]] == y;
}
// ghost field for the length of the values array (stored in offset 0)
ghost mapping(bytes32 => uint256) addressSetsGhostLength {
    // assumption: it's infeasible to grow the list to these many elements.
    init_state axiom forall bytes32 role. addressSetsGhostLength[role] == 0;
    axiom forall bytes32 x. addressSetsGhostLength[x] < 0xffffffffffffffffffffffffffffffff;
}

// uintSets
ghost mapping(bytes32 => mapping(mathint => bytes32)) uintSetsGhostValues {
    init_state axiom forall bytes32 x. forall mathint y. uintSetsGhostValues[x][y] == to_bytes32(0);
}
// ghost field for the indexes map
ghost mapping(bytes32 => mapping(bytes32 => uint256)) uintSetsGhostIndexes {
    init_state axiom forall bytes32 x. forall bytes32 y. uintSetsGhostIndexes[x][y] == 0;
    axiom forall bytes32 x. forall bytes32 y. uintSetsGhostIndexes[x][y] > 0 => uintSetsGhostValues[x][uintSetsGhostIndexes[x][y]] == y;
}
// ghost field for the length of the values array (stored in offset 0)
ghost mapping(bytes32 => uint256) uintSetsGhostLength {
    // assumption: it's infeasible to grow the list to these many elements.
    init_state axiom forall bytes32 role. uintSetsGhostLength[role] == 0;
    axiom forall bytes32 x. uintSetsGhostLength[x] < 0xffffffffffffffffffffffffffffffff;
}


// HOOKS
// Store hook to synchronize bytes32SetsGhostLength with the length of the bytes32Sets._inner._values array.
// We need to use (offset 0) here, as there is no keyword yet to access the length.

hook Sstore currentContract.bytes32Sets[KEY bytes32 roleKey].(offset 0) uint256 newLength STORAGE {
    bytes32SetsGhostLength[roleKey] = newLength;
}
// Store hook to synchronize bytes32SetsGhostValues array with bytes32Sets[roleKey]._inner._values.
hook Sstore currentContract.bytes32Sets[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    bytes32SetsGhostValues[roleKey][index] = newValue;
}
// Store hook to synchronize bytes32SetsGhostIndexes array with bytes32Sets[roleKey]._inner._indexes.
hook Sstore currentContract.bytes32Sets[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    bytes32SetsGhostIndexes[roleKey][value] = newIndex;
}

hook Sstore currentContract.addressSets[KEY bytes32 roleKey].(offset 0) uint256 newLength STORAGE {
    addressSetsGhostLength[roleKey] = newLength;
}
// Store hook to synchronize addressSetsGhostValues array with addressSets[roleKey]._inner._values.
hook Sstore currentContract.addressSets[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    addressSetsGhostValues[roleKey][index] = newValue;
}
// Store hook to synchronize addressSetsGhostIndexes array with addressSets[roleKey]._inner._indexes.
hook Sstore currentContract.addressSets[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    addressSetsGhostIndexes[roleKey][value] = newIndex;
}

hook Sstore currentContract.uintSets[KEY bytes32 roleKey].(offset 0) uint256 newLength STORAGE {
    uintSetsGhostLength[roleKey] = newLength;
}
// Store hook to synchronize uintSetsGhostValues array with uintSets[roleKey]._inner._values.
hook Sstore currentContract.uintSets[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    uintSetsGhostValues[roleKey][index] = newValue;
}
// Store hook to synchronize uintSetsGhostIndexes array with uintSets[roleKey]._inner._indexes.
hook Sstore currentContract.uintSets[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    uintSetsGhostIndexes[roleKey][value] = newIndex;
}

hook Sload uint256 length currentContract.bytes32Sets[KEY bytes32 roleKey].(offset 0) STORAGE {
    require bytes32SetsGhostLength[roleKey] == length;
}
hook Sload bytes32 value currentContract.bytes32Sets[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] STORAGE {
    require bytes32SetsGhostValues[roleKey][index] == value;
}
hook Sload uint256 index currentContract.bytes32Sets[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require bytes32SetsGhostIndexes[roleKey][value] == index;
}

hook Sload uint256 length currentContract.addressSets[KEY bytes32 roleKey].(offset 0) STORAGE {
    require addressSetsGhostLength[roleKey] == length;
}
hook Sload bytes32 value currentContract.addressSets[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] STORAGE {
    require addressSetsGhostValues[roleKey][index] == value;
}
hook Sload uint256 index currentContract.addressSets[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require addressSetsGhostIndexes[roleKey][value] == index;
}

hook Sload uint256 length currentContract.uintSets[KEY bytes32 roleKey].(offset 0) STORAGE {
    require uintSetsGhostLength[roleKey] == length;
}
hook Sload bytes32 value currentContract.uintSets[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] STORAGE {
    require uintSetsGhostValues[roleKey][index] == value;
}
hook Sload uint256 index currentContract.uintSets[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require uintSetsGhostIndexes[roleKey][value] == index;
}



// INVARIANTS

//  This is the main invariant stating that the indexes and values always match:
//        values[indexes[v] - 1] = v for all values v in the set
//    and indexes[values[i]] = i+1 for all valid indexes i.

invariant bytes32SetsEnumerableSetInvariant()
    (forall bytes32 roleKey.
      (forall uint256 index.
        (0 <= index && index < bytes32SetsGhostLength[roleKey] => to_mathint(bytes32SetsGhostIndexes[roleKey][bytes32SetsGhostValues[roleKey][index]]) == index + 1)
      )
      &&
      (forall bytes32 value.
        bytes32SetsGhostIndexes[roleKey][value] == 0 ||
        (bytes32SetsGhostValues[roleKey][bytes32SetsGhostIndexes[roleKey][value] - 1] == value && bytes32SetsGhostIndexes[roleKey][value] >= 1 && bytes32SetsGhostIndexes[roleKey][value] <= bytes32SetsGhostLength[roleKey])
      )
    );


invariant addressSetsEnumerableSetInvariant()
    (forall bytes32 roleKey.
      (forall uint256 index.
        (0 <= index && index < addressSetsGhostLength[roleKey] => to_mathint(addressSetsGhostIndexes[roleKey][addressSetsGhostValues[roleKey][index]]) == index + 1)
      )
      &&
      (forall bytes32 value.
        addressSetsGhostIndexes[roleKey][value] == 0 ||
        (addressSetsGhostValues[roleKey][addressSetsGhostIndexes[roleKey][value] - 1] == value && addressSetsGhostIndexes[roleKey][value] >= 1 && addressSetsGhostIndexes[roleKey][value] <= addressSetsGhostLength[roleKey])
      )
    );


invariant uintSetsEnumerableSetInvariant()
    (forall bytes32 roleKey.
      (forall uint256 index.
        (0 <= index && index < uintSetsGhostLength[roleKey] => to_mathint(uintSetsGhostIndexes[roleKey][uintSetsGhostValues[roleKey][index]]) == index + 1)
      )
      &&
      (forall bytes32 value.
        uintSetsGhostIndexes[roleKey][value] == 0 ||
        (uintSetsGhostValues[roleKey][uintSetsGhostIndexes[roleKey][value] - 1] == value && uintSetsGhostIndexes[roleKey][value] >= 1 && uintSetsGhostIndexes[roleKey][value] <= uintSetsGhostLength[roleKey])
      )
    );

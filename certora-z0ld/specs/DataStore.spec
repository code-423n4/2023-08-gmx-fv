///////////////// METHODS //////////////////////

// author: z0ld
methods {

    // DataStoreHarness envfree

    function sumReturnUint256Harness(uint256, int256) external returns (uint256) envfree;
    function hasRoleControllerHarness(address) external returns (bool) envfree;
    function getStringArrayHarness(bytes32, uint256) external returns (bytes1[]) envfree;

    function stringToBytes1Array(string) external returns (bytes1[]) envfree;
    function bytes32ToUint256(bytes32) external returns (uint256) envfree;
    function bytes32ToAddress(bytes32) external returns (address) envfree;
    function uint256ToBytes32(uint256) external returns (bytes32) envfree;
    function addressToBytes32(address) external returns (bytes32) envfree;
    function minusInt256ToUint256(int256) external returns (uint256) envfree;

    // DataStore    
    function setUint(bytes32, uint256) external returns (uint256);
    function removeUint(bytes32) external;
    function applyDeltaToUint(bytes32, int256, string) external returns (uint256);
    function applyDeltaToUint(bytes32, uint256) external returns (uint256);
    function applyBoundedDeltaToUint(bytes32, int256) external returns (uint256);
    function incrementUint(bytes32, uint256) external returns (uint256);
    function decrementUint(bytes32, uint256) external returns (uint256);
    function setInt(bytes32, int256) external returns (int256);
    function removeInt(bytes32) external;
    function applyDeltaToInt(bytes32, int256) external returns (int256);
    function incrementInt(bytes32, int256) external returns (int256);
    function decrementInt(bytes32, int256) external returns (int256);
    function setAddress(bytes32, address) external returns (address);
    function removeAddress(bytes32) external;
    function setBool(bytes32, bool) external returns (bool);
    function removeBool(bytes32) external;
    function setString(bytes32, string) external returns (string);
    function removeString(bytes32) external;
    function setBytes32(bytes32, bytes32) external returns (bytes32);
    function removeBytes32(bytes32) external;
    function setUintArray(bytes32, uint256[]) external;
    function removeUintArray(bytes32) external;
    function setIntArray(bytes32, int256[]) external;
    function removeIntArray(bytes32) external;
    function setAddressArray(bytes32, address[]) external;
    function removeAddressArray(bytes32) external;
    function setBoolArray(bytes32, bool[]) external;
    function removeBoolArray(bytes32) external;
    function removeStringArray(bytes32) external;
    function setBytes32Array(bytes32, bytes32[]) external;
    function removeBytes32Array(bytes32) external;
    function addBytes32(bytes32, bytes32) external;
    function removeBytes32(bytes32, bytes32) external;
    function addAddress(bytes32, address) external;
    function removeAddress(bytes32, address) external;
    function addUint(bytes32, uint256) external;
    function removeUint(bytes32, uint256) external;
    // envfree
    function getUint(bytes32) external returns (uint256) envfree;
    function getInt(bytes32) external returns (int256) envfree;
    function getAddress(bytes32) external returns (address) envfree;
    function getBool(bytes32) external returns (bool) envfree;
    function getString(bytes32) external returns (string) envfree;
    function getBytes32(bytes32) external returns (bytes32) envfree;
    function getUintArray(bytes32) external returns (uint256[]) envfree;
    function getIntArray(bytes32) external returns (int256[]) envfree;
    function getAddressArray(bytes32) external returns (address[]) envfree;
    function getBoolArray(bytes32) external returns (bool[]) envfree;
    function getStringArray(bytes32) external returns (string[]) envfree;
    function getBytes32Array(bytes32) external returns (bytes32[]) envfree;
    function containsBytes32(bytes32, bytes32) external returns (bool) envfree;
    function getBytes32Count(bytes32) external returns (uint256) envfree;
    function getBytes32ValuesAt(bytes32, uint256, uint256) external returns (bytes32[]) envfree;
    function containsAddress(bytes32, address) external returns (bool) envfree;
    function getAddressCount(bytes32) external returns (uint256) envfree;
    function getAddressValuesAt(bytes32, uint256, uint256) external returns (address[]) envfree;
    function containsUint(bytes32, uint256) external returns (bool) envfree;
    function getUintCount(bytes32) external returns (uint256) envfree;
    function getUintValuesAt(bytes32, uint256, uint256) external returns (uint256[]) envfree;

    // RoleStore
    function _.hasRole(address, bytes32) external => DISPATCHER(true);
}

///////////////// DEFINITIONS /////////////////////

definition PURE_VIEW_FUNCTIONS(method f) returns bool = f.isView || f.isPure;

definition BOOLARRAY_FUNCTIONS(method f) returns bool = 
    f.selector == sig:setBoolArray(bytes32, bool[]).selector || f.selector == sig:getBoolArray(bytes32).selector;

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

// uintValues

ghost mapping(bytes32 => uint256) ghostUintValues {
    init_state axiom forall bytes32 key. ghostUintValues[key] == 0;
}

hook Sstore currentContract.uintValues[KEY bytes32 key] uint256 val STORAGE {
    ghostUintValues[key] = val;
}

hook Sload uint256 val currentContract.uintValues[KEY bytes32 key] STORAGE {
    require(ghostUintValues[key] == val);
}

// intValues

ghost mapping(bytes32 => int256) ghostIntValues {
    init_state axiom forall bytes32 key. ghostIntValues[key] == 0;
}

hook Sstore currentContract.intValues[KEY bytes32 key] int256 val STORAGE {
    ghostIntValues[key] = val;
}

hook Sload int256 val currentContract.intValues[KEY bytes32 key] STORAGE {
    require(ghostIntValues[key] == val);
}

// addressValues

ghost mapping(bytes32 => address) ghostAddressValues {
    init_state axiom forall bytes32 key. ghostAddressValues[key] == 0;
}

hook Sstore currentContract.addressValues[KEY bytes32 key] address val STORAGE {
    ghostAddressValues[key] = val;
}

hook Sload address val currentContract.addressValues[KEY bytes32 key] STORAGE {
    require(ghostAddressValues[key] == val);
}

// boolValues

ghost mapping(bytes32 => bool) ghostBoolValues {
    init_state axiom forall bytes32 key. ghostBoolValues[key] == false;
}

hook Sstore currentContract.boolValues[KEY bytes32 key] bool val STORAGE {
    ghostBoolValues[key] = val;
}

hook Sload bool val currentContract.boolValues[KEY bytes32 key] STORAGE {
    require(ghostBoolValues[key] == val);
}

// stringValues

ghost mapping(bytes32 => mapping(uint256 => bytes1)) ghostStringValues {
    init_state axiom forall bytes32 key. forall uint256 index. ghostStringValues[key][index] == to_bytes1(0);
}

ghost mapping(bytes32 => uint256) ghostStringValuesLength {
    init_state axiom forall bytes32 key. ghostStringValuesLength[key] == 0;
    axiom forall bytes32 key. ghostStringValuesLength[key] < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.stringValues[KEY bytes32 key].(offset 0) uint256 length STORAGE {
    ghostStringValuesLength[key] = length;
}

hook Sload uint256 length currentContract.stringValues[KEY bytes32 key].(offset 0) STORAGE {
    require ghostStringValuesLength[key] == length;
}

hook Sstore currentContract.stringValues[KEY bytes32 key][INDEX uint256 index] bytes1 val STORAGE {
    ghostStringValues[key][index] = val;
}

hook Sload bytes1 val currentContract.stringValues[KEY bytes32 key][INDEX uint256 index] STORAGE {
    require(ghostStringValues[key][index] == val);
}

// bytes32Values

ghost mapping(bytes32 => bytes32) ghostBytes32Values {
    init_state axiom forall bytes32 key. ghostBytes32Values[key] == to_bytes32(0);
}

hook Sstore currentContract.bytes32Values[KEY bytes32 key] bytes32 val STORAGE {
    ghostBytes32Values[key] = val;
}

hook Sload bytes32 val currentContract.bytes32Values[KEY bytes32 key] STORAGE {
    require(ghostBytes32Values[key] == val);
}

// uintArrayValues

ghost uint256 ghostUintArrayValuesLength {
    init_state axiom ghostUintArrayValuesLength == 0;
    axiom ghostUintArrayValuesLength < 0xffffffffffffffffffffffffffffffff;
}

ghost uint256 ghostUintArrayValuesLengthPrev {
    init_state axiom ghostUintArrayValuesLengthPrev == 0;
    axiom ghostUintArrayValuesLengthPrev < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.uintArrayValues.(offset 0) uint256 length STORAGE {
    ghostUintArrayValuesLengthPrev = ghostUintArrayValuesLength;
    ghostUintArrayValuesLength = length;
}

hook Sload uint256 length currentContract.uintArrayValues.(offset 0) STORAGE {
    require ghostUintArrayValuesLength == length;
}

ghost mapping(bytes32 => mapping(uint256 => uint256)) ghostUintArrayValues {
    init_state axiom forall bytes32 key. forall uint256 index. ghostUintArrayValues[key][index] == 0;
}

hook Sstore currentContract.uintArrayValues[KEY bytes32 key][INDEX uint256 index] uint256 val STORAGE {
    ghostUintArrayValues[key][index] = val;
}

hook Sload uint256 val currentContract.uintArrayValues[KEY bytes32 key][INDEX uint256 index] STORAGE {
    require(ghostUintArrayValues[key][index] == val);
}

// intArrayValues

ghost uint256 ghostIntArrayValuesLength {
    init_state axiom ghostIntArrayValuesLength == 0;
    axiom ghostIntArrayValuesLength < 0xffffffffffffffffffffffffffffffff;
}

ghost uint256 ghostIntArrayValuesLengthPrev {
    init_state axiom ghostIntArrayValuesLengthPrev == 0;
    axiom ghostIntArrayValuesLengthPrev < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.intArrayValues.(offset 0) uint256 length STORAGE {
    ghostIntArrayValuesLengthPrev = ghostIntArrayValuesLength;
    ghostIntArrayValuesLength = length;
}

hook Sload uint256 length currentContract.intArrayValues.(offset 0) STORAGE {
    require ghostIntArrayValuesLength == length;
}

ghost mapping(bytes32 => mapping(uint256 => int256)) ghostIntArrayValues {
    init_state axiom forall bytes32 key. forall uint256 index. ghostIntArrayValues[key][index] == 0;
}

hook Sstore currentContract.intArrayValues[KEY bytes32 key][INDEX uint256 index] int256 val STORAGE {
    ghostIntArrayValues[key][index] = val;
}

hook Sload int256 val currentContract.intArrayValues[KEY bytes32 key][INDEX uint256 index] STORAGE {
    require(ghostIntArrayValues[key][index] == val);
}

// addressArrayValues

ghost uint256 ghostAddressArrayValuesLength {
    init_state axiom ghostAddressArrayValuesLength == 0;
    axiom ghostAddressArrayValuesLength < 0xffffffffffffffffffffffffffffffff;
}

ghost uint256 ghostAddressArrayValuesLengthPrev {
    init_state axiom ghostAddressArrayValuesLengthPrev == 0;
    axiom ghostAddressArrayValuesLengthPrev < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.addressArrayValues.(offset 0) uint256 length STORAGE {
    ghostAddressArrayValuesLengthPrev = ghostAddressArrayValuesLength;
    ghostAddressArrayValuesLength = length;
}

hook Sload uint256 length currentContract.addressArrayValues.(offset 0) STORAGE {
    require ghostAddressArrayValuesLength == length;
}

ghost mapping(bytes32 => mapping(uint256 => address)) ghostAddressArrayValues {
    init_state axiom forall bytes32 key. forall uint256 index. ghostAddressArrayValues[key][index] == 0;
}

hook Sstore currentContract.addressArrayValues[KEY bytes32 key][INDEX uint256 index] address val STORAGE {
    ghostAddressArrayValues[key][index] = val;
}

hook Sload address val currentContract.addressArrayValues[KEY bytes32 key][INDEX uint256 index] STORAGE {
    require(ghostAddressArrayValues[key][index] == val);
}

// boolArrayValues

ghost uint256 ghostBoolArrayValuesLength {
    init_state axiom ghostBoolArrayValuesLength == 0;
    axiom ghostBoolArrayValuesLength < 0xffffffffffffffffffffffffffffffff;
}

ghost uint256 ghostBoolArrayValuesLengthPrev {
    init_state axiom ghostBoolArrayValuesLengthPrev == 0;
    axiom ghostBoolArrayValuesLengthPrev < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.boolArrayValues.(offset 0) uint256 length STORAGE {
    ghostBoolArrayValuesLengthPrev = ghostBoolArrayValuesLength;
    ghostBoolArrayValuesLength = length;
}

hook Sload uint256 length currentContract.boolArrayValues.(offset 0) STORAGE {
    require ghostBoolArrayValuesLength == length;
}

ghost mapping(bytes32 => mapping(uint256 => bool)) ghostBoolArrayValues {
    init_state axiom forall bytes32 key. forall uint256 index. ghostBoolArrayValues[key][index] == false;
}

hook Sstore currentContract.boolArrayValues[KEY bytes32 key][INDEX uint256 index] bool val STORAGE {
    ghostBoolArrayValues[key][index] = val;
}

hook Sload bool val currentContract.boolArrayValues[KEY bytes32 key][INDEX uint256 index] STORAGE {
    require(ghostBoolArrayValues[key][index] == val);
}

// stringArrayValues

ghost uint256 ghostStringArrayValuesLength {
    init_state axiom ghostStringArrayValuesLength == 0;
    axiom ghostStringArrayValuesLength < 0xffffffffffffffffffffffffffffffff;
}

ghost uint256 ghostStringArrayValuesLengthPrev {
    init_state axiom ghostStringArrayValuesLengthPrev == 0;
    axiom ghostStringArrayValuesLengthPrev < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.stringArrayValues.(offset 0) uint256 length STORAGE {
    ghostStringArrayValuesLengthPrev = ghostStringArrayValuesLength;
    ghostStringArrayValuesLength = length;
}

hook Sload uint256 length currentContract.stringArrayValues.(offset 0) STORAGE {
    require ghostStringArrayValuesLength == length;
}

ghost mapping(bytes32 => mapping(uint256 => mapping(uint256 => bytes1))) ghostStringArrayValues {
    init_state axiom forall bytes32 key. forall uint256 index. forall uint256 bindex. ghostStringArrayValues[key][index][bindex] == to_bytes1(0);
}

hook Sstore currentContract.stringArrayValues[KEY bytes32 key][INDEX uint256 index][INDEX uint256 bindex] bytes1 val STORAGE {
    ghostStringArrayValues[key][index][bindex] = val;
}

hook Sload bytes1 val currentContract.stringArrayValues[KEY bytes32 key][INDEX uint256 index][INDEX uint256 bindex] STORAGE {
    require(ghostStringArrayValues[key][index][bindex] == val);
}

// bytes32ArrayValues

ghost uint256 ghostBytes32ArrayValuesLength {
    init_state axiom ghostBytes32ArrayValuesLength == 0;
    axiom ghostBytes32ArrayValuesLength < 0xffffffffffffffffffffffffffffffff;
}

ghost uint256 ghostBytes32ArrayValuesLengthPrev {
    init_state axiom ghostBytes32ArrayValuesLengthPrev == 0;
    axiom ghostBytes32ArrayValuesLengthPrev < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.bytes32ArrayValues.(offset 0) uint256 length STORAGE {
    ghostBytes32ArrayValuesLengthPrev = ghostBytes32ArrayValuesLength;
    ghostBytes32ArrayValuesLength = length;
}

hook Sload uint256 length currentContract.bytes32ArrayValues.(offset 0) STORAGE {
    require ghostBytes32ArrayValuesLength == length;
}

ghost mapping(bytes32 => mapping(uint256 => bytes32)) ghostBytes32ArrayValues {
    init_state axiom forall bytes32 key. forall uint256 index. ghostBytes32ArrayValues[key][index] == to_bytes32(0);
}

hook Sstore currentContract.bytes32ArrayValues[KEY bytes32 key][INDEX uint256 index] bytes32 val STORAGE {
    ghostBytes32ArrayValues[key][index] = val;
}

hook Sload bytes32 val currentContract.bytes32ArrayValues[KEY bytes32 key][INDEX uint256 index] STORAGE {
    require(ghostBytes32ArrayValues[key][index] == val);
}

// bytes32Sets

ghost mapping(bytes32 => uint256) ghostBytes32SetsLength {
    init_state axiom forall bytes32 key. ghostBytes32SetsLength[key] == 0;
    axiom forall bytes32 key. ghostBytes32SetsLength[key] < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.bytes32Sets[KEY bytes32 key].(offset 0) uint256 length STORAGE {
    ghostBytes32SetsLength[key] = length;
}

hook Sload uint256 length currentContract.bytes32Sets[KEY bytes32 key].(offset 0) STORAGE {
    require ghostBytes32SetsLength[key] == length;
}

ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostBytes32SetsIndexes {
    init_state axiom forall bytes32 key. forall bytes32 val. ghostBytes32SetsIndexes[key][val] == 0;
}

hook Sstore currentContract.bytes32Sets[KEY bytes32 key]._inner._indexes[KEY bytes32 val] uint256 index STORAGE {
    ghostBytes32SetsIndexes[key][val] = index;
}

hook Sload uint256 index currentContract.bytes32Sets[KEY bytes32 key]._inner._indexes[KEY bytes32 val] STORAGE {
    require(ghostBytes32SetsIndexes[key][val] == index);
}

ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostBytes32SetsValues {
    init_state axiom forall bytes32 key. forall mathint index. ghostBytes32SetsValues[key][index] == to_bytes32(0);
}

hook Sstore currentContract.bytes32Sets[KEY bytes32 key]._inner._values[INDEX uint256 index] bytes32 val STORAGE {
    ghostBytes32SetsValues[key][index] = val;
}

hook Sload bytes32 val currentContract.bytes32Sets[KEY bytes32 key]._inner._values[INDEX uint256 index] STORAGE {
    require(ghostBytes32SetsValues[key][index] == val);
}

// addressSets

ghost mapping(bytes32 => uint256) ghostAddressSetsLength {
    init_state axiom forall bytes32 key. ghostAddressSetsLength[key] == 0;
    axiom forall bytes32 key. ghostAddressSetsLength[key] < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.addressSets[KEY bytes32 key].(offset 0) uint256 length STORAGE {
    ghostAddressSetsLength[key] = length;
}

hook Sload uint256 length currentContract.addressSets[KEY bytes32 key].(offset 0) STORAGE {
    require ghostAddressSetsLength[key] == length;
}

ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostAddressSetsIndexes {
    init_state axiom forall bytes32 key. forall bytes32 val. ghostAddressSetsIndexes[key][val] == 0;
}

hook Sstore currentContract.addressSets[KEY bytes32 key]._inner._indexes[KEY bytes32 val] uint256 index STORAGE {
    ghostAddressSetsIndexes[key][val] = index;
}

hook Sload uint256 index currentContract.addressSets[KEY bytes32 key]._inner._indexes[KEY bytes32 val] STORAGE {
    require(ghostAddressSetsIndexes[key][val] == index);
}

ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostAddressSetsValues {
    init_state axiom forall bytes32 key. forall mathint index. ghostAddressSetsValues[key][index] == to_bytes32(0);
}

hook Sstore currentContract.addressSets[KEY bytes32 key]._inner._values[INDEX uint256 index] bytes32 val STORAGE {
    ghostAddressSetsValues[key][index] = val;
}

hook Sload bytes32 val currentContract.addressSets[KEY bytes32 key]._inner._values[INDEX uint256 index] STORAGE {
    require(ghostAddressSetsValues[key][index] == val);
}

// uintSets

ghost mapping(bytes32 => uint256) ghostUintSetsLength {
    init_state axiom forall bytes32 key. ghostUintSetsLength[key] == 0;
    axiom forall bytes32 key. ghostUintSetsLength[key] < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.uintSets[KEY bytes32 key].(offset 0) uint256 length STORAGE {
    ghostUintSetsLength[key] = length;
}

hook Sload uint256 length currentContract.uintSets[KEY bytes32 key].(offset 0) STORAGE {
    require ghostUintSetsLength[key] == length;
}

ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostUintSetsIndexes {
    init_state axiom forall bytes32 key. forall bytes32 val. ghostUintSetsIndexes[key][val] == 0;
}

hook Sstore currentContract.uintSets[KEY bytes32 key]._inner._indexes[KEY bytes32 val] uint256 index STORAGE {
    ghostUintSetsIndexes[key][val] = index;
}

hook Sload uint256 index currentContract.uintSets[KEY bytes32 key]._inner._indexes[KEY bytes32 val] STORAGE {
    require(ghostUintSetsIndexes[key][val] == index);
}

ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostUintSetsValues {
    init_state axiom forall bytes32 key. forall mathint index. ghostUintSetsValues[key][index] == to_bytes32(0);
}

hook Sstore currentContract.uintSets[KEY bytes32 key]._inner._values[INDEX uint256 index] bytes32 val STORAGE {
    ghostUintSetsValues[key][index] = val;
}

hook Sload bytes32 val currentContract.uintSets[KEY bytes32 key]._inner._values[INDEX uint256 index] STORAGE {
    require(ghostUintSetsValues[key][index] == val);
}

///////////////// SETUP INVARIANTS ////////////////

// uintArrayValues
invariant setUintArrayValuesInvariant() (ghostUintArrayValuesLength == ghostUintArrayValuesLengthPrev => ghostUintArrayValuesLength == 0)
    && (ghostUintArrayValuesLength > ghostUintArrayValuesLengthPrev => 1 == assert_uint256(ghostUintArrayValuesLength - ghostUintArrayValuesLengthPrev))
    && (ghostUintArrayValuesLength < ghostUintArrayValuesLengthPrev => 1 == assert_uint256(ghostUintArrayValuesLengthPrev - ghostUintArrayValuesLength))
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

// intArrayValues
invariant setIntArrayValuesInvariant() (ghostIntArrayValuesLength == ghostIntArrayValuesLengthPrev => ghostIntArrayValuesLength == 0)
    && (ghostIntArrayValuesLength > ghostIntArrayValuesLengthPrev => 1 == assert_uint256(ghostIntArrayValuesLength - ghostIntArrayValuesLengthPrev))
    && (ghostIntArrayValuesLength < ghostIntArrayValuesLengthPrev => 1 == assert_uint256(ghostIntArrayValuesLengthPrev - ghostIntArrayValuesLength))
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

// addressArrayValues
invariant setAddressArrayValuesInvariant() (ghostAddressArrayValuesLength == ghostAddressArrayValuesLengthPrev => ghostAddressArrayValuesLength == 0)
    && (ghostAddressArrayValuesLength > ghostAddressArrayValuesLengthPrev => 1 == assert_uint256(ghostAddressArrayValuesLength - ghostAddressArrayValuesLengthPrev))
    && (ghostAddressArrayValuesLength < ghostAddressArrayValuesLengthPrev => 1 == assert_uint256(ghostAddressArrayValuesLengthPrev - ghostAddressArrayValuesLength))
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

// boolArrayValues
invariant setBoolArrayValuesInvariant() (ghostBoolArrayValuesLength == ghostBoolArrayValuesLengthPrev => ghostBoolArrayValuesLength == 0)
    && (ghostBoolArrayValuesLength > ghostBoolArrayValuesLengthPrev => 1 == assert_uint256(ghostBoolArrayValuesLength - ghostBoolArrayValuesLengthPrev))
    && (ghostBoolArrayValuesLength < ghostBoolArrayValuesLengthPrev => 1 == assert_uint256(ghostBoolArrayValuesLengthPrev - ghostBoolArrayValuesLength))
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

// stringArrayValues
invariant setStringArrayValuesInvariant() (ghostStringArrayValuesLength == ghostStringArrayValuesLengthPrev => ghostStringArrayValuesLength == 0)
    && (ghostStringArrayValuesLength > ghostStringArrayValuesLengthPrev => 1 == assert_uint256(ghostStringArrayValuesLength - ghostStringArrayValuesLengthPrev))
    && (ghostStringArrayValuesLength < ghostStringArrayValuesLengthPrev => 1 == assert_uint256(ghostStringArrayValuesLengthPrev - ghostStringArrayValuesLength))
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

// bytes32ArrayValues
invariant setBytes32ArrayValuesInvariant() (ghostBytes32ArrayValuesLength == ghostBytes32ArrayValuesLengthPrev => ghostBytes32ArrayValuesLength == 0)
    && (ghostBytes32ArrayValuesLength > ghostBytes32ArrayValuesLengthPrev => 1 == assert_uint256(ghostBytes32ArrayValuesLength - ghostBytes32ArrayValuesLengthPrev))
    && (ghostBytes32ArrayValuesLength < ghostBytes32ArrayValuesLengthPrev => 1 == assert_uint256(ghostBytes32ArrayValuesLengthPrev - ghostBytes32ArrayValuesLength))
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

//  This is the main invariant stating that the indexes and values always match:
//        values[indexes[v] - 1] = v for all values v in the set
//    and indexes[values[i]] = i+1 for all valid indexes i.

// bytes32Sets
invariant setBytes32SetsInvariant() forall bytes32 key.
    (forall uint256 index. 0 <= index && index < ghostBytes32SetsLength[key] => to_mathint(ghostBytes32SetsIndexes[key][ghostBytes32SetsValues[key][index]]) == index + 1)
    && (forall bytes32 val. ghostBytes32SetsIndexes[key][val] == 0 || 
         (ghostBytes32SetsValues[key][ghostBytes32SetsIndexes[key][val] - 1] == val && ghostBytes32SetsIndexes[key][val] >= 1 && ghostBytes32SetsIndexes[key][val] <= ghostBytes32SetsLength[key])) 
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

// addressSets
invariant setAddressSetsInvariant() forall bytes32 key.
    (forall uint256 index. 0 <= index && index < ghostAddressSetsLength[key] => to_mathint(ghostAddressSetsIndexes[key][ghostAddressSetsValues[key][index]]) == index + 1)
    && (forall bytes32 val. ghostAddressSetsIndexes[key][val] == 0 || 
         (ghostAddressSetsValues[key][ghostAddressSetsIndexes[key][val] - 1] == val && ghostAddressSetsIndexes[key][val] >= 1 && ghostAddressSetsIndexes[key][val] <= ghostAddressSetsLength[key]))
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

// uintSets
invariant setUintSetsInvariant() forall bytes32 key.
    (forall uint256 index. 0 <= index && index < ghostUintSetsLength[key] => to_mathint(ghostUintSetsIndexes[key][ghostUintSetsValues[key][index]]) == index + 1)
    && (forall bytes32 val. ghostUintSetsIndexes[key][val] == 0 || 
         (ghostUintSetsValues[key][ghostUintSetsIndexes[key][val] - 1] == val && ghostUintSetsIndexes[key][val] >= 1 && ghostUintSetsIndexes[key][val] <= ghostUintSetsLength[key]))
    filtered { f -> !BOOLARRAY_FUNCTIONS(f) }

///////////////// PROPERTIES //////////////////////

// [2-3] only CONTROLLER could modify state
rule onlyControllerCouldModifyState(env e, method f, calldataarg args) filtered {
    f -> !PURE_VIEW_FUNCTIONS(f) 
        // Exclude it because of https://discord.com/channels/795999272293236746/1143131362132504646/1143131362132504646
        && !BOOLARRAY_FUNCTIONS(f)
} {

    bool isController = hasRoleControllerHarness(e.msg.sender);

    storage before = lastStorage;

    f(e, args);

    storage after = lastStorage;

    assert(before[currentContract] != after[currentContract] => isController);
}

// [1] integrity

rule getUintIntegrity(bytes32 key) {    
    assert(getUint(key) == ghostUintValues[key]);
}

rule setUintIntegrity(env e, bytes32 key, uint256 value) {    
    uint256 result = setUint(e, key, value);
    assert(result == ghostUintValues[key] && ghostUintValues[key] == value);
}

rule removeUintIntegrity(env e, bytes32 key) {    
    require(ghostUintValues[key] != 0);
    removeUint(e, key);
    assert(ghostUintValues[key] == 0);
}

rule applyDeltaToUintIntegrity(env e, bytes32 key, int256 value, string errorMessage) {

    uint256 currValue = ghostUintValues[key];

    uint256 result = applyDeltaToUint@withrevert(e, key, value, errorMessage);
    bool reverted = lastReverted;

    assert(value < 0 && minusInt256ToUint256(value) > currValue => reverted); 

    assert(!reverted && value < 0 => minusInt256ToUint256(value) <= currValue);
    assert(!reverted => result == ghostUintValues[key] && result == sumReturnUint256Harness(currValue, value));
}

rule applyDeltaToUint2Integrity(env e, bytes32 key, uint256 value) {

    uint256 currValue = ghostUintValues[key];

    uint256 result = applyDeltaToUint(e, key, value);
    
    assert(result == ghostUintValues[key] && result == require_uint256(currValue + value));
}

rule applyBoundedDeltaToUintIntegrity(env e, bytes32 key, int256 value) {

    uint256 uintValue = ghostUintValues[key];

    uint256 result = applyBoundedDeltaToUint(e, key, value);

    assert(result == ghostUintValues[key]);
    assert(value < 0 && minusInt256ToUint256(value) > uintValue
        ? result == 0
        : result == sumReturnUint256Harness(uintValue, value)
    );
}

rule incrementUintIntegrity(env e, bytes32 key, uint256 value) {
    uint256 uintValue = ghostUintValues[key];
    uint256 result = incrementUint(e, key, value);
    assert(result == ghostUintValues[key] && result == require_uint256(uintValue + value));
}

rule decrementUintIntegrity(env e, bytes32 key, uint256 value) {
    uint256 uintValue = ghostUintValues[key];
    uint256 result = decrementUint(e, key, value);
    assert(result == ghostUintValues[key] && result == require_uint256(uintValue - value));
}

rule getIntIntegrity(bytes32 key) {    
    assert(getInt(key) == ghostIntValues[key]);
}

rule setIntIntegrity(env e, bytes32 key, int256 value) {   
    int result = setInt(e, key, value); 
    assert(result == ghostIntValues[key] && ghostIntValues[key] == value);
}

rule removeIntIntegrity(env e, bytes32 key) {   
    require(ghostIntValues[key] != 0); 
    removeInt(e, key);
    assert(ghostIntValues[key] == 0);
}

rule applyDeltaToIntIntegrity(env e, bytes32 key, int256 value) {
    int256 currValue = ghostIntValues[key];
    int256 result = applyDeltaToInt(e, key, value);
    assert(result == ghostIntValues[key] && result == require_int256(currValue + value));
}

rule incrementIntIntegrity(env e, bytes32 key, int256 value) {
    int256 intValue = ghostIntValues[key];
    int256 result = incrementInt(e, key, value);
    assert(result == ghostIntValues[key] && result == require_int256(intValue + value));
}

rule decrementIntIntegrity(env e, bytes32 key, int256 value) {
    int256 intValue = ghostIntValues[key];
    int256 result = decrementInt(e, key, value);
    assert(result == ghostIntValues[key] && result == require_int256(intValue - value));
}

rule getAddressIntegrity(bytes32 key) {    
    assert(getAddress(key) == ghostAddressValues[key]);
}

rule setAddressIntegrity(env e, bytes32 key, address value) {   
    address result = setAddress(e, key, value); 
    assert(result == ghostAddressValues[key] && ghostAddressValues[key] == value);
}

rule removeAddressIntegrity(env e, bytes32 key) {   
    require(ghostAddressValues[key] != 0); 
    removeAddress(e, key);
    assert(ghostAddressValues[key] == 0);
}

rule getBytes32Integrity(bytes32 key) {    
    assert(getBytes32(key) == ghostBytes32Values[key]);
}

rule setBytes32Integrity(env e, bytes32 key, bytes32 value) {   
    bytes32 result = setBytes32(e, key, value); 
    assert(result == ghostBytes32Values[key] && ghostBytes32Values[key] == value);
}

rule removeBytes32Integrity(env e, bytes32 key) {   
    require(ghostBytes32Values[key] != to_bytes32(0)); 
    removeBytes32(e, key);
    assert(ghostBytes32Values[key] == to_bytes32(0));
}

rule getUintArrayIntegrity(bytes32 key) {    
    uint256[] a = getUintArray(key);
    uint256 i;
    require(i < a.length);
    assert(a[i] == ghostUintArrayValues[key][i]);
}

rule setUintArrayIntegrity(env e, bytes32 key, uint256[] value) {
    setUintArray(e, key, value);
    uint256 i;
    require(i < value.length);
    assert(value[i] == ghostUintArrayValues[key][i]);
}

rule removeUintArrayIntegrity(env e, bytes32 key) {   
    removeUintArray(e, key);
    uint256[] a = getUintArray(key);
    assert(a.length == 0);
}

rule getIntArrayIntegrity(bytes32 key) {    
    int256[] a = getIntArray(key);
    uint256 i;
    require(i < a.length);
    assert(a[i] == ghostIntArrayValues[key][i]);
}

rule setIntArrayIntegrity(env e, bytes32 key, int256[] value) {
    setIntArray(e, key, value);
    uint256 i;
    require(i < value.length);
    assert(value[i] == ghostIntArrayValues[key][i]);
}

rule removeIntArrayIntegrity(env e, bytes32 key) {   
    removeIntArray(e, key);
    int256[] a = getIntArray(key);
    assert(a.length == 0);
}

rule getAddressArrayIntegrity(bytes32 key) {    
    address[] a = getAddressArray(key);
    uint256 i;
    require(i < a.length);
    assert(a[i] == ghostAddressArrayValues[key][i]);
}

rule setAddressArrayIntegrity(env e, bytes32 key, address[] value) {
    setAddressArray(e, key, value);
    uint256 i;
    require(i < value.length);
    assert(value[i] == ghostAddressArrayValues[key][i]);
}

rule removeAddressArrayIntegrity(env e, bytes32 key) {  
    removeAddressArray(e, key);
    address[] a = getAddressArray(key);
    assert(a.length == 0);
}

rule getBytes32ArrayIntegrity(bytes32 key) {    
    bytes32[] a = getBytes32Array(key);
    uint256 i;
    require(i < a.length);
    assert(a[i] == ghostBytes32ArrayValues[key][i]);
}

rule setBytes32ArrayIntegrity(env e, bytes32 key, bytes32[] value) {
    setBytes32Array(e, key, value);
    uint256 i;
    require(i < value.length);
    assert(value[i] == ghostBytes32ArrayValues[key][i]);
}

rule removeBytes32ArrayIntegrity(env e, bytes32 key) {   
    removeBytes32Array(e, key);
    bytes32[] a = getBytes32Array(key);
    assert(a.length == 0);
}

rule containsBytes32Integrity(bytes32 key, bytes32 value) {    
    assert(containsBytes32(key, value) == (ghostBytes32SetsIndexes[key][value] != 0));
}

rule getBytes32CountIntegrity(bytes32 key) {    
    assert(getBytes32Count(key) == ghostBytes32SetsLength[key]);
}

rule getBytes32ValuesAtIntegrity(bytes32 key, uint256 start, uint256 end) {    

    require(end < ghostBytes32SetsLength[key]);
    require(start < end);

    uint256 i;
    require(i < assert_uint256(end - start));

    bytes32[] a = getBytes32ValuesAt(key, start, end);
    assert(a[i] == ghostBytes32SetsValues[key][start + i]);
}

rule addBytes32Integrity(env e, bytes32 key, bytes32 value) {
    
    uint256 count = ghostBytes32SetsLength[key];
    bool contains = containsBytes32(key, value);

    addBytes32(e, key, value);
    
    assert(containsBytes32(key, value));
    assert(contains 
        ? ghostBytes32SetsLength[key] == count 
        : ghostBytes32SetsLength[key] == assert_uint256(count + 1)
    );
}

rule removeBytes32ValueIntegrity(env e, bytes32 key, bytes32 value) {

    uint256 count = ghostBytes32SetsLength[key];
    bool contains = containsBytes32(key, value);

    removeBytes32(e, key, value);
    
    assert(containsBytes32(key, value) == false);
    assert(contains == false
        ? ghostBytes32SetsLength[key] == count 
        : ghostBytes32SetsLength[key] == assert_uint256(count - 1)
    );
}

rule containsAddressIntegrity(bytes32 key, address value) {    
    assert(containsAddress(key, value) == (ghostAddressSetsIndexes[key][addressToBytes32(value)] != 0));
}

rule getAddressCountIntegrity(bytes32 key) {    
    assert(getAddressCount(key) == ghostAddressSetsLength[key]);
}

rule getAddressValuesAtIntegrity(bytes32 key, uint256 start, uint256 end) {    

    require(end < ghostAddressSetsLength[key]);
    require(start < end);

    uint256 i;
    require(i < assert_uint256(end - start));

    address[] a = getAddressValuesAt(key, start, end);
    assert(a[i] == bytes32ToAddress(ghostAddressSetsValues[key][start + i]));
}

rule addAddressIntegrity(env e, bytes32 key, address value) {
    
    uint256 count = ghostAddressSetsLength[key];
    bool contains = containsAddress(key, value);

    addAddress(e, key, value);
    
    assert(containsAddress(key, value));
    assert(contains 
        ? ghostAddressSetsLength[key] == count 
        : ghostAddressSetsLength[key] == assert_uint256(count + 1)
    );
}

rule removeAddressValueIntegrity(env e, bytes32 key, address value) {

    uint256 count = ghostAddressSetsLength[key];
    bool contains = containsAddress(key, value);

    removeAddress(e, key, value);
    
    assert(containsAddress(key, value) == false);
    assert(contains == false
        ? ghostAddressSetsLength[key] == count 
        : ghostAddressSetsLength[key] == assert_uint256(count - 1)
    );
}

rule containsUintIntegrity(bytes32 key, uint256 value) {    
    assert(containsUint(key, value) == (ghostUintSetsIndexes[key][uint256ToBytes32(value)] != 0));
}

rule getUintCountCountIntegrity(bytes32 key) {    
    assert(getUintCount(key) == ghostUintSetsLength[key]);
}

rule getUintValuesAtIntegrity(bytes32 key, uint256 start, uint256 end) {    

    require(end < ghostUintSetsLength[key]);
    require(start < end);

    uint256 i;
    require(i < assert_uint256(end - start));

    uint256[] a = getUintValuesAt(key, start, end);
    assert(a[i] == bytes32ToUint256(ghostUintSetsValues[key][start + i]));
}

rule addUintIntegrity(env e, bytes32 key, uint256 value) {
    
    uint256 count = ghostUintSetsLength[key];
    bool contains = containsUint(key, value);

    addUint(e, key, value);
    
    assert(containsUint(key, value));
    assert(contains 
        ? ghostUintSetsLength[key] == count 
        : ghostUintSetsLength[key] == assert_uint256(count + 1)
    );
}

rule removeUintValueIntegrity(env e, bytes32 key, uint256 value) {

    uint256 count = ghostUintSetsLength[key];
    bool contains = containsUint(key, value);

    removeUint(e, key, value);
    
    assert(containsUint(key, value) == false);
    assert(contains == false
        ? ghostUintSetsLength[key] == count 
        : ghostUintSetsLength[key] == assert_uint256(count - 1)
    );
}

/*
// hooking `mapping(bytes32 => bool)` issue 
// https://discord.com/channels/795999272293236746/1145391840477069322

rule getBoolIntegrity(bytes32 key) {    
    assert(getBool(key) == ghostBoolValues[key]); 
}

rule setBoolIntegrity(env e, bytes32 key, bool value) {   
    bool result = setBool(e, key, value); 
    assert(result == ghostBoolValues[key] && ghostBoolValues[key] == value);
}

rule removeBoolIntegrity(env e, bytes32 key) {    
    require(ghostBoolValues[key] == true);
    removeBool(e, key);
    assert(ghostBoolValues[key] == false);
}

rule getBoolArrayIntegrity(bytes32 key) {   
    bool[] a = getBoolArray(key);
    uint256 i;
    require(i < a.length);
    assert(a[i] == ghostBoolArrayValues[key][i]); 
}

rule setBoolArrayIntegrity(env e, bytes32 key, bool[] value) {
    setBoolArray(e, key, value);
    uint256 i;
    require(i < value.length);
    assert(value[i] == ghostBoolArrayValues[key][i]);
}

rule removeBoolArrayIntegrity(env e, bytes32 key) {   
    removeBoolArray(e, key);
    bool[] a = getBoolArray(key);
    assert(a.length == 0);
}
*/

/*
// hooking `string` issue
// https://discord.com/channels/795999272293236746/1145423162037764260

rule getStringIntegrity(bytes32 key) { 
    bytes1[] a = stringToBytes1Array(getString(key));
    uint256 i;
    require(i < a.length);
    assert(a[i] == ghostStringValues[key][i]); 
}

rule setStringIntegrity(env e, bytes32 key, string value) {   

    bytes1[] a = stringToBytes1Array(value);
    uint256 i;
    require(i < a.length);

    string result = setString(e, key, value); 

    bytes1[] b = stringToBytes1Array(result);
    uint256 j;
    require(j < b.length);

    assert(a[i] == ghostStringValues[key][i] && b[i] == a[i]);
}

rule removeStringIntegrity(env e, bytes32 key) {   
    require(ghostStringValues[key][0] != to_bytes1(0)); 
    removeString(e, key);
    assert(ghostStringValues[key][0] == to_bytes1(0));
}

rule getStringArrayIntegrity(bytes32 key) {    
    uint256 si;
    bytes1[] a = getStringArrayHarness(key, si);
    uint256 i;
    require(i < a.length);
    sassert(a[i] == ghostStringArrayValues[key][si][i]);
}
*/

// [] possibility

rule applyDeltaToUintPossibility(env e, bytes32 key, int256 value, string errorMessage) {

    uint256 currValue = ghostUintValues[key];

    uint256 result = applyDeltaToUint(e, key, value, errorMessage);

    satisfy(value < 0 && minusInt256ToUint256(value) == currValue); 
}

rule notRevertedPossibility(env e, method f, calldataarg args) filtered {
    f -> !BOOLARRAY_FUNCTIONS(f) 
} {
    f@withrevert(e, args);
    satisfy(!lastReverted); 
}

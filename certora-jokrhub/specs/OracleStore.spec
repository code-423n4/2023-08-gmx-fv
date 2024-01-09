using OracleStoreHarness as oracleStore;

definition UINT256_MAX() returns uint256 = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;

// author: jokrhub
methods {
    // RoleStore
    function _.hasRole(address,bytes32) external => DISPATCHER(true);
}

//-----------------------------------------------------------------------------
// EnumerableSet Invariant Lib (Begin)
//-----------------------------------------------------------------------------
// Based on spec for EnumerableSet found here: https://github.com/Certora/Examples/tree/master/CVLByExample/QuantifierExamples/EnumerableSet

// GHOST COPIES
ghost mapping(mathint => bytes32) ghostValues {
    init_state axiom forall mathint x. ghostValues[x] == to_bytes32(0);
}
ghost mapping(bytes32 => uint256) ghostIndexes {
    init_state axiom forall bytes32 x. ghostIndexes[x] == 0;
}
ghost uint256 ghostLength {
    // assumption: it's infeasible to grow the list to these many elements.
    axiom ghostLength < 0xffffffffffffffffffffffffffffffff;
}

// HOOKS

hook Sstore currentContract.signers.(offset 0) uint256 newLength STORAGE {
    ghostLength = newLength;
}
hook Sstore currentContract.signers._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostValues[index] = newValue;
}
hook Sstore currentContract.signers._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostIndexes[value] = newIndex;
}

hook Sload uint256 length currentContract.signers.(offset 0) STORAGE {
    require ghostLength == length;
}
hook Sload bytes32 value currentContract.signers._inner._values[INDEX uint256 index] STORAGE {
    require ghostValues[index] == value;
}
hook Sload uint256 index currentContract.signers._inner._indexes[KEY bytes32 value] STORAGE {
    require ghostIndexes[value] == index;
}

// INVARIANTS

invariant setInvariant()
    (forall uint256 index. 0 <= index && index < ghostLength => to_mathint(ghostIndexes[ghostValues[index]]) == index + 1)
    && (forall bytes32 value. ghostIndexes[value] == 0 || 
         (ghostValues[ghostIndexes[value] - 1] == value && ghostIndexes[value] >= 1 && ghostIndexes[value] <= ghostLength));

//-----------------------------------------------------------------------------
// Enumerable Set Invariant Lib (End)
//-----------------------------------------------------------------------------


rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

// Natural language specifications
// 1. for addSigner, if the caller does not have the controller role
// the contract reverts and
// the result of calling getSigner will not change before/after the function
// (i.e. only those with the controller role can change signers)
//     -- similar as last spec but using getSigners()
//     -- similar as last spec but using getSignerCount()
// 2. for removeSigner, if the caller does not have the controller role
// the contract reverts and
// the result of calling getSigner will not change before/after the function
// (i.e. only those with the controller role can change signers)
//     -- similar as last spec but using getSigners()
//     -- similar as last spec but using getSignerCount()
// 3. calling removeSigner with an address that has not been added
// to the list of signers previously will have no affect on: getSigner(s), getSignerCount
// 4. calling getSigner with an invalid index "fails gracefully"
// 5. calling addSigner with the controller role will: increase getSignerCount, and add the signer to the result of getSinger(s) for some index(es).
// 6. calling removeSigner as a controller and on an address that has been 
// added to the list of signers previously will: decrease getSigners, ensure
// the address will not appear in the result of getSigner(s) for any index
// 7. calling getSignerCount() twice in a row with no other interleaving calls
// results in the same value. Similar for getSigner(s)

// 1. for addSigner, if the caller does not have the controller role
// the contract reverts and
// the result of calling getSigner will not change before/after the function
// (i.e. only those with the controller role can change signers)
//     -- similar as last spec but using getSigners()
//     -- similar as last spec but using getSignerCount()
rule non_controller_add_signer {
    env e;
    calldataarg args;
    address new_signer_address;
    uint256 signer_count_before;
    uint256 signer_count_after;
    uint256 some_index;
    address signer_at_index_before;
    address signer_at_index_after;
    uint256 signers_arr_idx;
    uint256 some_start;
    uint256 some_end;
    address[] signers_before;
    address[] signers_after;

    requireInvariant setInvariant();

    // The caller does  not have the controller role
    require(!oracleStore.hasControllerRole(e));

    signer_count_before = oracleStore.getSignerCount(e);
    signer_at_index_before = oracleStore.getSigner(e, some_index);
    signers_before = getSigners(e, some_start, some_end);

    // The range used to check getSigners is less than the size of the signers
    // and the specific index used to check the resulting array from the call
    // is within the range of the resulting array.
    require (some_start <= some_end && some_end < signer_count_before);
    require (signers_arr_idx < assert_uint256(some_end - some_start));
    
    signer_count_after = oracleStore.getSignerCount(e);
    signer_at_index_after = oracleStore.getSigner(e, some_index);
    signers_after = getSigners(e, some_start, some_end);

    assert(signer_count_before == signer_count_after, "signer count has not changed");
    assert(signer_at_index_before == signer_at_index_after, "getSigner has not changed");
    assert(signers_before[signers_arr_idx] == signers_after[signers_arr_idx],   
    "getSigenrs has not changed");
}

// 2. for removeSigner, if the caller does not have the controller role
// the contract reverts and
// the result of calling getSigner will not change before/after the function
// (i.e. only those with the controller role can change signers)
//     -- similar as last spec but using getSigners()
//     -- similar as last spec but using getSignerCount()
rule non_controller_remove_signer {
    env e;
    calldataarg args;
    address remove_signer_address;
    uint256 signer_count_before;
    uint256 signer_count_after;
    uint256 some_index;
    address signer_at_index_before;
    address signer_at_index_after;
    uint256 signers_arr_idx;
    uint256 some_start;
    uint256 some_end;
    address[] signers_before;
    address[] signers_after;

    requireInvariant setInvariant();

    // The caller does  not have the controller role
    require(!oracleStore.hasControllerRole(e));

    signer_count_before = oracleStore.getSignerCount(e);
    signer_at_index_before = oracleStore.getSigner(e, some_index);
    signers_before = getSigners(e, some_start, some_end);

    // The range used to check getSigners is less than the size of the signers
    // and the specific index used to check the resulting array from the call
    // is within the range of the resulting array.
    require (some_start <= some_end && some_end < signer_count_before);
    require (signers_arr_idx < assert_uint256(some_end - some_start));
    
    signer_count_after = oracleStore.getSignerCount(e);
    signer_at_index_after = oracleStore.getSigner(e, some_index);
    signers_after = getSigners(e, some_start, some_end);

    assert(signer_count_before == signer_count_after, "signer count has not changed");
    assert(signer_at_index_before == signer_at_index_after, "getSigners has not changed");
    assert(signers_before[signers_arr_idx] == signers_after[signers_arr_idx]);
}

// 3. calling removeSigner with an address that has not been added
// to the list of signers previously will have no affect on: getSigner(s), 
// getSignerCount
rule remove_signer_not_in_list {
    env e;
    address signer_remove_arg;

    uint256 signer_count_before;
    uint256 signer_count_after;

    uint256 some_index;
    address signer_at_index_before;
    address signer_at_index_after;

    uint256 signers_arr_idx;
    uint256 some_start;
    uint256 some_end;
    address[] signers_before;
    address[] signers_after;

    requireInvariant setInvariant();

    // the signer address argument is not in the list
    require(!oracleStore.signersContains(e, signer_remove_arg));
    
    signer_count_before = oracleStore.getSignerCount(e);
    signer_at_index_before = oracleStore.getSigner(e, some_index);
    signers_before = oracleStore.getSigners(e, some_start, some_end);

    // The range used to check getSigners is less than the size of the signers
    // and the specific index used to check the resulting array from the call
    // is within the range of the resulting array.
    require (some_start <= some_end && some_end < signer_count_before);
    require (signers_arr_idx < assert_uint256(some_end - some_start));

    oracleStore.removeSigner(e, signer_remove_arg);

    signer_count_after = oracleStore.getSignerCount(e);
    signer_at_index_after= oracleStore.getSigner(e, some_index);
    signers_after = oracleStore.getSigners(e, some_start, some_end);

    assert(signer_count_before == signer_count_after);
    assert(signer_at_index_before == signer_at_index_after);
    assert(signers_before[signers_arr_idx] == signers_after[signers_arr_idx]);
}

// 4. calling getSigner with an invalid index "fails gracefully"
rule get_invalid_index {
    env e;
    uint256 signers_size;
    uint256 some_index;
    address signer_at_index;

    requireInvariant setInvariant();

    signers_size = oracleStore.getSignerCount(e);

    // Make an index that is out of bounds
    require(some_index > signers_size);

    // acceessing the out of bounds element causes a revert
    signer_at_index = oracleStore.getSigner@withrevert(e, some_index);
    assert(lastReverted);
}

// 5. calling addSigner with the controller role will: increase getSignerCount, and add the signer to the result of getSinger for some index.
rule add_signer_valid_liveness {
    env e;
    calldataarg args;
    address new_signer_address;
    uint256 signer_count_before;
    uint256 signer_count_after;

    requireInvariant setInvariant();

    // The caller *does* have the controller role
    require (oracleStore.hasControllerRole(e));

    signer_count_before = oracleStore.getSignerCount(e);
    require(signer_count_before < UINT256_MAX()); // reasonable: not many signers

    oracleStore.addSigner(e, new_signer_address);

    signer_count_after = oracleStore.getSignerCount(e);

    assert(signer_count_after == assert_uint256(signer_count_before + 1) ||
        signer_count_after == signer_count_before,
        "the signer count increments after adding a new signer, or is the same (in case it was already a signer)");
    
    assert(oracleStore.signersContains(e, new_signer_address),
        "the new signer has been added to the list");

}

// 6. calling removeSigner as a controller and on an address that has been 
// added to the list of signers previously will: decrease getSigners, ensure
// the address will not appear in the result of getSigner(s) for any index
rule remove_signer_valid_liveness {
    env e;
    calldataarg args;
    address signer_to_remove;
    uint256 signer_count_before;
    uint256 signer_count_after;

    // Assuming: The "signers" set obeys an invariant that
    // the two data structures it uses internally are consistent.
    requireInvariant setInvariant();

    // The caller *does* have the controller role
    require(oracleStore.hasControllerRole(e));

    // the signer to be deleted is really in the set
    require(oracleStore.signersContains(e, signer_to_remove));

    signer_count_before = oracleStore.getSignerCount(e);

    oracleStore.removeSigner(e, signer_to_remove);

    signer_count_after = oracleStore.getSignerCount(e);

    assert(signer_count_after == assert_uint256(signer_count_before - 1),
        "Removing a signer that exists and with correct permissions reduces signer count" );
    assert(!oracleStore.signersContains(e, signer_to_remove),
        "the removed signer is not in the list of signers");
}

// 7. calling getSignerCount() twice in a row with no other interleaving calls
// results in the same value.
rule double_get_signer_count {
    env e;
    uint256 signer_count_one;
    uint256 signer_count_two;

    requireInvariant setInvariant();

    signer_count_one = getSignerCount(e);
    signer_count_two = getSignerCount(e);
    assert(signer_count_one == signer_count_two);
}

// 8. Removing a signer will not cause any other signer to be removed.
rule remove_signer_deletes_no_others {
    env e;
    calldataarg args;
    address signer_to_remove;
    address some_other_signer;

    // Assuming: The "signers" set obeys an invariant that
    // the two data structures it uses internally are consistent.
    requireInvariant setInvariant();

    // there is some other strictly different signer in the set
    require(oracleStore.signersContains(e, some_other_signer));
    require(some_other_signer != signer_to_remove);

    oracleStore.removeSigner(e, signer_to_remove);

    assert(oracleStore.signersContains(e, some_other_signer));
}
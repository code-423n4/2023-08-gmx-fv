///////////////// METHODS //////////////////////

// author: z0ld
methods {

    // RoleStoreHarness
    function grantRoleHarness(address, bytes32) external;
    function revokeRoleHarness(address, bytes32) external;

    // RoleStoreHarness envfree
    function hasRoleAdmin(address) external returns (bool) envfree;
    function isRoleAdmin(bytes32) external returns (bool) envfree;
    function isRoleTimelockMultisig(bytes32) external returns (bool) envfree;
    function addressToBytes32(address) external returns (bytes32) envfree;
    function bytes32ToAddress(bytes32) external returns (address) envfree;

    // RoleStore 
    function grantRole(address, bytes32) external;
    function revokeRole(address, bytes32) external;
    function hasRole(address, bytes32) internal returns (bool);
    // envfree
    function getRoleCount() external returns (uint256) envfree;
    function getRoles(uint256, uint256) external returns (bytes32[]) envfree;
    function getRoleMemberCount(bytes32) external returns (uint256) envfree;
    function getRoleMembers(bytes32, uint256, uint256) external returns (address[]) envfree;
}

///////////////// DEFINITIONS /////////////////////

definition PURE_VIEW_FUNCTIONS(method f) returns bool = f.isView || f.isPure;

definition GRANT_REVOKE_ROLE_FUNCTIONS(method f) returns bool = 
    f.selector == sig:grantRole(address, bytes32).selector
    || f.selector == sig:revokeRole(address, bytes32).selector;

definition HARNESS_FUNCTIONS(method f) returns bool =
    f.selector == sig:grantRoleHarness(address, bytes32).selector
    || f.selector == sig:revokeRoleHarness(address, bytes32).selector;

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

// roles

ghost uint256 ghostRolesLength {
    axiom ghostRolesLength < 0xffffffffffffffffffffffffffffffff;
}

ghost uint256 ghostIncrementedRolesLength {
    axiom ghostIncrementedRolesLength < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.roles.(offset 0) uint256 newLength STORAGE {

    ghostRolesLength = newLength;

    havoc ghostIncrementedRolesLength assuming ghostRolesLength == 0 
        ? ghostIncrementedRolesLength@new == 0 
        : ghostIncrementedRolesLength@new == require_uint256(ghostIncrementedRolesLength@old + 1);
}

hook Sload uint256 length currentContract.roles.(offset 0) STORAGE {
    require ghostRolesLength == length;
}

ghost mapping(bytes32 => uint256) ghostRolesIndexes {
    init_state axiom forall bytes32 i. ghostRolesIndexes[i] == 0;
}

hook Sstore currentContract.roles._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostRolesIndexes[value] = newIndex;
}

hook Sload uint256 index currentContract.roles._inner._indexes[KEY bytes32 value] STORAGE {
    require(ghostRolesIndexes[value] == index);
}

ghost mapping(mathint => bytes32) ghostRolesValues {
    init_state axiom forall mathint i. ghostRolesValues[i] == to_bytes32(0);
}

hook Sstore currentContract.roles._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostRolesValues[index] = newValue;
}

hook Sload bytes32 value currentContract.roles._inner._values[INDEX uint256 index] STORAGE {
    require(ghostRolesValues[index] == value);
}

// roleMembers

ghost mapping(bytes32 => uint256) ghostRoleMembersLength {
    init_state axiom forall bytes32 i. ghostRoleMembersLength[i] == 0;
    axiom forall bytes32 i. ghostRoleMembersLength[i] < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.roleMembers[KEY bytes32 roleKey].(offset 0) uint256 newLength STORAGE {
    ghostRoleMembersLength[roleKey] = newLength;
}

hook Sload uint256 length currentContract.roleMembers[KEY bytes32 roleKey].(offset 0) STORAGE {
    require ghostRoleMembersLength[roleKey] == length;
}

ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostRoleMembersIndexes {
    init_state axiom forall bytes32 i. forall bytes32 j. ghostRoleMembersIndexes[i][j] == 0;
}

hook Sstore currentContract.roleMembers[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostRoleMembersIndexes[roleKey][value] = newIndex;
}

hook Sload uint256 index currentContract.roleMembers[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require(ghostRoleMembersIndexes[roleKey][value] == index);
}

ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostRoleMembersValues {
    init_state axiom forall bytes32 i. forall mathint j. ghostRoleMembersValues[i][j] == to_bytes32(0);
}

hook Sstore currentContract.roleMembers[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostRoleMembersValues[roleKey][index] = newValue;
}

hook Sload bytes32 value currentContract.roleMembers[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] STORAGE {
    require(ghostRoleMembersValues[roleKey][index] == value);
}

// roleCache

ghost mapping(address => mapping(bytes32 => bool)) ghostRoleCache {
    init_state axiom forall address i. forall bytes32 j. ghostRoleCache[i][j] == false;
}

hook Sstore currentContract.roleCache[KEY address account][KEY bytes32 roleKey] bool newValue STORAGE {
    ghostRoleCache[account][roleKey] = newValue;
}

hook Sload bool value currentContract.roleCache[KEY address account][KEY bytes32 roleKey] STORAGE {
    require(ghostRoleCache[account][roleKey] == value);
}

///////////////// SETUP INVARIANTS ////////////////

//  This is the main invariant stating that the indexes and values always match:
//        values[indexes[v] - 1] = v for all values v in the set
//    and indexes[values[i]] = i+1 for all valid indexes i.

invariant setRolesInvariant()
    (forall uint256 index. 0 <= index && index < ghostRolesLength => to_mathint(ghostRolesIndexes[ghostRolesValues[index]]) == index + 1)
    && (forall bytes32 value. ghostRolesIndexes[value] == 0 || 
         (ghostRolesValues[ghostRolesIndexes[value] - 1] == value && ghostRolesIndexes[value] >= 1 && ghostRolesIndexes[value] <= ghostRolesLength));

invariant setRoleMembersInvariant() forall bytes32 roleKey.
    (forall uint256 index. 0 <= index && index < ghostRoleMembersLength[roleKey] => to_mathint(ghostRoleMembersIndexes[roleKey][ghostRoleMembersValues[roleKey][index]]) == index + 1)
    && (forall bytes32 value. ghostRoleMembersIndexes[roleKey][value] == 0 || 
         (ghostRoleMembersValues[roleKey][ghostRoleMembersIndexes[roleKey][value] - 1] == value && ghostRoleMembersIndexes[roleKey][value] >= 1 && ghostRoleMembersIndexes[roleKey][value] <= ghostRoleMembersLength[roleKey]));

///////////////// PROPERTIES //////////////////////

// [1] roles could not be removed
invariant rolesAlwaysGrowing() ghostRolesLength == ghostIncrementedRolesLength filtered {
    f -> !PURE_VIEW_FUNCTIONS(f)
}

// [2] roleMembers should contain only existence roles
invariant roleMembersExistenceRole(bytes32 roleKey) ghostRoleMembersLength[roleKey] != 0 => ghostRolesIndexes[roleKey] != 0 {
    preserved {
        requireInvariant setRolesInvariant();
    }
}

// [3-4] only ROLE_ADMIN could grant or revoke roles
rule onlyRoleAdminGrantRevokeRoles(env e, method f, calldataarg args) filtered {
    f -> GRANT_REVOKE_ROLE_FUNCTIONS(f)
} {
    bool adminRole = hasRoleAdmin(e.msg.sender);

    f(e, args);
    
    assert(adminRole);
}

// [5-7] at least one user should left with ROLE_ADMIN or TIMELOCK_MULTISIG roles
rule atLeastOneUserLeftWithCriticalRoles(env e, address account, bytes32 roleKey) {

    require(isRoleAdmin(roleKey) || isRoleTimelockMultisig(roleKey));

    revokeRole@withrevert(e, account, roleKey);

    assert(ghostRoleMembersLength[roleKey] == 0 => lastReverted);
}

// [8-9] roleMembers grow while grand role and decrease while revoke role
rule roleMembersChange(env e, method f, calldataarg args, bytes32 roleKey) filtered {
    f -> !HARNESS_FUNCTIONS(f)
} { 

    require(hasRoleAdmin(e.msg.sender));

    uint256 before = ghostRoleMembersLength[roleKey];

    f(e, args);

    uint256 after = ghostRoleMembersLength[roleKey];

    assert(after > before => (
        f.selector == sig:grantRole(address, bytes32).selector 
            && assert_uint256(after - before) == 1
        ));

    assert(after < before => (
        f.selector == sig:revokeRole(address, bytes32).selector 
            && assert_uint256(before - after) == 1
        ));
}

// [10-14] roleCache solvency with roles and roleMembers, could be modified from grantRole() or revokeRole()
rule roleCacheSolvency(env e, method f, calldataarg args, address account, bytes32 roleKey) filtered {
    f -> !HARNESS_FUNCTIONS(f)
} { 

    bytes32 accountBytes32 = addressToBytes32(account);

    bool roleCacheBefore = ghostRoleCache[account][roleKey];

    f(e, args);

    bool roleCacheAfter = ghostRoleCache[account][roleKey];

    assert(roleCacheBefore != roleCacheAfter => (roleCacheAfter == true
        ? f.selector == sig:grantRole(address, bytes32).selector 
            && ghostRoleMembersIndexes[roleKey][accountBytes32] != 0 
            && ghostRolesIndexes[roleKey] != 0
        : f.selector == sig:revokeRole(address, bytes32).selector 
            && ghostRoleMembersIndexes[roleKey][accountBytes32] == 0
    ));
} 

// [15-19] roleMembers solvency with roles and roleCache, could be modified from grantRole() or revokeRole()
rule roleMembersSolvency(env e, method f, address account, bytes32 roleKey) filtered {
    f -> !HARNESS_FUNCTIONS(f)
} { 

    bytes32 accountBytes32 = addressToBytes32(account);

    uint256 roleMembersLengthBefore = ghostRoleMembersLength[roleKey];
    uint256 roleMembersBefore = ghostRoleMembersIndexes[roleKey][accountBytes32];
    bool roleCacheBefore = ghostRoleCache[account][roleKey];

    if(f.selector == sig:grantRole(address, bytes32).selector) {
        grantRole(e, account, roleKey);
    } else if(f.selector == sig:revokeRole(address, bytes32).selector) {
        revokeRole(e, account, roleKey);
    }

    uint256 roleMembersLengthAfter = ghostRoleMembersLength[roleKey];
    uint256 roleMembersAfter = ghostRoleMembersIndexes[roleKey][accountBytes32];
    bool roleCacheAfter = ghostRoleCache[account][roleKey];

    assert(roleMembersLengthAfter > roleMembersLengthBefore => (
        f.selector == sig:grantRole(address, bytes32).selector && ghostRolesIndexes[roleKey] != 0
        && roleMembersAfter != 0 && roleCacheAfter == true
    ));

    assert(roleMembersLengthAfter < roleMembersLengthBefore => (
        f.selector == sig:revokeRole(address, bytes32).selector
        && roleMembersAfter == 0 && roleCacheAfter == false
    ));
}

// [20] grant external integrity
rule grantExternalIntegrity(env e, address account, bytes32 roleKey) {
    
    storage storageInit = lastStorage;

    grantRole(e, account, roleKey) at storageInit;
    storage storage1 = lastStorage;

    grantRoleHarness(e, account, roleKey) at storageInit;
    storage storage2 = lastStorage;

    assert(storage1[currentContract] == storage2[currentContract]);
}

// [21] revoke external integrity
rule revokeExternalIntegrity(env e, address account, bytes32 roleKey) {
    
    storage storageInit = lastStorage;

    revokeRole(e, account, roleKey) at storageInit;
    storage storage1 = lastStorage;

    revokeRoleHarness(e, account, roleKey) at storageInit;
    storage storage2 = lastStorage;

    assert(storage1[currentContract] == storage2[currentContract]);
}

// [22-24] integrity

rule hasRoleIntegrity(env e, address account, bytes32 roleKey) {
    assert(hasRole(e, account, roleKey) == ghostRoleCache[account][roleKey]);
}

rule getRoleCountIntegrity() {
    assert(getRoleCount() == ghostRolesLength);
}

rule getRoleMemberCountIntegrity(bytes32 roleKey) {
    assert(getRoleMemberCount(roleKey) == ghostRoleMembersLength[roleKey]);
}

rule getRolesIntegrity(uint256 start, uint256 end) {

    require(end < ghostRolesLength);
    require(start < end);

    uint256 index;
    require(index < assert_uint256(end - start));

    bytes32[] barr = getRoles(start, end);
    assert(barr[index] == ghostRolesValues[start + index]);
}

rule getRoleMembersiIntegrity(bytes32 roleKey, uint256 start, uint256 end) {

    require(end < ghostRoleMembersLength[roleKey]);
    require(start < end);

    uint256 index;
    require(index < assert_uint256(end - start));

    address[] arr = getRoleMembers(roleKey, start, end);
    assert(arr[index] == bytes32ToAddress(ghostRoleMembersValues[roleKey][start + index]));
}

// [25-26] getters possibility

rule hasRolePossibility(env e, address account, bytes32 roleKey) {
    require(ghostRoleCache[account][roleKey] == true);
    satisfy(hasRole(e, account, roleKey) == ghostRoleCache[account][roleKey]);
}

rule getRoleCountPossibility(env e, address account, bytes32 roleKey) {
    require(ghostRolesLength != 0);
    satisfy(getRoleCount() == ghostRolesLength);
}

rule getRoleMemberCountPossibility(env e, address account, bytes32 roleKey) {
    require(ghostRoleMembersLength[roleKey] != 0);
    satisfy(getRoleMemberCount(roleKey) == ghostRoleMembersLength[roleKey]);
}

rule getRolesPossibility(uint256 start, uint256 end) {

    require(end < ghostRolesLength);
    require(start < end);

    uint256 index;
    require(index < assert_uint256(end - start));

    bytes32[] barr = getRoles(start, end);
    satisfy(barr[index] == ghostRolesValues[start + index]);
}

rule getRoleMembersiPossibility(bytes32 roleKey, uint256 start, uint256 end) {

    require(end < ghostRoleMembersLength[roleKey]);
    require(start < end);

    uint256 index;
    require(index < assert_uint256(end - start));

    address[] arr = getRoleMembers(roleKey, start, end);
    satisfy(arr[index] == bytes32ToAddress(ghostRoleMembersValues[roleKey][start + index]));
}

rule notRevertedPossibility(env e, method f, calldataarg args) {
    f@withrevert(e, args);
    satisfy(!lastReverted); 
}

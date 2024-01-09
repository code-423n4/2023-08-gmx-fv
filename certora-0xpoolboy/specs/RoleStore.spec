
// author: 0xpoolboy
methods {
    function hasRole(address, bytes32) external returns (bool) envfree;
    function getRoleMemberCount(bytes32) external returns (uint256) envfree;

    //Harness
    function RoleStoreHarness.hasRoleFromRoleMembers(address, bytes32) external returns (bool) envfree;
    function RoleStoreHarness.isAdmin(address) external returns (bool) envfree;
    function RoleStoreHarness.isRoleKey(bytes32) external returns (bool) envfree;

    function RoleStoreHarness.ROLE_ADMIN() external returns (bytes32) envfree;
    function RoleStoreHarness.TIMELOCK_MULTISIG() external returns (bytes32) envfree;
}

// ROLES
// EnumerableSet.Bytes32Set internal roles;
ghost mapping(mathint => bytes32) ghostRolesValues {
    init_state axiom forall mathint x. ghostRolesValues[x] == to_bytes32(0);
}
ghost mapping(bytes32 => uint256) ghostRolesIndexes {
    init_state axiom forall bytes32 x. ghostRolesIndexes[x] == 0;
}
ghost uint256 ghostRolesLength {
    init_state axiom ghostRolesLength == 0;
    // assumption: it's infeasible to grow the list to these many elements.
    axiom ghostRolesLength < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.roles.(offset 0) uint256 newLength STORAGE {
    ghostRolesLength = newLength;
}
hook Sstore currentContract.roles._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostRolesValues[index] = newValue;
}
hook Sstore currentContract.roles._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostRolesIndexes[value] = newIndex;
}

hook Sload uint256 length currentContract.roles.(offset 0) STORAGE {
    require ghostRolesLength == length;
}
hook Sload bytes32 value currentContract.roles._inner._values[INDEX uint256 index] STORAGE {
    require ghostRolesValues[index] == value;
}
hook Sload uint256 index currentContract.roles._inner._indexes[KEY bytes32 value] STORAGE {
    require ghostRolesIndexes[value] == index;
}

invariant rolesInvariant()
    (forall uint256 index. 0 <= index && index < ghostRolesLength => to_mathint(ghostRolesIndexes[ghostRolesValues[index]]) == index + 1)
    && (forall bytes32 value. ghostRolesIndexes[value] == 0 ||
         (ghostRolesValues[ghostRolesIndexes[value] - 1] == value && ghostRolesIndexes[value] >= 1 && ghostRolesIndexes[value] <= ghostRolesLength));


// ROLE MEMBERS
ghost mapping(bytes32 => mapping(mathint => bytes32)) ghostRoleMembersValues {
    init_state axiom forall bytes32 k. forall mathint x. ghostRoleMembersValues[k][x] == to_bytes32(0);
}
ghost mapping(bytes32 => mapping(bytes32 => uint256)) ghostRoleMembersIndexes {
    init_state axiom forall bytes32 k. forall bytes32 x. ghostRoleMembersIndexes[k][x] == 0;
}
ghost mapping(bytes32 => uint256) ghostRoleMembersLength {
    init_state axiom forall bytes32 k. ghostRoleMembersLength[k] == 0;
    // assumption: it's infeasible to grow the list to these many elements.
    axiom forall bytes32 k. ghostRoleMembersLength[k] < 0xffffffffffffffffffffffffffffffff;
}

hook Sstore currentContract.roleMembers[KEY bytes32 roleKey].(offset 0) uint256 newLength STORAGE {
    ghostRoleMembersLength[roleKey] = newLength;
}

hook Sstore currentContract.roleMembers[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    ghostRoleMembersValues[roleKey][index] = newValue;
}
hook Sstore currentContract.roleMembers[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    ghostRoleMembersIndexes[roleKey][value] = newIndex;
}

hook Sload uint256 length currentContract.roleMembers[KEY bytes32 roleKey].(offset 0) STORAGE {
    require ghostRoleMembersLength[roleKey] == length;
}
hook Sload bytes32 value currentContract.roleMembers[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] STORAGE {
    require ghostRoleMembersValues[roleKey][index] == value;
}
hook Sload uint256 index currentContract.roleMembers[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require ghostRoleMembersIndexes[roleKey][value] == index;
}

invariant roleMembersInvariant()
    forall bytes32 roleKey .(
        (forall uint256 index. 0 <= index && index < ghostRoleMembersLength[roleKey] => to_mathint(ghostRoleMembersIndexes[roleKey][ghostRoleMembersValues[roleKey][index]]) == index + 1)
     && (forall bytes32 value. ghostRoleMembersIndexes[roleKey][value] == 0 ||
         (ghostRoleMembersValues[roleKey][ghostRoleMembersIndexes[roleKey][value] - 1] == value && ghostRoleMembersIndexes[roleKey][value] >= 1 && ghostRoleMembersIndexes[roleKey][value] <= ghostRoleMembersLength[roleKey])));

invariant roleCacheUpToDate(address account, bytes32 roleKey)
    hasRole(account, roleKey) <=> hasRoleFromRoleMembers(account, roleKey)
    {
        preserved {
            requireInvariant roleMembersInvariant();
        }
    }

// if anyone owns a role, that role is contained in `EnumerableSet.Bytes32Set roles`
invariant validRoles(address account, bytes32 roleKey)
    hasRole(account, roleKey) => isRoleKey(roleKey);


invariant ThereMustBeAtLeastOneRoleAdmin()
    getRoleMemberCount(ROLE_ADMIN()) > 0;
// -------------------------------------------------------

rule OnceSetThereMustBeAtLeastOneTimelockMultiSig(
    env e,
    method f,
    calldataarg args
) {
    require getRoleMemberCount(TIMELOCK_MULTISIG()) > 0;
    f(e, args);
    assert getRoleMemberCount(TIMELOCK_MULTISIG()) > 0;
}

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

rule hasRoleShouldNotRevert(
    address account,
    bytes32 roleKey
) {
    bool returnValue = hasRole@withrevert(account, roleKey);
    assert !lastReverted;
}

rule GrantAndRevokeShouldNotAffectOtherAccountsOrRoles(
    env e,
    method f,
    calldataarg args,
    address account,
    bytes32 roleKey,
    address otherAccount,
    bytes32 otherRoleKey,
    bytes32 anyRoleKey
) filtered {
    f -> f.selector == sig:grantRole(address, bytes32).selector
      || f.selector == sig:revokeRole(address, bytes32).selector
} {
    require(isAdmin(e.msg.sender));

    require(otherAccount != account);
    require(otherRoleKey != roleKey);

    bool accountHasOtherRoleBefore = hasRole(account, otherRoleKey);
    bool otherAccountHasRoleBefore = hasRole(otherAccount, anyRoleKey);

    if (f.selector == sig:grantRole(address, bytes32).selector) {
        grantRole(e, account, roleKey);
    } else if (f.selector == sig:revokeRole(address, bytes32).selector) {
        revokeRole(e, account, roleKey);
    }

    bool accountHasOtherRoleAfter = hasRole(account, otherRoleKey);
    bool otherAccountHasRoleAfter = hasRole(otherAccount, anyRoleKey);

    assert accountHasOtherRoleAfter == accountHasOtherRoleBefore,
        "grant or revoke should not affect other roles of account";
    assert otherAccountHasRoleAfter == otherAccountHasRoleBefore,
        "grant or revoke should not affect any roles of other accounts";
}

rule onlyAdminCanGrantOrRevokeRole(
    env e,
    method f,
    address account,
    bytes32 roleKey
) filtered {
    f -> f.selector == sig:grantRole(address, bytes32).selector
      || f.selector == sig:revokeRole(address, bytes32).selector
} {
    bool grantRoleIsCalled  = (f.selector == sig:grantRole(address, bytes32).selector);
    bool revokeRoleIsCalled = (f.selector == sig:revokeRole(address, bytes32).selector);

    bool isAdmin = isAdmin(e.msg.sender);
    bool hasRoleBefore = hasRole(account, roleKey);

    if (grantRoleIsCalled) {
        grantRole(e, account, roleKey);
    } else if (revokeRoleIsCalled) {
        revokeRole(e, account, roleKey);
    }

    bool grantOrRevokeReverted = lastReverted;

    bool hasRoleAfter = hasRole(account, roleKey);

    assert !isAdmin <=> grantOrRevokeReverted,
        "grant or revoke should only revert iif caller does not hold admin role";
    assert (grantOrRevokeReverted && grantRoleIsCalled)  =>  hasRoleAfter,
        "grant should set role";
    assert (grantOrRevokeReverted && revokeRoleIsCalled) => !hasRoleAfter,
        "revoke should revoke role";
}

rule noOtherFunctionThanGrantOrRevokeCanAffectRoles(
    env e,
    method otherFunction,
    calldataarg data,
    address anyAccount,
    bytes32 anyRoleKey
) filtered {
    otherFunction -> otherFunction.selector != sig:grantRole(address, bytes32).selector
                  && otherFunction.selector != sig:revokeRole(address, bytes32).selector
} {
    bool hasRoleBefore = hasRole(anyAccount, anyRoleKey);

    otherFunction(e, data);

    bool hasRoleAfter = hasRole(anyAccount, anyRoleKey);

    assert hasRoleAfter == hasRoleBefore,
        "other functions than grant or revoke should not affect any roles of any account";
}
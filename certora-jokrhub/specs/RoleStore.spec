definition UINT256_MAX() returns uint256 = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

rule grantRoleUnitTest (env e, address account, bytes32 roleKey) {

    uint256 rolesCountBefore = getRoleCount(e);
    uint256 roleMemebersCountBefore = roleMembersCount(e, roleKey);

    require(rolesCountBefore < UINT256_MAX());
    require(roleMemebersCountBefore < UINT256_MAX());

    grantRole(e, account, roleKey);

    uint256 roleCountAfter = getRoleCount(e);
    uint256 roleMemebersCountAfter = roleMembersCount(e, roleKey);

    bool roleExists = rolesContains(e, roleKey);
    bool roleMemberExists = roleMembersContains(e, roleKey, account);
    bool hasCacheRole = hasRole(e, account, roleKey);

    assert(roleExists);
    assert(roleMemberExists);
    assert(roleCountAfter == assert_uint256(rolesCountBefore + 1) || roleCountAfter == rolesCountBefore);
    assert(roleMemebersCountAfter == assert_uint256(roleMemebersCountBefore + 1) || roleMemebersCountAfter == roleMemebersCountBefore);
    assert(hasCacheRole);
    assert(isAdminHarness(e));

}

rule revoleRoleUnitTest (env e, address account, bytes32 roleKey) {

    require(roleMembersContains(e, roleKey, account));

    uint256 roleMemebersCountBefore = roleMembersCount(e, roleKey);

    revokeRole(e, account, roleKey);

    uint256 roleMemebersCountAfter = roleMembersCount(e, roleKey);

    bool roleMemberExists = roleMembersContains(e, roleKey, account);
    bool hasCacheRole = hasRole(e, account, roleKey);

    assert(!roleMemberExists);
    assert(roleMemebersCountAfter == assert_uint256(roleMemebersCountBefore - 1) || roleMemebersCountAfter == roleMemebersCountBefore);
    assert(!hasCacheRole);
    assert(roleKey != admin(e) => isAdminHarness(e));

}

rule revokeRoleShouldRevert (env e, address account, bytes32 roleKey) {
    require(roleMembersContains(e, roleKey, account));
    uint256 roleMemebersCountBefore = roleMembersCount(e, roleKey);
    require roleMemebersCountBefore >= 1;

    revokeRole@withrevert(e, account, roleKey);
    bool revokeRoleReverted = lastReverted;

    uint256 roleMemebersCountAfter = roleMembersCount(e, roleKey);

    assert(
        (roleMemebersCountAfter == 0 && ( roleKey == getRoleAdmin(e) || roleKey == getTimelockMultisig(e) )) ||
        (roleKey != admin(e) && !isAdminHarness(e))
        => revokeRoleReverted
    );
    
}
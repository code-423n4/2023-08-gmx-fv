//import "./hasRoleInvariant.spec";


// METHOD specification
// author: neumoxx
methods {
    function grantRole(address, bytes32) external;
    function revokeRole(address, bytes32) external;
    function hasRole(address, bytes32) external returns (bool);
    function containsRole(address, bytes32) external returns (bool);
    function containsRoleInCache(address, bytes32) external returns (bool);
    function getRoleCount() external returns (uint256) envfree;
    function getRoles(uint256, uint256) external returns (bytes32[]) envfree;
    function getRoleMemberCount(bytes32) external returns (uint256) envfree;
    function getRoleMembers(bytes32, uint256, uint256) external returns (address[]) envfree;
    function _grantRole(address, bytes32) internal;
    function _revokeRole(address, bytes32) internal;
    function bytes32ToUint(bytes32) external returns (uint256) envfree;
    function addressToBytes32(address) external returns (bytes32) envfree;
}


// DEFINITION

// Returns, whether a value is in the roles set.
definition inRolesSet(bytes32 value) returns bool = (rolesGhostIndexes[value] != 0);

// Returns, whether a value is in the roleMembers set.
definition inRoleMembersSet(bytes32 roleKey, bytes32 value) returns bool = (roleMembersGhostIndexes[roleKey][value] != 0);

// @notice: Functions defined in harness contract
definition notHarnessCall(method f) returns bool =
    (f.selector != sig:containsRole(address,bytes32).selector
    && f.selector != sig:containsRoleInCache(address,bytes32).selector
    && f.selector != sig:getMembersLength(bytes32).selector
    && f.selector != sig:getRoleMemberByIndex(bytes32, uint256).selector
    && f.selector != sig:bytes32ToUint(bytes32).selector
    && f.selector != sig:addressToBytes32(address).selector);


// RULES

// @notice: Consistency check for the execution of function grantRole
rule grantRoleConsistencyCheck(env e) {

  address account;
  bytes32 roleKey;

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  bool isAdmin = hasRole(e, e.msg.sender, ROLE_ADMIN(e));

  grantRole@withrevert(e, account, roleKey);
  bool lastRev = lastReverted;

  assert lastRev <=> e.msg.value > 0 || !isAdmin, "grantRole not payable and only callable by admin";
  assert !lastRev => (
    containsRole(e, account, roleKey) == true &&
    containsRoleInCache(e, account, roleKey) == true
  );
}


// @notice: Consistency check for the execution of function revokeRole
rule revokeRoleConsistencyCheck(env e, env e1) {

  address account;
  bytes32 roleKey;

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  bool isAdmin = hasRole(e, e.msg.sender, ROLE_ADMIN(e));

  bool accountIsAdmin = hasRole(e, account, ROLE_ADMIN(e));
  bool accountIsTimelockMultisig = hasRole(e, account, TIMELOCK_MULTISIG(e));

  uint256 roleMembersCount = getRoleMemberCount(roleKey);

  revokeRole@withrevert(e, account, roleKey);
  bool lastRev = lastReverted;

  assert (
    e.msg.value > 0 ||
    !isAdmin ||
    (roleMembersCount == 1 && roleKey == ROLE_ADMIN(e) && accountIsAdmin) ||
    (roleMembersCount == 1 && roleKey == TIMELOCK_MULTISIG(e) && accountIsTimelockMultisig)
  ) => lastRev, "revokeRole should have reverted";
  assert !lastRev => (
    !containsRole(e, account, roleKey) &&
    !containsRoleInCache(e, account, roleKey) &&
    !hasRole(e, account, roleKey)
  );
}


// @notice: Function revokeRole satisfies a ROLE_ADMIN can be revoked
rule revokeRoleSatisfies1(env e, env e1) {

  address account;
  bytes32 roleKey;

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  bool isAdmin = hasRole(e, e.msg.sender, ROLE_ADMIN(e));

  bool accountIsAdmin = hasRole(e, account, ROLE_ADMIN(e));
  bool accountIsTimelockMultisig = hasRole(e, account, TIMELOCK_MULTISIG(e));

  uint256 roleMembersCount = getRoleMemberCount(roleKey);

  revokeRole(e, account, roleKey);

  satisfy roleKey == ROLE_ADMIN(e);
}


// @notice: Function revokeRole satisfies a TIMELOCK_MULTISIG can be revoked
rule revokeRoleSatisfies2(env e, env e1) {

  address account;
  bytes32 roleKey;

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  bool isAdmin = hasRole(e, e.msg.sender, ROLE_ADMIN(e));

  bool accountIsAdmin = hasRole(e, account, ROLE_ADMIN(e));
  bool accountIsTimelockMultisig = hasRole(e, account, TIMELOCK_MULTISIG(e));

  uint256 roleMembersCount = getRoleMemberCount(roleKey);

  revokeRole(e, account, roleKey);

  satisfy roleKey == TIMELOCK_MULTISIG(e);
}

// @notice: Consistency check for the execution of function hasRole
rule hasRoleConsistencyCheck(env e, env e1) {

  address account;
  bytes32 roleKey;

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  require hasRole(e, account, roleKey) <=> hasRole(e1, account, roleKey);

  bool hasIt = hasRole@withrevert(e, account, roleKey);

  assert lastReverted <=> e.msg.value > 0;
  assert !lastReverted => (
    //containsRole(e, account, roleKey) == hasIt &&
    containsRoleInCache(e, account, roleKey) == hasIt
  );

}

// @notice: Consistency check for the execution of function getRoleCount
rule getRoleCountConsistencyCheck(env e) {

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  uint256 length = getRoleCount@withrevert();

  assert !lastReverted;
  assert rolesGhostLength == length;

}

// @notice: Consistency check for the execution of function getRoles
rule getRolesConsistencyCheck(env e) {

  uint256 start;
  uint256 end;

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  require end - start == 2;
  require end < getRoleCount();

  bytes32[] roles = getRoles@withrevert(start, end);

  assert start > end <=> lastReverted;
  assert !lastReverted <=> (
    roles[0] == rolesGhostValues[start] &&
    roles[1] == rolesGhostValues[start + 1]
  );

}

// @notice: Consistency check for the execution of function getRoleMemberCount
rule getRoleMemberCountConsistencyCheck(env e) {

  bytes32 roleKey;

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  uint256 length = getRoleMemberCount@withrevert(roleKey);

  assert !lastReverted;
  assert getMembersLength(e, roleKey) == length;

}

// @notice: Consistency check for the execution of function getRoleMembers
rule getRoleMembersConsistencyCheck(env e) {

  bytes32 roleKey;
  uint256 start;
  uint256 end;

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  require end - start == 2;
  require end < getRoleMemberCount(roleKey);

  address[] members = getRoleMembers@withrevert(roleKey, start, end);

  assert lastReverted <=> end < start;
  assert !lastReverted => (
        members[0] == getRoleMemberByIndex(e, roleKey, start) &&
        members[1] == getRoleMemberByIndex(e, roleKey, assert_uint256(start + 1))
  );

}


// @notice: Number of roles cannot decrease, as there is no way in the contract to remove a role
rule roleCountMonotonicallyIncreases(method f) filtered {
    f -> notHarnessCall(f)
} {

  requireInvariant rolesEnumerableSetInvariant();
  requireInvariant roleMembersEnumerableSetInvariant();

  env e;

  uint256 lengthPre = getRoleCount@withrevert();

  calldataarg args;
  f(e, args);

  uint256 lengthPost = getRoleCount@withrevert();

  assert lengthPost >= lengthPre;
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

// roleCache
ghost mapping(bytes32 => mapping (bytes32 => bool)) roleCacheGhost {
    init_state axiom forall bytes32 x. forall bytes32 y. roleCacheGhost[x][y] == false;
    axiom forall bytes32 x. forall bytes32 y. roleCacheGhost[x][y] == true => roleMembersGhostIndexes[y][x] > 0;
    axiom forall bytes32 x. forall bytes32 y. roleCacheGhost[x][y] == true => (x & to_bytes32(2^160 - 1  )) == x;
}

// roles

// ghost field for the values array
ghost mapping(mathint => bytes32) rolesGhostValues {
    init_state axiom forall mathint x. rolesGhostValues[x] == to_bytes32(0);
}
// ghost field for the indexes map
ghost mapping(bytes32 => uint256) rolesGhostIndexes {
    init_state axiom forall bytes32 x. rolesGhostIndexes[x] == 0;
}
// ghost field for the length of the values array (stored in offset 0)
ghost uint256 rolesGhostLength {
    // assumption: it's infeasible to grow the list to these many elements.
    axiom rolesGhostLength < 0xffffffffffffffffffffffffffffffff;
}

// roleMembers
ghost mapping(bytes32 => mapping(mathint => bytes32)) roleMembersGhostValues {
    init_state axiom forall bytes32 x. forall mathint y. roleMembersGhostValues[x][y] == to_bytes32(0);
    axiom forall bytes32 x. forall mathint y. (roleMembersGhostValues[x][y] & to_bytes32(2^160 - 1  )) == roleMembersGhostValues[x][y];
    axiom forall bytes32 x. forall mathint y. roleMembersGhostValues[x][y] != to_bytes32(0) => rolesGhostIndexes[x] > 0;
}
// ghost field for the indexes map
ghost mapping(bytes32 => mapping(bytes32 => uint256)) roleMembersGhostIndexes {
    init_state axiom forall bytes32 x. forall bytes32 y. roleMembersGhostIndexes[x][y] == 0;
    axiom forall bytes32 x. forall bytes32 y. roleMembersGhostIndexes[x][y] > 0 => roleMembersGhostValues[x][roleMembersGhostIndexes[x][y]] == y;
}
// ghost field for the length of the values array (stored in offset 0)
ghost mapping(bytes32 => uint256) roleMembersGhostLength {
    // assumption: it's infeasible to grow the list to these many elements.
    init_state axiom forall bytes32 role. roleMembersGhostLength[role] == 0;
    axiom forall bytes32 x. roleMembersGhostLength[x] < 0xffffffffffffffffffffffffffffffff;
}


// HOOKS
// Store hook to synchronize rolesGhostLength with the length of the roles._inner._values array.
// We need to use (offset 0) here, as there is no keyword yet to access the length.

// roleCache
hook Sstore currentContract.roleCache[KEY address account][KEY bytes32 roleKey] bool newValue STORAGE {
    roleCacheGhost[to_bytes32(require_uint256(account))][roleKey] = newValue;
}

// roles
hook Sstore currentContract.roles.(offset 0) uint256 newLength STORAGE {
    rolesGhostLength = newLength;
}
// Store hook to synchronize rolesGhostValues array with roles._inner._values.
hook Sstore currentContract.roles._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    rolesGhostValues[index] = newValue;
}
// Store hook to synchronize rolesGhostIndexes array with roles._inner._indexes.
hook Sstore currentContract.roles._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    rolesGhostIndexes[value] = newIndex;
}


// roleMembers
hook Sstore currentContract.roleMembers[KEY bytes32 roleKey].(offset 0) uint256 newLength STORAGE {
    roleMembersGhostLength[roleKey] = newLength;
}
// Store hook to synchronize roleMembersGhostValues array with roleMembers[roleKey]._inner._values.
hook Sstore currentContract.roleMembers[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] bytes32 newValue STORAGE {
    roleMembersGhostValues[roleKey][index] = newValue;
}
// Store hook to synchronize roleMembersGhostIndexes array with roleMembers[roleKey]._inner._indexes.
hook Sstore currentContract.roleMembers[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] uint256 newIndex STORAGE {
    roleMembersGhostIndexes[roleKey][value] = newIndex;
}

// The load hooks can use require to ensure that the ghost field has the same information as the storage.
// The require is sound, since the store hooks ensure the contents are always the same.  However we cannot
// prove that with invariants, since this would require the invariant to read the storage for all elements
// and neither storage access nor function calls are allowed in quantifiers.
//
// By following this simple pattern it is ensured that the ghost state and the storage are always the same
// and that the solver can use this knowledge in the proofs.

// Load hook to synchronize rolesGhostLength with the length of the roles._inner._values array.
// Again we use (offset 0) here, as there is no keyword yet to access the length.

// roleCache
hook Sload bool value currentContract.roleCache[KEY address account][KEY bytes32 roleKey] STORAGE {
    require roleCacheGhost[to_bytes32(require_uint256(account))][roleKey] == value;
}

// roles
hook Sload uint256 length currentContract.roles.(offset 0) STORAGE {
    require rolesGhostLength == length;
}
hook Sload bytes32 value currentContract.roles._inner._values[INDEX uint256 index] STORAGE {
    require rolesGhostValues[index] == value;
}
hook Sload uint256 index currentContract.roles._inner._indexes[KEY bytes32 value] STORAGE {
    require rolesGhostIndexes[value] == index;
}


// roleMembers
hook Sload uint256 length currentContract.roleMembers[KEY bytes32 roleKey].(offset 0) STORAGE {
    require roleMembersGhostLength[roleKey] == length;
}
hook Sload bytes32 value currentContract.roleMembers[KEY bytes32 roleKey]._inner._values[INDEX uint256 index] STORAGE {
    require roleMembersGhostValues[roleKey][index] == value;
}
hook Sload uint256 index currentContract.roleMembers[KEY bytes32 roleKey]._inner._indexes[KEY bytes32 value] STORAGE {
    require roleMembersGhostIndexes[roleKey][value] == index;
}

// INVARIANTS

//  This is the main invariant stating that the indexes and values always match:
//        values[indexes[v] - 1] = v for all values v in the set
//    and indexes[values[i]] = i+1 for all valid indexes i.

invariant rolesEnumerableSetInvariant()
    (forall uint256 index. 0 <= index && index < rolesGhostLength => to_mathint(rolesGhostIndexes[rolesGhostValues[index]]) == index + 1)
    && (forall bytes32 value. rolesGhostIndexes[value] == 0 ||
         (rolesGhostValues[rolesGhostIndexes[value] - 1] == value && rolesGhostIndexes[value] >= 1 && rolesGhostIndexes[value] <= rolesGhostLength));


invariant roleMembersEnumerableSetInvariant()
    (forall bytes32 roleKey.
      (forall uint256 index.
        (0 <= index && index < roleMembersGhostLength[roleKey] => to_mathint(roleMembersGhostIndexes[roleKey][roleMembersGhostValues[roleKey][index]]) == index + 1)
      )
      &&
      (forall bytes32 value.
        roleMembersGhostIndexes[roleKey][value] == 0 ||
        (roleMembersGhostValues[roleKey][roleMembersGhostIndexes[roleKey][value] - 1] == value && roleMembersGhostIndexes[roleKey][value] >= 1 && roleMembersGhostIndexes[roleKey][value] <= roleMembersGhostLength[roleKey])
      )
    );

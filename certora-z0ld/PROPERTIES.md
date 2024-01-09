# Oracle
## High-Level
- [] only CONTROLLER could modify state
- [] tokensWithPrices and primaryPrices should exist simultaneously
## Valid States
- [] block numbers must be in ascending order
## State Transitions
## Variable Transitions
## Unit Tests
- integrity
- possibility
# OracleStore
## High-Level
- [1] only CONTROLLER could modify state
    - `onlyControllerCouldModifyState`
## Valid States
## State Transitions
- [] signer grow when adding and decrease when removing
    - `addRemoveChangeSignersInValidDirection`
## Variable Transitions
- [] signer length always change to 1
    - `signersChangeConditions`
## Unit Tests
- integrity
- possibility
# DataStore
## High-Level
- [2-3] only CONTROLLER could modify state
    - `onlyControllerCouldModifyState`
## Valid States
## State Transitions
## Variable Transitions
## Unit Tests
- integrity
- possibility
# RoleStore
## High-Level
- [3-4] only ROLE_ADMIN could grant or revoke roles
    - `onlyRoleAdminGrantRevokeRoles`
- [5-7] at least one user should left with ROLE_ADMIN or TIMELOCK_MULTISIG roles 
    - `atLeastOneUserLeftWithCriticalRoles`
## Valid States
- [2] roleMembers should contain only existence roles
    - `roleMembersExistenceRole`
## State Transitions
- [8-9] roleMembers grow while grand role and decrease while revoke role
    - `roleMembersLengthChange`
- [10-14] roleCache solvency with roles and roleMembers, could be modified from grantRole() or revokeRole()
    - `roleCacheSolvency`
- [15-19] roleMembers solvency with roles and roleCache, could be modified from grantRole() or revokeRole()
    - `roleMembersSolvency`
## Variable Transitions
- [1] roles could not be removed
    - `rolesAlwaysGrowing`
## Unit Tests
- [20] grant external integrity
    - `grantExternalIntegrity`
- [21] revoke external integrity
    - `revokeExternalIntegrity`
- [22-24] integrity
    - `hasRoleIntegrity`
    - `getRoleCountIntegrity`
    - `getRoleMemberCountIntegrity`
    - `getRolesIntegrity`
    - `getRoleMembersiIntegrity`
- [25-26] possibility
    - `hasRolePossibility`
    - `getRoleCountPossibility`
    - `getRoleMemberCountPossibility`
    - `getRolesPossibility`
    - `getRoleMembersiPossibility`
# StrictBank
## High-Level
- [5-9] onlyController can execute non-view functions, otherwise got reverted
    - `onlyControllerCouldChangeState`
- [4] interaction with a token should not change balance of another token
    - `balanceIndependence`
- [15-18] transfer out should correctly update all balances
## Valid States
- [1-3] tokenBalances storage variable should be equal to balance of current contract  
    - `tokenBalancesSolvency`
## State Transitions
- [11-12] receive native tokens only via payable fallback and from `wnt` contract
    - `receiveNativeTokensFromWnt`
## Variable Transitions
- [10] recordTransferIn() should update token balance in a big way
    - `recordTransferInTokenBalanceGreater`
## Unit Tests
- [13-14] transfer out to the current contract is forbidden
    - `transferOutToCurrentContractForbidden`
- [19] syncTokenBalance() integrity
    - `syncTokenBalanceIntegrity`
- [20] recordTransferIn() integrity
    - `recordTransferInIntegrity`
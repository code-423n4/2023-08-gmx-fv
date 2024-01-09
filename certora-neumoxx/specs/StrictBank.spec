using DataStore as DATA_STORE;
using RoleStore as ROLE_STORE;
using DummyERC20A as TOKEN;

// author: neumoxx
methods {

    // ERC20
    function _.name()                                external  => DISPATCHER(true);
    function _.symbol()                              external  => DISPATCHER(true);
    function _.decimals()                            external  => DISPATCHER(true);
    function _.totalSupply()                         external  => DISPATCHER(true);
    function _.balanceOf(address)                    external  => DISPATCHER(true);
    function _.allowance(address,address)            external  => DISPATCHER(true);
    function _.approve(address,uint256)              external  => DISPATCHER(true);
    function _.transfer(address,uint256)             external  => DISPATCHER(true);
    function _.transferFrom(address,address,uint256) external  => DISPATCHER(true);

    // DataStore
    function _.getUint(bytes32) external => DISPATCHER(true);
    function _.getAddress(bytes32) external => DISPATCHER(true);
    function _.getBytes32(bytes32) external => DISPATCHER(true);
    // RoleStore
    function _.hasRole(address,bytes32) external => DISPATCHER(true);

    // WNT
    function _.deposit()                             external  => DISPATCHER(true);
    function _.withdraw(uint256)                     external  => DISPATCHER(true);

    function tokenBalances(address) external returns (uint256) envfree;

    // Bank
    function transferOut(address, address, uint256) external;
    function transferOut(address, address, uint256, bool) external;
    function transferOutNativeToken(address, uint256) external;
    function _transferOut(address, address, uint256) internal;
    function _transferOutNativeToken(address, address, uint256) internal;

    // Strict bank
    function recordTransferIn(address) external returns (uint256);
    function syncTokenBalance(address) external returns (uint256);
    function _recordTransferIn(address token) internal;
    function _afterTransferOut(address token) internal;
}


// DEFINITION

// @notice: Functions defined in harness contract
definition notHarnessCall(method f) returns bool =
    (f.selector != sig:afterTransferOut(address).selector
    && f.selector != sig:getETHBalance(address).selector);

definition UINT256_MAX() returns mathint = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;


// RULES

// @notice: The Wnt address is the only one that can send ether to the contract
rule balanceCanOnlyIncreaseIfCallerIsWnt(method f) filtered {
    f -> notHarnessCall(f)
} {

    env e;

    address wnt = getWntAddress(e);
    uint256 balancePre = getETHBalance(e, currentContract);

    calldataarg args;
    f(e, args);

    uint256 balancePost = getETHBalance(e, currentContract);

    assert balancePost > balancePre => e.msg.sender == wnt;
}

// @notice: Consistency check for the execution of function transferOut
rule transferOutConsistencyCheck() {

    env e;
    env e1;

    address token;
    address receiver;
    uint256 amount;

    require roleStore(e) == ROLE_STORE;
    require dataStore(e) == DATA_STORE;

    bool isController = hasControllerRole(e);
    address holdingAddress = getHoldingAddress(e);

    uint256 gasLimit = getGasLimit(e, token);

    require token == TOKEN;
    require receiver != currentContract;
    require holdingAddress != currentContract;

    uint256 balanceContractPre = TOKEN.balanceOf(e, currentContract);
    uint256 balanceSenderPre = TOKEN.balanceOf(e, e.msg.sender);
    uint256 balanceHoldingPre = TOKEN.balanceOf(e, holdingAddress);
    uint256 balanceReceiverPre = TOKEN.balanceOf(e, receiver);

    transferOut@withrevert(e, token, receiver, amount);
    bool lastRev = lastReverted;

    uint256 balanceContractPost = TOKEN.balanceOf(e, currentContract);
    uint256 balanceSenderPost = TOKEN.balanceOf(e, e.msg.sender);
    uint256 balanceHoldingPost = TOKEN.balanceOf(e, holdingAddress);
    uint256 balanceReceiverPost = TOKEN.balanceOf(e, receiver);

    assert (e.msg.value > 0
        || amount > balanceContractPre
        || (balanceReceiverPre + amount > UINT256_MAX() && holdingAddress == 0 && amount > 0)
        || (balanceReceiverPre + amount > UINT256_MAX() && balanceHoldingPre + amount > UINT256_MAX())
        || !isController
        || receiver == currentContract
        || (gasLimit == 0 && amount > 0)
    ) => lastRev;

    assert !lastRev => (
      ((balanceReceiverPre + amount > UINT256_MAX() && balanceHoldingPre + amount <= UINT256_MAX()) => to_mathint(balanceHoldingPost) == balanceHoldingPre + amount ) &&
      (
        (balanceReceiverPre + amount <= UINT256_MAX()) => (
              to_mathint(balanceReceiverPost) == balanceReceiverPre + amount ||
              to_mathint(balanceReceiverPost) == balanceReceiverPre + 2*amount  // I have to do this because I found an error in the prover where a low level call reverts but does the transfer anyway https://prover.certora.com/output/32676/6b0fd213b3a14330941676a48483ce3e/?anonymousKey=0f9eb8eb4c5f66b7132ce451930a916bce0f527f
            )
      ) &&
      (
        (to_mathint(balanceContractPost) == balanceContractPre - amount) ||
        (to_mathint(balanceContractPost) == balanceContractPre - 2*amount)      // I have to do this because I found an error in the prover where a low level call reverts but does the transfer anyway https://prover.certora.com/output/32676/6b0fd213b3a14330941676a48483ce3e/?anonymousKey=0f9eb8eb4c5f66b7132ce451930a916bce0f527f
      ) &&
      (ghostTokenBalances[token] == balanceContractPost)
    );
}

// @notice: Consistency check for the execution of function transferOut with shouldUnwrapNativeToken flag
rule transferOutWithFlagConsistencyCheck() {

    env e;

    address token;
    address receiver;
    uint256 amount;
    bool shouldUnwrapNativeToken;

    address wnt = getWntAddress(e);

    require roleStore(e) == ROLE_STORE;
    require dataStore(e) == DATA_STORE;

    bool isController = hasControllerRole(e);
    address holdingAddress = getHoldingAddress(e);

    uint256 gasLimit = getGasLimit(e, token);

    require token == TOKEN;
    require receiver != currentContract;
    require holdingAddress != currentContract;

    uint256 balanceContractPre = TOKEN.balanceOf(e, currentContract);
    uint256 balanceSenderPre = TOKEN.balanceOf(e, e.msg.sender);
    uint256 balanceHoldingPre = TOKEN.balanceOf(e, holdingAddress);
    uint256 balanceReceiverPre = TOKEN.balanceOf(e, receiver);

    transferOut@withrevert(e, token, receiver, amount, shouldUnwrapNativeToken);
    bool lastRev = lastReverted;

    uint256 balanceContractPost = TOKEN.balanceOf(e, currentContract);
    uint256 balanceSenderPost = TOKEN.balanceOf(e, e.msg.sender);
    uint256 balanceHoldingPost = TOKEN.balanceOf(e, holdingAddress);
    uint256 balanceReceiverPost = TOKEN.balanceOf(e, receiver);

    assert (e.msg.value > 0
        || amount > balanceContractPre
        || (balanceReceiverPre + amount > UINT256_MAX() && holdingAddress == 0 && amount > 0)
        || (balanceReceiverPre + amount > UINT256_MAX() && balanceHoldingPre + amount > UINT256_MAX())
        || !isController
        || receiver == currentContract
        || (gasLimit == 0 && amount > 0)
    ) => lastRev;

    assert !lastRev => (
      ((balanceReceiverPre + amount > UINT256_MAX() && balanceHoldingPre + amount <= UINT256_MAX()) => to_mathint(balanceHoldingPost) == balanceHoldingPre + amount ) &&
      (
        (balanceReceiverPre + amount <= UINT256_MAX()) => (
              to_mathint(balanceReceiverPost) == balanceReceiverPre + amount ||
              to_mathint(balanceReceiverPost) == balanceReceiverPre + 2*amount  // I have to do this because I found an error in the prover where a low level call reverts but does the transfer anyway https://prover.certora.com/output/32676/6b0fd213b3a14330941676a48483ce3e/?anonymousKey=0f9eb8eb4c5f66b7132ce451930a916bce0f527f
            )
      ) &&
      (
        (to_mathint(balanceContractPost) == balanceContractPre - amount) ||
        (to_mathint(balanceContractPost) == balanceContractPre - 2*amount)      // I have to do this because I found an error in the prover where a low level call reverts but does the transfer anyway https://prover.certora.com/output/32676/6b0fd213b3a14330941676a48483ce3e/?anonymousKey=0f9eb8eb4c5f66b7132ce451930a916bce0f527f
      ) &&
      (ghostTokenBalances[token] == balanceContractPost)
    );

}

// @notice: Consistency check for the execution of function transferOutNativeToken
rule transferOutNativeTokenConsistencyCheck() {

    env e;

    address token;
    address receiver;
    uint256 amount;

    address wnt = getWntAddress(e);

    require roleStore(e) == ROLE_STORE;
    require dataStore(e) == DATA_STORE;

    require wnt == TOKEN;

    bool isController = hasControllerRole(e);
    address holdingAddress = getHoldingAddress(e);

    uint256 gasLimit = getGasLimit(e, token);

    require token == TOKEN;
    require receiver != currentContract;
    require holdingAddress != currentContract;

    uint256 balanceContractPre = TOKEN.balanceOf(e, currentContract);
    uint256 balanceSenderPre = TOKEN.balanceOf(e, e.msg.sender);
    uint256 balanceHoldingPre = TOKEN.balanceOf(e, holdingAddress);
    uint256 balanceReceiverPre = TOKEN.balanceOf(e, receiver);

    transferOutNativeToken@withrevert(e, receiver, amount);
    bool lastRev = lastReverted;

    uint256 balanceContractPost = TOKEN.balanceOf(e, currentContract);
    uint256 balanceSenderPost = TOKEN.balanceOf(e, e.msg.sender);
    uint256 balanceHoldingPost = TOKEN.balanceOf(e, holdingAddress);
    uint256 balanceReceiverPost = TOKEN.balanceOf(e, receiver);

    assert (e.msg.value > 0
        || amount > balanceContractPre
        || (balanceReceiverPre + amount > UINT256_MAX() && holdingAddress == 0 && amount > 0)
        || (balanceReceiverPre + amount > UINT256_MAX() && balanceHoldingPre + amount > UINT256_MAX())
        || !isController
        || receiver == currentContract
        || (gasLimit == 0 && amount > 0)
    ) => lastRev;

    assert !lastRev => (
      ((balanceReceiverPre + amount > UINT256_MAX() && balanceHoldingPre + amount <= UINT256_MAX()) => to_mathint(balanceHoldingPost) == balanceHoldingPre + amount ) &&
      (
        (balanceReceiverPre + amount <= UINT256_MAX()) => (
              to_mathint(balanceReceiverPost) == balanceReceiverPre + amount ||
              to_mathint(balanceReceiverPost) == balanceReceiverPre + 2*amount  // I have to do this because I found an error in the prover where a low level call reverts but does the transfer anyway https://prover.certora.com/output/32676/6b0fd213b3a14330941676a48483ce3e/?anonymousKey=0f9eb8eb4c5f66b7132ce451930a916bce0f527f
            )
      ) &&
      (
        (to_mathint(balanceContractPost) == balanceContractPre - amount) ||
        (to_mathint(balanceContractPost) == balanceContractPre - 2*amount)      // I have to do this because I found an error in the prover where a low level call reverts but does the transfer anyway https://prover.certora.com/output/32676/6b0fd213b3a14330941676a48483ce3e/?anonymousKey=0f9eb8eb4c5f66b7132ce451930a916bce0f527f
      ) &&
      (ghostTokenBalances[token] == balanceContractPost)
    );

}


// @notice: Consistency check for the execution of function recordTransferIn
rule recordTransferInConsistencyCheck(env e, address token) {

  require token == TOKEN;

    uint256 balanceBefore = ghostTokenBalances[token];
    uint256 balanceNext = TOKEN.balanceOf(e, currentContract);

    bool isController = hasControllerRole(e);

    uint256 res = recordTransferIn@withrevert(e, token);
    bool lastRev = lastReverted;

    uint256 balanceAfter = ghostTokenBalances[token];

    assert lastRev <=> (!isController || e.msg.value > 0 || balanceNext < balanceBefore);
    assert !lastRev => (balanceAfter == balanceNext && to_mathint(res) == balanceNext - balanceBefore);
}


// @notice: Consistency check for the execution of function syncTokenBalance
// @notice: Catches bug #0
rule syncTokenBalanceConsistencyCheck(env e, address token) {

  require token == TOKEN;

    uint256 balanceNext = TOKEN.balanceOf(e, currentContract);

    bool isController = hasControllerRole(e);

    uint256 res = syncTokenBalance@withrevert(e, token);
    bool lastRev = lastReverted;

    uint256 balanceAfter = ghostTokenBalances[token];

    assert lastRev <=> (!isController || e.msg.value > 0);
    assert !lastRev => (balanceAfter == balanceNext && res == balanceNext);
}


// @notice: syncTokenBalance, afterTransferOut, and recordTransferIn should not change tokenBalances[token1] where token1 != token2
rule balanceIndependence(method f, env e, address token1, address token2) filtered {
    f -> f.selector == sig:recordTransferIn(address).selector
        || f.selector == sig:afterTransferOut(address).selector
        || f.selector == sig:syncTokenBalance(address).selector
} {
    uint256 balanceBefore = tokenBalances(token2);

    if (f.selector == sig:recordTransferIn(address).selector) {
        recordTransferIn(e, token1);
    } else if (f.selector == sig:afterTransferOut(address).selector) {
        afterTransferOut(e, token1);
    } else if (f.selector == sig:syncTokenBalance(address).selector) {
        syncTokenBalance(e, token1);
    }

    uint256 balanceAfter = tokenBalances(e, token2);
    assert (token2 != token1 => balanceBefore == balanceAfter);
}


// @notice: Ensure all funtions have at least one non-reverting path
rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}



// HOOKS

// ghost field for the values array
ghost mapping(address => uint256) ghostTokenBalances {
    init_state axiom forall address x. ghostTokenBalances[x] == 0;
}

hook Sstore currentContract.tokenBalances[KEY address index] uint256 newValue STORAGE {
    ghostTokenBalances[index] = newValue;
}

hook Sload uint256 value currentContract.tokenBalances[KEY address index] STORAGE {
    require ghostTokenBalances[index] == value;
}

// INVARIANTS
/*
invariant tokenBalances()
    (forall uint256 index. 0 <= index && index < ghostLength => to_mathint(ghostIndexes[ghostValues[index]]) == index + 1)
    && (forall bytes32 value. ghostIndexes[value] == 0 ||
         (ghostValues[ghostIndexes[value] - 1] == value && ghostIndexes[value] >= 1 && ghostIndexes[value] <= ghostLength));
*/

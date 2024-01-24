using DummyERC20A as _DummyERC20A;

///////////////// METHODS //////////////////////

// author: z0ld
methods {

    // Harness
    function afterTransferOut(address) external;
    // envfree
    function isController(address) external returns (bool) envfree;
    function wntAddress() external returns (address) envfree;
    function holdingAddress() external returns (address) envfree;

    // StrictBank
    function recordTransferIn(address) external returns (uint256);
    function syncTokenBalance(address) external returns (uint256);
    // envfree
    function tokenBalances(address) external returns (uint256) envfree;

    // Bank
    function transferOut(address, address, uint256) external;
    function transferOut(address, address, uint256, bool) external;
    function transferOutNativeToken(address, uint256) external;

    // ERC20
    function _.name() external  => DISPATCHER(true);
    function _.symbol() external  => DISPATCHER(true);
    function _.decimals() external  => DISPATCHER(true);
    function _.totalSupply() external  => DISPATCHER(true);
    function _.balanceOf(address) external  => DISPATCHER(true);
    function _.allowance(address,address) external  => DISPATCHER(true);
    function _.approve(address,uint256) external  => DISPATCHER(true);
    function _.transfer(address,uint256) external  => DISPATCHER(true);
    function _.transferFrom(address,address,uint256) external  => DISPATCHER(true);

    // DataStore
    function _.getUint(bytes32) external => DISPATCHER(true);
    function _.getAddress(bytes32) external => DISPATCHER(true);
    function _.getBytes32(bytes32) external => DISPATCHER(true);

    // RoleStore
    function _.hasRole(address,bytes32) external => DISPATCHER(true);

    // WNT
    function _.deposit() external => DISPATCHER(true);
    function _.withdraw(uint256) external => DISPATCHER(true);
}

///////////////// DEFINITIONS /////////////////////

definition MAX_UINT256() returns uint256 = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;

definition PURE_VIEW_FUNCTIONS(method f) returns bool = f.isView || f.isPure;
definition RECEIVE_FUNCTIONS(method f) returns bool = f.isFallback;

definition TRANSFER_OUT_NATIVE_FUNCTIONS(method f) returns bool = 
    f.selector == sig:transferOut(address, address, uint256, bool).selector
    || f.selector == sig:transferOutNativeToken(address, uint256).selector;

definition TRANSFER_OUT_FUNCTIONS(method f) returns bool = 
    f.selector == sig:transferOut(address, address, uint256).selector
    || TRANSFER_OUT_NATIVE_FUNCTIONS(f);

definition HARNESS_FUNCTIONS(method f) returns bool = 
    f.selector == sig:afterTransferOut(address).selector
    || f.selector == sig:isController(address).selector
    || f.selector == sig:wntAddress().selector;

////////////////// FUNCTIONS //////////////////////

function setupEssential(env e) {
    require(e.msg.value == 0);
    require(e.block.number != 0);
}

///////////////// GHOSTS & HOOKS //////////////////

// Ghost copy of tokenBalances[]

ghost mapping(address => uint256) ghostTokenBalancesPrev {
    init_state axiom forall address token. ghostTokenBalancesPrev[token] == 0;
}

ghost mapping(address => uint256) ghostTokenBalances {
    init_state axiom forall address token. ghostTokenBalances[token] == 0;
}

hook Sstore tokenBalances[KEY address token] uint256 balance (uint256 prevBalance) STORAGE {
    ghostTokenBalancesPrev[token] = prevBalance;
    ghostTokenBalances[token] = balance;
}

hook Sload uint256 balance tokenBalances[KEY address token] STORAGE {
    require(ghostTokenBalances[token] == balance);
}

// Ghost copy of _DummyERC20A.balances[]

ghost mapping(address => uint256) ghostDummyERC20ABalances {
    init_state axiom forall address account. ghostDummyERC20ABalances[account] == 0;
}

hook Sstore _DummyERC20A.balances[KEY address account] uint256 balance STORAGE {
    ghostDummyERC20ABalances[account] = balance;
}

hook Sload uint256 balance _DummyERC20A.balances[KEY address account] STORAGE {
    require(ghostDummyERC20ABalances[account] == balance);
}

///////////////// PROPERTIES //////////////////////

// [1-3] `tokenBalances` storage variable should be equal to balance of current contract 
invariant tokenBalancesSolvency() ghostTokenBalances[_DummyERC20A] == ghostDummyERC20ABalances[currentContract] filtered { 
    f -> !PURE_VIEW_FUNCTIONS(f) && !HARNESS_FUNCTIONS(f) 
}

// [4] interaction with a token should not change balance of another token
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

    assert(token2 != token1 => balanceBefore == balanceAfter);
} 

// [5-9] onlyController can execute non-view functions, otherwise got reverted
rule onlyControllerCouldChangeState(env e, method f, calldataarg args) filtered { 
    f -> !PURE_VIEW_FUNCTIONS(f) && !RECEIVE_FUNCTIONS(f) && !HARNESS_FUNCTIONS(f) 
} {

    bool controller = isController(e.msg.sender);

    storage before = lastStorage;

    f@withrevert(e, args);
    bool reverted = lastReverted;

    storage after = lastStorage;

    assert(!controller => reverted);
    assert(!reverted && before[currentContract] != after[currentContract] => controller);
}

// [10] recordTransferIn() should update token balance in a big way 
invariant recordTransferInTokenBalanceGreater(address token) ghostTokenBalances[token] >= ghostTokenBalancesPrev[token] filtered {
    f -> f.selector == sig:recordTransferIn(address).selector 
    }

// [11-12] receive native tokens via payable fallback from `wnt` contract
rule receiveNativeTokensFromWnt(env e, method f, calldataarg args, uint256 amount) filtered { 
    f -> RECEIVE_FUNCTIONS(f) 
} {
    require(e.block.timestamp != 0);
    require(e.msg.sender != currentContract);
    require(amount == e.msg.value);

    // Can send native nokens
    require(amount > 0 && amount <= nativeBalances[e.msg.sender]);

    // Can accept native nokens
    uint256 before = nativeBalances[currentContract];
    require(require_uint256(MAX_UINT256() - before) >= amount);

    f@withrevert(e, args);
    bool reverted = lastReverted;

    uint256 after = nativeBalances[currentContract];

    assert(!reverted => e.msg.sender == wntAddress() && assert_uint256(after - before) == amount);
    assert(e.msg.sender != wntAddress() => reverted);
}

// [13-14] transfer out to the current contract is forbidden
rule transferOutToCurrentContractForbidden(env e, method f, address token, address receiver, uint256 amount) filtered { 
    f -> TRANSFER_OUT_FUNCTIONS(f) 
} {

    if(f.selector == sig:transferOut(address, address, uint256).selector) {
        transferOut@withrevert(e, token, receiver, amount);
    } else if (f.selector == sig:transferOut(address, address, uint256, bool).selector) {
        bool shouldUnwrapNativeToken;
        transferOut@withrevert(e, token, receiver, amount, shouldUnwrapNativeToken);
    } else if(f.selector == sig:transferOutNativeToken(address, uint256).selector) {
        transferOutNativeToken@withrevert(e, receiver, amount);
    }

    assert(receiver == currentContract => lastReverted);
}

// [15-18] transfer out should correctly update all balances
rule transferOutSolvency(env e, address token, address receiver, address holding, uint256 amount) {

    require isController(e.msg.sender);

    require(token == _DummyERC20A);
    requireInvariant tokenBalancesSolvency();

    require(receiver != currentContract);
    require(holding != currentContract && holding == holdingAddress());

    uint256 tokenBalancesBefore = tokenBalances(token);
    require(tokenBalancesBefore >= amount);

    uint256 senderBefore = _DummyERC20A.balanceOf(e, currentContract);
    uint256 receiverBefore = _DummyERC20A.balanceOf(e, receiver);
    uint256 holdingBefore = _DummyERC20A.balanceOf(e, holding);

    transferOut(e, token, receiver, amount);

    uint256 tokenBalancesAfter = tokenBalances(token);
    uint256 senderAfter = _DummyERC20A.balanceOf(e, currentContract);
    uint256 receiverAfter = _DummyERC20A.balanceOf(e, receiver);
    uint256 holdingAfter = _DummyERC20A.balanceOf(e, holding);

    bool balanceChanged = tokenBalancesBefore != tokenBalancesAfter 
        || senderBefore != senderAfter 
        || receiverBefore != receiverAfter
        || holdingBefore != holdingAfter;

    assert(amount != 0 => 
        balanceChanged 
        && assert_uint256(tokenBalancesBefore - tokenBalancesAfter) == amount
        && assert_uint256(senderBefore - senderAfter) == amount
        // receiver or holding should receive tokens
        && (receiverBefore != receiverAfter 
            ? assert_uint256(receiverAfter - receiverBefore) == amount
            : assert_uint256(holdingAfter - holdingBefore) == amount)
    );
}

// [19] syncTokenBalance() integrity
rule syncTokenBalanceIntegrity(env e, address token) {
    assert(syncTokenBalance(e, token) == ghostTokenBalances[token]);
}

// [20] recordTransferIn() integrity
rule recordTransferInIntegrity(env e, address token) {
    assert(recordTransferIn(e, token) == require_uint256(ghostTokenBalances[token] - ghostTokenBalancesPrev[token]));
}

rule notRevertedPossibility(env e, method f, calldataarg args) {
    f@withrevert(e, args);
    satisfy(!lastReverted); 
}

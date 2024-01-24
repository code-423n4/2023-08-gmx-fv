
// author: 0xpoolboy
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

    // Harness
    function ERC20TokenBalanceOf(address, address) external returns (uint256) envfree;
    function getHoldingAddress() external returns (address) envfree;
    function getTokenGasLimit(address token) external returns (uint256) envfree;
}

rule sanity_satisfy(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}

// syncTokenBalance, afterTransferOut, and recordTransferIn should not change tokenBalances[token1] where token1 != token2
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

// This rule catches mutations/certora/bug0
rule syncTokenBalanceCorrectness(
    env e,
    address token
) {
    bool isController = isController(e);
    // token.balanceOf(currentContract);
    uint256 actualTokenBalance = ERC20TokenBalanceOf(token, currentContract);

    uint256 returnedValue = syncTokenBalance@withrevert(e, token);
    bool syncTokenBalanceReverted = lastReverted;

    uint256 writtenValue = tokenBalances(token);

    assert !isController <=> syncTokenBalanceReverted;
    assert !syncTokenBalanceReverted => (returnedValue == actualTokenBalance && writtenValue == actualTokenBalance);
}

rule recordTransferInCorrectness(
    env e,
    address token
) {
    bool isController = isController(e);

    mathint actualTokenBalanceBefore = ERC20TokenBalanceOf(token, currentContract);
    mathint lastRecordedTokenBalanceBefore = tokenBalances(token);

    mathint amountRecorded = recordTransferIn@withrevert(e, token);
    bool recordTransferInReverted = lastReverted;

    mathint actualTokenBalanceAfter = ERC20TokenBalanceOf(token, currentContract);
    mathint lastRecordedTokenBalanceAfter = tokenBalances(token);

    assert (actualTokenBalanceBefore - lastRecordedTokenBalanceBefore < 0 || !isController)<=> recordTransferInReverted,
        "function should only revert when send does not hold controller role or when balance was withdrawn";
    assert !recordTransferInReverted => actualTokenBalanceBefore - lastRecordedTokenBalanceBefore == amountRecorded,
        "the returned amount should be correct";
    assert !recordTransferInReverted => lastRecordedTokenBalanceAfter == actualTokenBalanceAfter,
        "recordTransferIn should sync";
    assert actualTokenBalanceBefore == actualTokenBalanceAfter,
        "recordTransferIn should not change the actualy token balance";
}

rule transferOutCorrectness(
    env e,
    address token,
    address receiver,
    uint256 amount
) {
    bool isController = isController(e);
    require receiver != 0;

    mathint actualTokenBalanceBefore = ERC20TokenBalanceOf(token, currentContract);
    mathint receiverTokenBalanceBefore = ERC20TokenBalanceOf(token, receiver);
    mathint holdingTokenBalanceBefore = ERC20TokenBalanceOf(token, getHoldingAddress());
    require holdingTokenBalanceBefore == 0; // Assume address balance can't overflow;

    transferOut@withrevert(e, token, receiver, amount);
    bool transferOutReverted = lastReverted;

    mathint actualTokenBalanceAfter = ERC20TokenBalanceOf(token, currentContract);
    mathint receiverTokenBalanceAfter = ERC20TokenBalanceOf(token, receiver);
    mathint tokenBalancesAfter = tokenBalances(token);
    mathint holdingTokenBalanceAfter = ERC20TokenBalanceOf(token, getHoldingAddress());

    assert (!isController || receiver == currentContract
            || to_mathint(amount) > actualTokenBalanceBefore
            || getTokenGasLimit(token) == 0 && amount != 0
            || (getHoldingAddress() == 0 && amount + receiverTokenBalanceBefore >=  2^256)
           ) <=> transferOutReverted, "Should not revert";
    assert !transferOutReverted => actualTokenBalanceBefore - amount == actualTokenBalanceAfter, "Should deduct correct amount from contract";
    // transfers correct amount to receiver
    assert (!transferOutReverted && amount + receiverTokenBalanceBefore <  2^256) => receiverTokenBalanceBefore + amount == receiverTokenBalanceAfter, "Should updated receiver address correctly";
    assert (!transferOutReverted && amount + receiverTokenBalanceBefore >= 2^256) => holdingTokenBalanceBefore + amount == holdingTokenBalanceAfter, "Should update receiver address correctly";
    // updates local state
    assert !transferOutReverted => tokenBalancesAfter == actualTokenBalanceAfter, "Should update tokenBalances";
}
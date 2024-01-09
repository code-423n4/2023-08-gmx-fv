// author: jokrhub
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
    function getBalanceOf(address token, address contractAddress) external returns (uint256) envfree;
    function getHoldingAddress() external returns (address) envfree;
    function getWntAddress() external returns (address) envfree;
    function getEthBalance(address account) external returns (uint256) envfree;
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

rule syncTokenBalanceUnitTest (env e, address token) {
    uint256 currentBalance = getBalanceOf(token, currentContract);

    uint256 expectedBalance = syncTokenBalance(e, token);
    uint256 tokenBalance = tokenBalances(token);
    assert currentBalance == tokenBalance && currentBalance == expectedBalance;
    
    assert(isControllerHarness(e));   
}

rule recordTransferInUnitTest(env e, address token) {
    uint256 prevTokenBalance = tokenBalances(token);
    
    uint256 expectedBalance = recordTransferIn(e, token);

    uint256 currentBalance = getBalanceOf(token, currentContract);
    uint256 tokenBalance = tokenBalances(token);

    assert(currentBalance == tokenBalance && expectedBalance == assert_uint256(tokenBalance - prevTokenBalance));
    assert(isControllerHarness(e));   
}

rule afterTransferOutUnitTest (env e, address token) {
    uint256 currentBalance = getBalanceOf(token, currentContract);
    afterTransferOutHarness(e, token);
    uint256 tokenBalance = tokenBalances(token);
    assert currentBalance == tokenBalance;
}

//@todo check bankBalance
rule transferOutUnitTest (env e, address token, address receiver, uint256 amount) {
    address holdingAddress = getHoldingAddress();

    uint256 bankBalanceBefore = getBalanceOf(token, currentContract);
    uint256 holdingBalanceBefore = getBalanceOf(token, holdingAddress);
    uint256 receiverBalanceBefore =  getBalanceOf(token, receiver);

    transferOut(e, token, receiver, amount);

    uint256 bankBalanceAfter = getBalanceOf(token, currentContract);
    uint256 holdingBalanceAfter = getBalanceOf(token, holdingAddress);
    uint256 receiverBalanceAfter =  getBalanceOf(token, receiver);


    uint256 bankTokenBalance = tokenBalances(token);

    mathint check1 = holdingBalanceBefore + amount;
    mathint check2 = receiverBalanceBefore + amount;

    assert (
        ( check1 <= max_uint =>  holdingBalanceAfter == assert_uint256(holdingBalanceBefore + amount) )  ||
        ( check2 <= max_uint =>  receiverBalanceAfter == assert_uint256(receiverBalanceBefore + amount) )
    );
    // assert bankBalanceAfter == assert_uint256(bankBalanceBefore - amount);
    assert bankTokenBalance == bankBalanceAfter;
    assert(isControllerHarness(e));   
    
}

rule transferOutShouldRevert(env e, address token, address receiver, uint256 amount) {
    transferOut@withrevert(e, token, receiver, amount);
    assert (amount != 0 && receiver == 0) || receiver == currentContract => lastReverted;
}   



//@todo check bankBalance
rule transferOutNativeTokenUintTest (env e, address receiver, uint256 amount) {
    address token = getWntAddress();
    address holdingAddress = getHoldingAddress();

    uint256 receiverEthBefore = getEthBalance(receiver);
    uint256 bankBalanceBefore = getBalanceOf(token, currentContract);
    uint256 holdingBalanceBefore = getBalanceOf(token, holdingAddress);
    uint256 receiverBalanceBefore =  getBalanceOf(token, receiver);

    transferOutNativeToken(e, receiver, amount);

    uint256 receiverEthAfter = getEthBalance(receiver);
    uint256 bankBalanceAfter = getBalanceOf(token, currentContract);
    uint256 holdingBalanceAfter = getBalanceOf(token, holdingAddress);
    uint256 receiverBalanceAfter =  getBalanceOf(token, receiver);

    uint256 bankTokenBalance = tokenBalances(token);

    mathint check1 = holdingBalanceBefore + amount;
    mathint check2 = receiverBalanceBefore + amount;
    mathint check3 = receiverEthBefore + amount;

    assert (
        ( check1 <= max_uint =>  holdingBalanceAfter == assert_uint256(holdingBalanceBefore + amount) )  ||
        ( check2 <= max_uint =>  receiverBalanceAfter == assert_uint256(receiverBalanceBefore + amount) ) ||
        ( check3 <= max_uint =>  receiverEthAfter == assert_uint256(receiverEthBefore + amount) )
    );
    assert bankTokenBalance == bankBalanceAfter;
    assert(isControllerHarness(e));   

}

rule transferOutNativeTokenShouldRevert(env e, address token, address receiver, uint256 amount) {
    transferOutNativeToken@withrevert(e, receiver, amount);
    assert (amount != 0 && receiver == 0) || receiver == currentContract => lastReverted;
}   

rule transferOutNativeUnitTest (env e, address token, address receiver, uint256 amount, bool shouldUnwrapNativeToken) {
    address wnt = getWntAddress();
    address holdingAddress = getHoldingAddress();

    uint256 receiverEthBefore = getEthBalance(receiver);
    uint256 holdingBalanceBefore = getBalanceOf(token, holdingAddress);
    uint256 receiverBalanceBefore =  getBalanceOf(token, receiver);

    transferOut(e, token, receiver, amount, shouldUnwrapNativeToken);

    uint256 receiverEthAfter = getEthBalance(receiver);
    uint256 holdingBalanceAfter = getBalanceOf(token, holdingAddress);
    uint256 receiverBalanceAfter =  getBalanceOf(token, receiver);
    uint256 bankBalanceAfter = getBalanceOf(token, currentContract);

    uint256 bankTokenBalance = tokenBalances(token);

    mathint check1 = holdingBalanceBefore + amount;
    mathint check2 = receiverBalanceBefore + amount;
    mathint check3 = receiverEthBefore + amount;

    assert (
        ( check1 <= max_uint =>  holdingBalanceAfter == assert_uint256(holdingBalanceBefore + amount) )  ||
        ( check2 <= max_uint =>  receiverBalanceAfter == assert_uint256(receiverBalanceBefore + amount) ) ||
        ( check3 <= max_uint =>  receiverEthAfter == assert_uint256(receiverEthBefore + amount) )
    );

    assert (token != wnt || !shouldUnwrapNativeToken) => receiverEthAfter == receiverEthBefore;
    assert bankTokenBalance == bankBalanceAfter;
    assert(isControllerHarness(e));   

}
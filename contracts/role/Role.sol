// SPDX-License-Identifier: BUSL-1.1

pragma solidity ^0.8.0;

/**
 * @title Role
 * @dev Library for role keys
 */
library Role {
    /**
     * @dev The ROLE_ADMIN role.
     */
    bytes32 public constant ROLE_ADMIN = 0x56908b85b56869d7c69cd020749874f238259af9646ca930287866cdd660b7d9; // keccak256(abi.encode("ROLE_ADMIN"))

    /**
     * @dev The TIMELOCK_ADMIN role.
     */
    bytes32 public constant TIMELOCK_ADMIN = 0xf49b0c86b385620e25b0985905d1a112a5f1bc1d51a7a292a8cdf112b3a7c47c; // keccak256(abi.encode("TIMELOCK_ADMIN"));

    /**
     * @dev The TIMELOCK_MULTISIG role.
     */
    bytes32 public constant TIMELOCK_MULTISIG = 0xe068a8d811c3c8290a8be34607cfa3184b26ffb8dea4dde7a451adfba9fa173a; // keccak256(abi.encode("TIMELOCK_MULTISIG"));

    /**
     * @dev The CONFIG_KEEPER role.
     */
    bytes32 public constant CONFIG_KEEPER = 0x901fb3de937a1dcb6ecaf26886fda47a088e74f36232a0673eade97079dc225b; // keccak256(abi.encode("CONFIG_KEEPER"));

    /**
     * @dev The CONTROLLER role.
     */
    bytes32 public constant CONTROLLER = 0x97adf037b2472f4a6a9825eff7d2dd45e37f2dc308df2a260d6a72af4189a65b; // keccak256(abi.encode("CONTROLLER"));

    /**
     * @dev The ROUTER_PLUGIN role.
     */
    bytes32 public constant ROUTER_PLUGIN = 0xc82e6cc76072f8edb32d42796e58e13ab6e145524eb6b36c073be82f20d410f3; // keccak256(abi.encode("ROUTER_PLUGIN"));

    /**
     * @dev The MARKET_KEEPER role.
     */
    bytes32 public constant MARKET_KEEPER = 0xd66692c70b60cf1337e643d6a6473f6865d8c03f3c26b460df3d19b504fb46ae; // keccak256(abi.encode("MARKET_KEEPER"));

    /**
     * @dev The FEE_KEEPER role.
     */
    bytes32 public constant FEE_KEEPER = 0xd66692c70b60cf1337e643d6a6473f6865d8c03f3c26b460df3d19b504fb46ae; // keccak256(abi.encode("FEE_KEEPER"));

    /**
     * @dev The ORDER_KEEPER role.
     */
    bytes32 public constant ORDER_KEEPER = 0x40a07f8f0fc57fcf18b093d96362a8e661eaac7b7e6edbf66f242111f83a6794; // keccak256(abi.encode("ORDER_KEEPER"));

    /**
     * @dev The FROZEN_ORDER_KEEPER role.
     */
    bytes32 public constant FROZEN_ORDER_KEEPER = 0xcb6c7bc0d25d73c91008af44527b80c56dee4db8965845d926a25659a4a8bc07; // keccak256(abi.encode("FROZEN_ORDER_KEEPER"));

    /**
     * @dev The PRICING_KEEPER role.
     */
    bytes32 public constant PRICING_KEEPER = 0x2700e36dc4e6a0daa977bffd4368adbd48f8058da74152919f91f58eddb42103; // keccak256(abi.encode("PRICING_KEEPER"));
    /**
     * @dev The LIQUIDATION_KEEPER role.
     */
    bytes32 public constant LIQUIDATION_KEEPER = 0x556c788ffc0574ec93966d808c170833d96489c9c58f5bcb3dadf711ba28720e; // keccak256(abi.encode("LIQUIDATION_KEEPER"));
    /**
     * @dev The ADL_KEEPER role.
     */
    bytes32 public constant ADL_KEEPER = 0xb37d64edaeaf5e634c13682dbd813f5a12fec9eb4f74433a089e7a3c3289af91; // keccak256(abi.encode("ADL_KEEPER"));
}

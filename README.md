# GMX Formal Verification Contest Details
- Total Prize Pool: $40,000 USDC
  - High/Medium awards: $22,000 USDC
  - Coverage awards: $14,000 USDC
  - Participation awards: $4,000 USDC
- Join [C4 Discord](https://discord.gg/code4rena) to register
- [Register](https://docs.google.com/forms/d/e/1FAIpQLSf7rGov3q0A_UNmKckv-tzR5snLGibZWF9y9dhgXUBZRZ0EVw/viewform) through Certora to gain access to the prover
  - Resources to get familiar with the Certora Prover will be emailed to registrants along with their Certora key.
- Learn about [GMX](https://github.com/gmx-io/gmx-synthetics)
- Starts August 07, 2023 20:00 UTC
- Ends August 28, 2023 20:00 UTC

## Incentives

The total reward will be split into three categories: participation, bugs, and mutations. Participation rewards are distributed evenly amongst those catching all public mutations found in `certora/mutations/certora/`. Private mutations will be used to evaluate coverage. Bugs are rewarded using the [Code4rena incentive model](https://docs.code4rena.com/awarding/incentive-model-and-awards). Low, Informational, and Gas findings may be submitted but will not be considered for the reward. Severity will be determined by Certora using [Code4rena criteria](https://code4rena.com/judging-criteria/). Bug submissions require details such as impact, exploit scenario, mitigation and CVL property violated to be eligible for rewards. In the case that no high or medium findings, the coverage pool will be increased to 90%.

## Setup

* [Import](https://github.com/new/import) this repository as a private repo and give access to teryanarmen and nd-certora. 
* Add `CERTORAKEY` as a repository secret for CI. Work in the `certora` branch. 
* Install the Certora Prover, instructions below.
* Submit your work by creating a pull request from `certora` to `main` in your repo.
* Note the Certora Prover [docs](docs.certora.com).

## Scope

* Oracle.sol
* OracleStore.sol
* RoleStore.sol
* DataStore.sol
* StrictBank.sol

Oracle is more challenging to verify. Feel free to ask questions if you have any issues with the tool such as errors or timeouts. OracleStore has an example of how to use the specification for EnumerableSet, you can do something similar for RoleStore and DataStore.

## Participation 

The `certora` directory that consists of 5 sub-directories - `harnesses`, `confs`, `mutations`, `helpers` and `specs`. These should contain the entire preliminary setup to allow you to start writing rules. Each sub-directory contains a different component of the verification project and may contain additional sub-directories to maintain organization. Try to keep a similar structure when adding new files.

Gather all the rules and invariants that you were able to verify in `<Contract>.spec` under `certora/specs`. Before submitting this spec, make sure to check the following things:
* Ensure all properties are finished, reachable, and not timing out. Any properties not catching real bugs must also be passing.
* Document each property.
* It is recommended to inject bugs to test your properties.

For each real bug open an issue on your private repository with:
* Short description of the problem
* Impact
* Expected and actual behaviors of the system
* A concrete example of the exploit
* CVL property violated 

For properties that find real bugs, create `<Contract>Issues.spec` with only properties that catch bugs. For each of these specs, create a separate `.conf` file name `contract_violated.conf` Document each property with a short description of the attack vector found in the violation counter example with concrete values if possible. Also add a reference to the GitHub issue that further explains the bug.

At the end of the formal verification contest, private mutations will be pushed to the public repo. Pull any changes from the public repo and open a pull request within your repository from the `certora` branch to the `main` branch. Upon opening the PR, the CI will be triggered, and the result will be evaluated by the judges.


## Testing

It is recommended to test your spec against the publicly available mutations to ensure your rules are working properly. You can use `check-all-mutations.sh`. This script will inject either the bugs injected by you or by certora one by one and run your spec against them.

## Installation

### Installing Manually

Installation instructions can be found [here](https://docs.certora.com/en/latest/docs/user-guide/getting-started/install.html?highlight=install). Briefly, you must install
* Node JS version >= 14.16.
* Yarn version >= 1.22.
* Java Development Kit version >= 11.
* Solidity version 0.8.19.
* One can install Certora with the Python package manager Pip3,
  ```
  pip3 install certora-cli
  ```
* Assuming you are in the root of this reposotory, install the remaining dependencies with
  ```
  yarn install
  ```

### Installing With Docker

There is a docker file in the `docker` folder, with instructions to create an environment with
dependencies required for executing Certora. The container will be created with a user with
username 'docker' and password 'docker'. On a Unix system with an sh shell, the docker container
can be built with the `docker/build.sh` script. For example
```
docker/build.sh auto auto
```
builds the container with the docker user having the same user id and group id as the user executing
the `build.sh` script. The user id and group id are inferred using the `id` command. This is the
typical case.

If one wants to specify the user id and/or group id manually, then that is also possible. The first
argument to the `build.sh` script is the user id and the second argument is the group id,
```
docker/build.sh 1234 4321
```

When the container is built, then it can be started with the `docker/run.sh` script. For example
```
docker/run.sh "`realpath .`"
```
where the argument to `run.sh` is the absolute path to this repository (2023-08-gmx-fv).
The repository will then be volume mapped for use inside the running docker container.

IMPORTANT: The docker container is automatically removed after exiting, so that all changes to the
container will be deleted. But since the repository 2023-08-gmx-fv is volume mapped inside
the container, changes to the repository will be persistent, even after the docker container has
exited.

Inside the running docker container, go to the folder `~/2023-08-gmx-fv` and run
```
yarn install
```
to install the last dependencies.

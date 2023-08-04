# GMX Formal Verification Contest Details
- Total Prize Pool: $40,000 USDC
  - High/Medium awards: $22,000 USDC
  - Injected bug awards: $14,000 USDC
  - Participation awards: $4,000 USDC
- Join [C4 Discord](https://discord.gg/code4rena) to register
- [Register](https://docs.google.com/forms/d/e/1FAIpQLSf7rGov3q0A_UNmKckv-tzR5snLGibZWF9y9dhgXUBZRZ0EVw/viewform) through Certora to gain access to the prover
  - Resources to get familiar with the Certora Prover will be emailed to registrants along with their Certora key. 
- Starts August 07, 2023 20:00 UTC
- Ends August 28, 2023 20:00 UTC

## Incentives

The total reward will be split into three categories: participation, bugs, and mutations. Participation rewards are distributed evenly amongst those catching all public mutations. Private mutations will be used to evaluate coverage. Findings are rewarded using the [Code4rena incentive model](https://docs.code4rena.com/awarding/incentive-model-and-awards). Finding submissions require details such as impact, exploit scenario, and mitigation. In the case that no high or medium findings, the coverage pool will be increased to 90%.

To receive rewards for your findings, submissions must include a rule that detects the bug. The value of each bug will be distributed evenly. A bug's value is equal to VALUE * 0.9^FINDERS. High severity bugs have a value of 4 and medium severity bugs have a value of 1. Low, Informational, and Gas findings may be submitted but will not be considered for the reward. Severity will be determined by Certora using [Code4rena criteria](https://code4rena.com/judging-criteria/).  

## Setup

* [Import](https://github.com/new/import) the [public repository]() as a private repo and give access to teryanarmen. 
* Add `CERTORAKEY` as a repository secret for CI. Work in the `certora-contest` branch. 
* Submit your work by creating a pull request from `certora-contest` to `certora` in your repo.
* Note the Certora Prover [docs](docs.certora.com).


## Participation 

The `certora` directory that consists of 5 sub-directories - `harnesses`, `confs`, `tests` and `specs`. These should contain the entire preliminary setup to allow you to start writing rules. Each sub-directory contains a different component of the verification project and may contain additional sub-directories to maintain organization. Try to keep a similar structure when adding new files.

In the `certora/spec` directory, you will find a spec file named `<Contract>.spec` that inherits from the relevant `setup.spec` file. In this spec, gather all the rules and invariants that you were able to verify. Before submitting this spec, make sure to check the following things:
* Ensure all properties are finished, reachable, and not timing out. Any properties not catching real bugs must also be passing.
* Document each property.
* It is recommended to inject a bugs to test your properties.

For each real bug open an issue on your private repository with:
* Short description of the problem
* Impact
* Expected and actual behaviours of the system
* A concrete example of the exploit
* CVL property violated 

For properties that find real bugs, create `<Contract>Issues.spec` with  only properties that catch bugs. Document each property with a short description of the attack vector found in the violation counter example with concrete values if possible. Also add a reference to the GitHub issue that further explains the bug.

At the end of the formal verification contest, private mutations will be pushed to the public repo. Pull any changes from the public repo and open a pull request within your repository from the `certora-contest` branch to the `certora` branch. Upon opening the PR, the CI will be triggered, and the result will be evaluated by the judges.


## Testing

It is recommended to test your spec against the publicly available mutations to ensure your rules are working properly. You can use `verify_all_mutations.sh`. This script will inject either the bugs injected by you or by certora one by one and run your spec against them.



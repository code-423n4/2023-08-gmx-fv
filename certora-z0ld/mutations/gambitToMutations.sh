#!/bin/bash

# Gambit. Start from git root directory. Example:
# gambit mutate -f ./contracts/rewards/RewardsDistributor.sol --solc_remappings @aave=node_modules/@aave

# Create bugs. Start from git root directory. Example:
# certora/mutations/gambitToMutations.sh contracts/rewards/RewardsDistributor.sol RewardsDistributor_181

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <target_sol_path> <bugs_directory_name>"
  exit 1
fi

sol_path="$1"
bugs="$2"

# Create the destination directory for the patch file
dest_dir="certora/mutations/${bugs}"
mkdir -p "${dest_dir}"

# Iterate over each directory in the `gambit_out/mutants/*` path
for dir in ./gambit_out/mutants/*/"${sol_path}"; do
  # Extract the mutant number (X)
  mutant_number=$(basename $(dirname $(dirname $(dirname "${dir}"))))

  # Copy the file to the sol_path
  cp "${dir}" "${sol_path}"

  # Execute git diff and store the result in the patch file
  git diff certora -- "${sol_path}" > "${dest_dir}/bug${mutant_number}.patch"
done

git restore "${sol_path}" 

echo "Operation complete."
certoraMutate --prover_conf certora/confs/dataStore_verified.conf --mutation_conf certora/confs/gambit/dataStore.conf
mv collect.json collect_dataStore.json
# certoraMutate --prover_conf certora/confs/roleStore_verified.conf --mutation_conf certora/confs/gambit/roleStore.conf
# mv collect.json collect_roleStore.json
# certoraMutate --prover_conf certora/confs/oracleStore_verified.conf --mutation_conf certora/confs/gambit/oracleStore.conf
# mv collect.json collect_oracleStore.json
# certoraMutate --prover_conf certora/confs/oracle_verified.conf --mutation_conf certora/confs/gambit/oracle.conf 
# mv collect.json collect_oracle.json
# certoraMutate --prover_conf certora/confs/strictBank_verified.conf --mutation_conf certora/confs/gambit/strictBank.conf 
# mv collect.json collect_strictBank.json
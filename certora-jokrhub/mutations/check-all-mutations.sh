# take first input from user and use it as the path to the folder that contains the patch files
# apply all patches in to munged using git apply and run all scripts in ../scripts/ against each patch file
for f in certora/mutations/$1/*.patch
do
    echo "Applying $f"
    git apply $f
    echo "Running Prover"
    for conf in certora/confs/*.conf
    do
        echo "Running $conf"
        certoraRun $conf
    done
    echo "Reverting $f"
    git apply -R $f
done
# Example: checkAllMutations.sh oracle participants
for f in certora/mutations/$2_$1/bug*.patch
do
    wildcard=${f##"certora/mutations/$2_$1"/bug}
    wildcard=${wildcard%.patch}
    certora/mutations/checkMutation.sh $1 $2 $wildcard
done
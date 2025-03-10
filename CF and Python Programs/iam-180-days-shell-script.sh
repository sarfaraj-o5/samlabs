# Script displays users Active access keys with created date and the age of the keys.\n Only the keys that are 180 days olders


if [[ -z "$1" ]]; then
   echo "Profile not mentioned, Please run as ./iam_access_keyage profile"
   exit 1
fi

profile=$1

Today=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

printf "The list of all the users Active access keys with created date and the age of the keys.\n Only the keys that are 180 days olders are printed here.\n"
function calcage(){
        CURRENT_KEY_ID=$(aws iam list-access-keys --user-name "$user" --profile "$profile" --output json |jq '.AccessKeyMetadata[] | select(.Status == "Active")| .CreateDate' | tr -d '"')
        ACCESS_KEY=$(aws iam list-access-keys --user-name "$user"  --profile "$profile"  --output json |jq '.AccessKeyMetadata[] | select(.Status == "Active")| .AccessKeyId' | tr -d '"')
        CREATED_ON=$(aws iam list-access-keys --user-name "$user"  --profile "$profile" --output json |jq '.AccessKeyMetadata[] | select(.Status == "Active")| .CreateDate' | tr -d '"')
        for dates in $CURRENT_KEY_ID;
        do
            d1=$(date -jf %Y-%m-%d "$Today" +%s 2> /dev/null)
            d2=$(date -jf %Y-%m-%d "$dates" +%s 2> /dev/null)
            keyageinsec=`expr $d1 - $d2`
            age=`expr $keyageinsec / 172800`

            return $age
        done
}

for user in $(aws iam list-users  --profile "$profile" --output json|jq -r ".Users[].UserName");
do
    calcage "$user"
    # This prints list of all the users whose keys are Active and the Access keys are 180 Days older
    if [[ -n "$ACCESS_KEY" && $age -ge 180 ]]; then
         printf "\nUser: $user \t Key age :$age \n"
         printf "Keys: $ACCESS_KEY \t Created on: $CREATED_ON\n"
    fi
done
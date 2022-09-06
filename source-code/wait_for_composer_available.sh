
# !/bin/bash

n=0
until [[ $n -ge "${3}" ]]
do
  status=0
  res_state=$( gcloud composer environments describe "${1}" --location "${2}" | grep state | awk '{print $2}')
  echo "($n/${3}) state is : $res_state"
  if [ "$res_state" == "RUNNING" ]; then
    break
  fi
  n=$(($n+1))
  sleep "${4}"
done
exit $status
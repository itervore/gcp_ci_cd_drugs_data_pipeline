
# !/bin/bash

n=0
until [[ $n -ge "${4}" ]]
do
  status=0
  # res_state=$( gcloud composer environments describe "${1}" --location "${2}" | grep state | awk '{print $2}')
  custom_comm=$(gcloud composer environments update "${1}" --location "${2}" --update-env-variables="${3}" --verbosity=debug 2>&1)
  echo "$custom_comm"
  if [[ "$custom_comm" == *"ERROR: (gcloud.composer.environments.update) INVALID_ARGUMENT: No change in configuration. Must specify a change to configuration.software_configuration.env_variables"* ]]; then 
    echo "This failure is expected if there is no change to env_variables"
    break
  elif [[ "$custom_comm" == *"ERROR: (gcloud.composer.environments.update) FAILED_PRECONDITION: Cannot update environment in state UPDATING. Environment must be in RUNNING state."* ]]; then
    echo "This failure is expected if environment in state UPDATING"
  else 
    status = 1
    break
  fi
  n=$(($n+1))
  sleep "${5}"
done
exit $status
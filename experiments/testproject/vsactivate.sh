#!/bin/bash
source /Users/raven/development/lib/virtstrap/experiments/testproject/vs.env/bin/activate

# Save the deactivate function from virtualenv under a different name
virtualenvwrapper_original_deactivate=`typeset -f deactivate | sed 's/deactivate/virtualenv_deactivate/g'`
eval "$virtualenvwrapper_original_deactivate"
unset -f deactivate >/dev/null 2>&1

deactivate () {
    virtualenv_deactivate $1

    if [ ! "$1" = "nondestructive" ]
    then
        # Remove this function
        unset -f virtualenv_deactivate >/dev/null 2>&1
        unset -f deactivate >/dev/null 2>&1
    fi
}

#python /Users/raven/development/lib/virtstrap/experiments/testproject/conf/environment.py
#source /Users/raven/development/lib/virtstrap/experiments/testproject/vs.env/generated_env/test.sh

'''
detcord : Action execution on hosts

Micah Martin - knif3
'''

import os.path
import sys
from detcord.exceptions import InvalidDetfile

if not os.path.exists("detfile.py"):
    raise InvalidDetfile("Missing detfile in the current directory")

from inspect import getmembers, isfunction
import detfile
from detcord.actions import ActionGroup

def main():
    env = detfile.env
    if env.get('hosts', False):
        for host in env['hosts']:
            env['current_host'] = host
            Action = ActionGroup(
                host = host,
                user = env['user'],
                password = env['pass']
            )
            getattr(detfile, sys.argv[1])(Action)
            Action.close()

if __name__ == '__main__':
    # Parse the actions in the detfile
    action_functions = []
    for func in getmembers(detfile):
        # Make sure the function is decorated as an action
        if getattr(func[1], 'detcord_action', False):
            #('action',False):
            action_functions += [func]

    # If we have no runnable action, error out
    if not action_functions:
        raise InvalidDetfile("No runnable actions in detfile.py")

    if len(sys.argv) < 2:
        # Print valid functions that the detfile has
        print("USAGE: {} <action>[..<action>]")
        func_strings = []
        for function in action_functions:
            docstring = function[1].__doc__
            if docstring:
                docstring = docstring.strip().split('\n')[0].strip()
            else:
                docstring = "No description"
            func_strings += ["{} - {}".format(function[0], docstring)]
        print("Valid actions for this detfile are:\n\t{}".format("\n\t".join(func_strings)))
        quit()

    for action in sys.argv[1:]:
        if action not in [f[0] for f in action_functions]:
            raise InvalidDetfile("Not a valid action in the detfile: {}".format(action))
    # Make sure we have set hosts for the detfile
    if not detfile.env.get("hosts", False):
        raise InvalidDetfile("No hosts specified in the detfile environment")
    # Actually run the actions
    main()

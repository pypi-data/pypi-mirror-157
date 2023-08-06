from .shared_functions import listPromptInquirer, checkBoxPromptInquirer, runCmd, invalidAnswerExit, promptPyInquirer
from argparse import ArgumentParser
import os, sys
import re

deploy_to_choices = ["github", "heroku"]
command_choices = ["create-update", "update", "delete"]

def main():
    args = takeArgs()
    if not args["to"]:
        args["to"] = listPromptInquirer({
            "name": "deploy_to",
            "question": "where d you want to deploy it?",
            "choices":deploy_to_choices
        })["deploy_to"]
    if not args["path"]:
        # args["path"] = input(f"path of the project folder (current directory: {os.getcwd()}): ")
        args["path"] = promptPyInquirer({
            "type": "input",
            "name": "path",
            "message": f"Path of the project folder: ",
            "default": os.getcwd(),
            "validate": lambda x: "Invalid path" if not os.path.exists(x) else True
        })["path"]
    elif not os.path.exists(args["path"]):
            print("Invalid path")
            sys.exit(5)
    additional_cmd = handleAdditionalCmds(args)
    # runCmd(f"py easy_deployer/{args['to']}.py -p {args['path']} {additional_cmd}") # main command
    if(re.match(".+\.exe$", __file__)):
        # This is Executable (*.exe)
        args_to = f"easy-{args['to']}"
        current_dir = os.path.dirname(__file__)
        runCmd(f"{os.path.join(current_dir, args_to)} -p {args['path']} {additional_cmd}") # main command
    else:
        # Assuming this is a python file (.py)
        runCmd(f"py easy-{args['to']}.py -p {args['path']} {additional_cmd}") # main command

def takeArgs():
    parser = ArgumentParser(prog="github-deployer",
    usage="""""", description="%(prog)s <commands> [options]")
    parser.add_argument("-p", "--path", required=False)
    parser.add_argument("-to", required=False, choices=deploy_to_choices)
    parser.add_argument("-cmd", "--command", choices=command_choices, help="Command to execute")
    parser.add_argument("-q", "--quick", action="store_true", help="")
    args = parser.parse_args()
    return vars(args)

def handleAdditionalCmds(args):
    additional_cmd = ""
    if args["to"] == "github":
        additional_cmd = githubCommands(args)
    elif args["to"] == "heroku":
        additional_cmd = herokuCommands(args)
        # add_addtional_cmds = listPromptInquirer({
        #     "name":"add_addtional_cmds",
        #     "question": "want to add some additional commands?",
        #     "choices": ["Yes", "No"]
        #     })["add_addtional_cmds"]
    return additional_cmd

def githubCommands(args):
    additional_cmd = ""
    command = listPromptInquirer({
        "name":"command",
        "question": "which command you want? (create-update is the default one)",
        "choices": ["create-update", "update", "delete"],
    })['command'] if not args["command"] else args["command"]
    additional_cmd += f"{command} "
    if command == 'create-update':
        pass
    if not args["quick"]:
        add_addtional_cmds = listPromptInquirer({
            "name":"add_addtional_cmds",
            "question": "Want to add some additional commands?",
            "choices": ["Yes", "No"]
            })["add_addtional_cmds"]
        if add_addtional_cmds == "Yes":
            if command != "delete":
                ADD_COLLABORATORS_CHOICE = "Add collaborators"
                GIT_IGNORE_CHOICE = "Add gitIgnore (ignore files)"
                VISIBILITY_CHOICE = "Change the visiblity of an existing repository"
                RESET_TOKEN_CHOICE = "Reset token"
                RESET_USER_CHOICE = "Reset user"
                checkBoxAnswers = checkBoxPromptInquirer({
                    "name": "secondaryOptions",
                    "question": "Add what you want (use spacebar to add stuff and enter to confirm)",
                    "choices": [
                        ADD_COLLABORATORS_CHOICE, GIT_IGNORE_CHOICE,
                        VISIBILITY_CHOICE, RESET_TOKEN_CHOICE, RESET_USER_CHOICE
                    ]
                })
                if(RESET_TOKEN_CHOICE in checkBoxAnswers["secondaryOptions"]) or (RESET_USER_CHOICE in checkBoxAnswers["secondaryOptions"]):
                    additional_cmd += "-new "
                    if RESET_TOKEN_CHOICE in checkBoxAnswers["secondaryOptions"]:
                        additional_cmd += "token "
                    if RESET_USER_CHOICE in checkBoxAnswers["secondaryOptions"]:
                        additional_cmd += "user "
                if(GIT_IGNORE_CHOICE in checkBoxAnswers["secondaryOptions"]):
                    additional_cmd += "-git-ig "
                if(VISIBILITY_CHOICE in checkBoxAnswers["secondaryOptions"]):
                    additional_cmd += "-visibility "
                if(ADD_COLLABORATORS_CHOICE in checkBoxAnswers["secondaryOptions"]):
                    additional_cmd += "-ac "
            else:
                RESET_TOKEN_CHOICE = "Reset token"
                RESET_USER_CHOICE = "Reset user"
                checkBoxAnswers = checkBoxPromptInquirer({
                    "name": "secondaryOptions",
                    "question": "Add what you want (use spacebar to add stuff and enter to confirm)",
                    "choices": [
                        RESET_TOKEN_CHOICE, RESET_USER_CHOICE
                    ]
                })
                if(RESET_TOKEN_CHOICE in checkBoxAnswers["secondaryOptions"]) or (RESET_USER_CHOICE in checkBoxAnswers["secondaryOptions"]):
                    additional_cmd += "-new "
                    if RESET_TOKEN_CHOICE in checkBoxAnswers["secondaryOptions"]:
                        additional_cmd += "token "
                    if RESET_USER_CHOICE in checkBoxAnswers["secondaryOptions"]:
                        additional_cmd += "user "
    return additional_cmd

def herokuCommands(args):
    additional_cmd = ""
    FRAMEWORK_LANGUAGE_CHOICES = ["nodejs", "flask"]
    command = listPromptInquirer({
        "name":"command",
        "question": "which command you want? (create-update is the default one)",
        "choices": ["create-update", "update", "delete"],
    })['command'] if not args["command"] else args["command"]
    additional_cmd += f"{command} "
    if command == 'create-update':
        listAnswers = listPromptInquirer({
                    "name": "language",
                    "question": "what language/framework are you using?",
                    "choices": FRAMEWORK_LANGUAGE_CHOICES
                })
        additional_cmd += f"-lang {listAnswers['language']} "
    if not args["quick"]:
        add_additional_cmds = promptPyInquirer({
            "type": "confirm",
            "name": "add_additional_cmds",
            "message": "Want to add some additional commands?",
        })["add_additional_cmds"]
        if add_additional_cmds:
            NEW_LOGIN = "Force a new login"
            NO_CACHE = "Remove cached info (like application name)"
            additional_cmds = promptPyInquirer({
                "name":"secondaryOptions",
                "type": "checkbox",
                "choices": [
                    {"name": NEW_LOGIN},
                    {"name": NO_CACHE}
                ],
                "message": "Add the option(s) you want "
            })
            if NEW_LOGIN in additional_cmds['secondaryOptions']:
                additional_cmd += f"-new-login "
            if NO_CACHE in additional_cmds['secondaryOptions']:
                additional_cmd += f"-no-cache "
    return additional_cmd
            

if __name__ == "__main__":
    main()
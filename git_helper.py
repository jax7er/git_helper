from glob import glob
from os import getcwd
from os.path import basename
from subprocess import PIPE, run


def is_even(n: int) -> bool:
    """
    Checks whether a number is even

    :param n: the number to check for evenness
    :returns: True if even else False
    """

    return n % 2 == 0


def cmd(text: str) -> str:
    """
    Execute a command by extracting the tokens and passing to subprocess.run
    Capable of extracting one level of double quoted tokens

    :param text: the text of the command written as if in the command line
    :returns: stdout from the command if the return code is 0
    :raises ValueError: if text contains an odd number of quotes
    :raises RuntimeError: if the command returns a non-zero return code
    """

    if not is_even(text.count("\"")):
        raise ValueError("Odd number of quotes in command text")
    
    extracted_tokens = []
    for i, text in enumerate(text.split("\"")):
        if is_even(i):
            extracted_tokens.extend(text.split())
        else:
            extracted_tokens.append(f"\"{text}\"")

    called = run(extracted_tokens, stdout=PIPE, stderr=PIPE)

    if called.returncode == 0:
        return str(called.stdout, "ascii")
    else:
        raise RuntimeError(f"Running \"{cmd}\" failed, stderr:\n{called.stderr}")


def exists(file_path: str) -> bool:
    """
    Checks whether a file/folder exists by using glob.glob

    :param file_path: path of the file/folder to check existence of
    :returns: True if exists else False
    """

    return len(glob(file_path)) == 1


def git_pull() -> str:
    """
    Calls git pull

    :returns: output from command
    """

    return cmd("git pull")


def git_push() -> str:
    """
    Calls git add, commit, and push with user customisable arguments
    Also can create a readme file if it doesn't already exist

    :returns: cumulative output from commands
    """

    default_branch = "master"
    default_create_readme = "y"
    default_readme = f"# {basename(getcwd())}"

    if not exists("README.md"):
        user_in = ""
        while True:
            user_in = input(f"No README.md file found, create one? [{'Y|n' if default_create_readme else 'y|N'}] ").strip().lower() or default_create_readme

            if user_in in ["y", "n"]:
                break
            else:
                print("Enter 'y' for yes, 'n' for no, or nothing for the default")

        if user_in == "y":
            readme_text = input(f"Readme text, default \"{default_readme}\": ").strip() or default_readme

            with open("README.md", "w") as readme_f:
                readme_f.write(readme_text + "\n")

    message = input("Commit message: ").strip()
    branch = input(f"Branch, default {default_branch}: ").strip() or default_branch

    print("Pushing to remote")

    cmd_out = ""
    cmd_out += cmd("git add --all")
    cmd_out += cmd(f"git commit --message \"{message}\"")
    cmd_out += cmd(f"git push origin {branch}")

    return cmd_out


def main() -> str:
    """
    Controls flow of program asking for user input and calling commands as necessary

    :returns: cumulative output from commands
    """

    cmd_out = ""
    valid_cmds_map = {"push": git_push, "pull": git_pull}
    default_cmd = "push"

    if not exists(".git"):
        print("Repo not initialised, running git init")

        cmd_out += cmd("git init")

        url = ""
        while True:
            url = input("URL of the remote: ").strip()

            if url.startswith("https://"):
                break
            else:
                print("Enter a URL starting with https://")

        cmd_out += cmd(f"git remote add origin {url}")

    user_cmd = ""
    while True:
        user_cmd = input(f"Command [{'|'.join(valid_cmds_map)}], default {default_cmd}: ").strip().lower() or default_cmd

        if user_cmd in valid_cmds_map:
            break
        else:
            print("Enter a valid command")

    cmd_out += valid_cmds_map[user_cmd]()

    return cmd_out


if __name__ == "__main__":
    try:
        main()
        print(f"Finished")
    except Exception as e:
        print(f"Failed with error:\n{e}")
    finally:
        input("Press <Enter> to exit")

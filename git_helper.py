from glob import glob
from os import getcwd
from os.path import basename
from subprocess import PIPE, run


def cmd(text: str) -> str:
    extracted_tokens = []
    for i, text in enumerate(text.split("\"")):
        if i % 2 == 0:
            extracted_tokens.extend(text.split())
        else:
            extracted_tokens.append(f"\"{text}\"")

    called = run(extracted_tokens, stdout=PIPE, stderr=PIPE)

    if called.returncode == 0:
        return called.stdout
    else:
        raise RuntimeError(f"Running \"{cmd}\" failed, stderr:\n{called.stderr}")


def exists(file_path: str) -> bool:
    return len(glob(file_path)) == 1


def git_pull():
    cmd("git pull")


def git_push():
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

    cmd("git add --all")
    cmd(f"git commit --message \"{message}\"")
    cmd(f"git push origin {branch}")


def main():
    valid_operations_map = {"push": git_push, "pull": git_pull}
    default_operation = "push"

    if not exists(".git"):
        print("Repo not initialised, running git init")

        cmd("git init")

        url = ""
        while True:
            url = input("URL of the remote: ").strip()

            if url.startswith("https://"):
                break
            else:
                print("Enter a URL starting with https://")

        cmd(f"git remote add origin {url}")

    operation = ""
    while True:
        operation = input(f"Operation [{'|'.join(valid_operations_map)}], default {default_operation}: ").strip().lower() or default_operation

        if operation in valid_operations_map:
            break
        else:
            print("Enter a valid operation")

    valid_operations_map[operation]()


if __name__ == "__main__":
    try:
        main()
        print(f"Finished")
    except Exception as e:
        print(f"Failed with error:\n{e}")
    finally:
        input("Press <Enter> to exit")

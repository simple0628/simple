import subprocess, getpass

token = getpass.getpass("请粘贴你的 PyPI API Token: ")
subprocess.run([
    "python", "-m", "twine", "upload", "dist/*",
    "-u", "__token__", "-p", token
], shell=True, cwd="E:/shenmo/simple-code")

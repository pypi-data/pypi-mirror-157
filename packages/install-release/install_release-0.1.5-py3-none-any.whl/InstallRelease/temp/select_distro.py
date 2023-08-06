import platform

print(
    platform.platform(),
    "\n",
    platform.machine(),
    "\n",
    platform.architecture(),
    "\n",
    platform.node(),
    "\n",
    platform.freedesktop_os_release(),  # not in 3.7
    "\n",
    platform.release(),
    "\n",
    platform.system(),
)

file_names = []
with open("./names.txt", "r") as names:
    line = names.readline()
    while line:
        if line.isascii():
            file_names.append(line.strip())
        line = names.readline()

print(file_names)

aliases = {"x86_64": ["x86", "amd"], "aarch64": ["arm64"]}

import sys

sys.path.append("../")
from cli_interact import get, listInstalled


# url = 'https://github.com/mufeedvh/moonwalk/' > exception

x = [
    "https://github.com/Canop/broot",
    # "https://github.com/tomnomnom/gron",
    # "https://github.com/terraform-docs/terraform-docs",
    "https://github.com/iann0036/iamlive",
    # "https://github.com/awslabs/fargatecli",
    # "https://github.com/projectdiscovery/nuclei",
    # "https://github.com/asciimoo/wuzz",
    # "https://github.com/loft-sh/devspace",
]

# print({'at':at, 'content': os.listdir(at) })


# for i in x:
#     get(i)

listInstalled()
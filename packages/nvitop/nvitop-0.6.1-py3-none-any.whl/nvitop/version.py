# This file is part of nvitop, the interactive NVIDIA-GPU process viewer.
# License: GNU GPL version 3.

"""An interactive NVIDIA-GPU process viewer, the one-stop solution for GPU process management."""

__version__ = '0.6.1'
__license__ = 'GPLv3'
__author__ = __maintainer__ = 'Xuehai Pan'
__email__ = 'XuehaiPan@pku.edu.cn'
__release__ = True

if not __release__:
    import os
    import subprocess

    try:
        __version__ = subprocess.check_output(
            ['git', 'describe', '--abbrev=7'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        ).strip().lstrip('v').replace('-', '+', 1).replace('-', '.')
    except (OSError, subprocess.CalledProcessError):
        pass

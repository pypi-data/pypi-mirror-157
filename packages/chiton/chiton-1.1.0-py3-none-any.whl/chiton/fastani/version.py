import subprocess

from chiton.fastani.config import FastAniVersion
from chiton.fastani.exceptions import FastANIVersionUnknown


def get_fastani_version(exe: str) -> FastAniVersion:
    """Determines the version of FastANI based on the executable help text.

    Args:
        exe: The path to the FastANI executable.

    Returns:
        The version of FastANI.
    """

    proc = subprocess.Popen([exe, '--version'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, encoding='utf-8')
    stdout, stderr = proc.communicate()

    # Not supported, perhaps it's an older version
    if proc.returncode != 0:
        proc = subprocess.Popen([exe, '--help'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, encoding='utf-8')
        stdout, stderr = proc.communicate()
        if proc.returncode != 0 and 'fastANI is a fast alignment-free' not in stderr:
            raise FastANIVersionUnknown('Could not determine FastANI version')
        if '--matrix' in stderr:
            return FastAniVersion.v1_1_or_1_2
        else:
            return FastAniVersion.v1_0
    else:
        return FastAniVersion(stderr.strip().split()[-1])

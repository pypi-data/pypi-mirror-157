import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post189"
version_tuple = (0, 4, 0, 189)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post189")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post47"
data_version_tuple = (0, 4, 0, 47)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post47")
except ImportError:
    pass
data_git_hash = "47d4a57b9e27363ff152c364324bdbbf91a06367"
data_git_describe = "0.4.0-47-g47d4a57b"
data_git_msg = """\
commit 47d4a57b9e27363ff152c364324bdbbf91a06367
Merge: f9cab8b9 9f803823
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Fri Jul 1 10:03:42 2022 +0200

    Merge pull request #605 from silabs-oysteink/silabs-oysteink_first_op
    
    Added a 'first_op' to track the first operation of multi operation in…

"""

# Tool version info
tool_version_str = "0.0.post142"
tool_version_tuple = (0, 0, 142)
try:
    from packaging.version import Version as V
    ptool_version = V("0.0.post142")
except ImportError:
    pass


def data_file(f):
    """Get absolute path for file inside pythondata_cpu_cv32e40x."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_cv32e40x".format(f))
    return fn

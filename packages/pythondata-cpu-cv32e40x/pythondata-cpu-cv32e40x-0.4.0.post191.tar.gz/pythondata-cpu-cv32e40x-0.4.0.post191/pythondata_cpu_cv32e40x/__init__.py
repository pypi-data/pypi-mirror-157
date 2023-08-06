import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.4.0.post191"
version_tuple = (0, 4, 0, 191)
try:
    from packaging.version import Version as V
    pversion = V("0.4.0.post191")
except ImportError:
    pass

# Data version info
data_version_str = "0.4.0.post49"
data_version_tuple = (0, 4, 0, 49)
try:
    from packaging.version import Version as V
    pdata_version = V("0.4.0.post49")
except ImportError:
    pass
data_git_hash = "faa52330cf49ed313f2237199cfec1f69f05ad36"
data_git_describe = "0.4.0-49-gfaa52330"
data_git_msg = """\
commit faa52330cf49ed313f2237199cfec1f69f05ad36
Merge: 47d4a57b 3de84645
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Fri Jul 1 15:08:05 2022 +0200

    Merge pull request #606 from silabs-oysteink/silabs-oysteink_allowed-refactor
    
    Refactored interrupt_allowed and halt_id logic.

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

__version__ = '0.13.0'
git_version = '1a4afa93ca0b22193b0cc3caad84e53617a2ab49'
from torchvision.extension import _check_cuda_version
if _check_cuda_version() > 0:
    cuda = _check_cuda_version()

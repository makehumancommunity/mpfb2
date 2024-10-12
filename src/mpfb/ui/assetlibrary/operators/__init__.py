"""Operators for asset library"""

from ....services import LogService
_LOG = LogService.get_logger("assetlibrary.operators.init")
_LOG.trace("initializing asset library operators")

from .unloadlibraryclothes import MPFB_OT_Unload_Library_Clothes_Operator
from .loadlibraryclothes import MPFB_OT_Load_Library_Clothes_Operator
from .loadlibraryproxy import MPFB_OT_Load_Library_Proxy_Operator
from .loadlibraryskin import MPFB_OT_Load_Library_Skin_Operator
from .loadlibrarymaterial import MPFB_OT_Load_Library_Material_Operator
from .loadlibrarypose import MPFB_OT_Load_Library_Pose_Operator
from .loadlibraryink import MPFB_OT_Load_Library_Ink_Operator
from .loadpack import MPFB_OT_Load_Pack_Operator
from ...assetlibrary.operators.installtarget import MPFB_OT_Install_Target_Operator

__all__ = [
    "MPFB_OT_Load_Library_Clothes_Operator",
    "MPFB_OT_Unload_Library_Clothes_Operator",
    "MPFB_OT_Load_Library_Proxy_Operator",
    "MPFB_OT_Load_Library_Skin_Operator",
    "MPFB_OT_Load_Library_Pose_Operator",
    "MPFB_OT_Load_Library_Ink_Operator",
    "MPFB_OT_Load_Library_Material_Operator",
    "MPFB_OT_Load_Pack_Operator",
    "MPFB_OT_Install_Target_Operator"
    ]

"""For mapping CMU mocap (cgspeed conversion) to default rig"""

from .bonemap import BoneMap

MAP = []
MAP.append( BoneMap("hip",      "root"          , translation=True) )
MAP.append( BoneMap("lThigh",   "upperleg02.L"  ) )
MAP.append( BoneMap("rThigh",   "upperleg02.R"  ) )
MAP.append( BoneMap("lShin",    "lowerleg01.L"  ) )
MAP.append( BoneMap("rShin",    "lowerleg01.R"  ) )
MAP.append( BoneMap("lFoot",    "foot.L"        ) )
MAP.append( BoneMap("rFoot",    "foot.R"        ) )
MAP.append( BoneMap("abdomen",  "spine03"       ) )
MAP.append( BoneMap("chest",    "spine02"       ) )
MAP.append( BoneMap("lCollar",  "clavicle.L"    ) )
MAP.append( BoneMap("rCollar",  "clavicle.R"    ) )
MAP.append( BoneMap("lShldr",   "upperarm01.L"  ) )
MAP.append( BoneMap("rShldr",   "upperarm01.R"  ) )

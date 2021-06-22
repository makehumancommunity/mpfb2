# Using MPFB as a code library

A design goal is that MPFB should be possible to import and use in your own python scripts and addons. 
To this end, there are public interfaces, which you should be able to import and use.

(this page obviously need to be significantly extended at some point...)

## Setting a target

You can set a target value using the TargetService. In the following code example, you can see how 
this is done both in the case the target has been previously loaded and in the case it needs to 
be loaded from disc.

```
import bpy, os

# Most of the functionality that can be used from outside is located in 
# the services dir, see https://github.com/makehumancommunity/mpfb2/tree/master/src/mpfb/services
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService

_TARGETS_DIR = LocationService.get_mpfb_data("targets")

# The base mesh
blender_object = bpy.context.active_object

# One sided targets 0..1, two sided targets -1..1
value = 0.8

# Target category, i.e the same as the name of the panel (actually the name of
# folder where the target is located
category = "head"

# Target file name minus .target.gz, see 
# https://github.com/makehumancommunity/mpfb2/tree/master/src/mpfb/data/targets
name = "head-square"

if not TargetService.has_target(blender_object, name):
    # Calculate the full path to the target file
    target_path = os.path.join(_TARGETS_DIR, category, name + ".target.gz")
    TargetService.load_target(blender_object, target_path, weight=value, name=name)
else:
    TargetService.set_target_value(blender_object, name, value, delete_target_on_zero=True)
```

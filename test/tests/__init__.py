"""
This is the root module for the unit test hierarchy. This module provides important code structures which are vital in order to run the unit tests.

As a background, the Blender 4.2 extension format requires all imports to be relative. In the now deprecated legacy addon format,
an absolute import could be done from anywhere. For example you could run this python code from anywhere:

    from mpfb.entities.material.mhmaterial import MhMaterial
    material = MhMaterial()

In the new extension format, this is no longer possible. Unfortunately, this means that the unit test modules have no knowledge of the
package structure. It will be different on different machines, as the first few parts of the module name will be constructed from
the "repository" the extension is installed in. This makes it impossible to do a direct import like the one above.

Instead, there are some utilities provided below:

dynamic_import(absolute_package_str, key): This function will search through all loaded modules to find a one with a name that ends
with the given package string. It will then check if that module exposes something with the given key. If so, it will return that object.
So, in order to do the same thing as above, you would do:

    MhMaterial = dynamic_import("mpfb.entities.material.mhmaterial", "MhMaterial")
    material = MhMaterial()

MPFB_CONTEXTUAL_INFORMATION: This is a dictionary containing all the services and other useful information, such as the full absolute
package name of MPFB and the location of MPFB's __init__.py file. For example:

    print("MPFB's full package name is: " + MPFB_CONTEXTUAL_INFORMATION["__package__"])
    print("MPFB's __init__.py file is located at: " + MPFB_CONTEXTUAL_INFORMATION["__file__"])

Finally, for convenience, all service classes are exposed directly through this module. A unit test further down in the hierachy can thus
do simplified relative import to get access to it. For example:

    from .. import ObjectService
    basemesh = ObjectService.load_base_mesh()
    assert basemesh is not None, "Failed to load base mesh"

Regarding the test suite, it is organized into four sub modules. Since pytest discovers the modules in alphabetical order, they have been
given prefixes so that the core logic is tested first. The modules containing the actual unit tests are:

- aaa_context_test.py: Check that tests can be performed at all, and that for example MPFB_CONTEXTUAL_INFORMATION is available.
- bbb_services: Tests for the core logic services (ie the code files under src/mpfb/services).
- ccc_entities: Tests for the entities (ie the code files under src/mpfb/entities).
- ddd_data: Test for checking that the data dir and its files look as expected.
- eee_ui: Thests for UI panels and UI operators (ie the code files under src/mpfb/ui).
"""

import importlib, sys


def dynamic_import(absolute_package_str, key):
    for amod in sys.modules:
        if amod.endswith(absolute_package_str):
            mpfb_mod = importlib.import_module(amod)

            if not hasattr(mpfb_mod, key):
                raise AttributeError(f"Module {amod} does not have attribute {key}")

            return getattr(mpfb_mod, key)


MPFB_CONTEXTUAL_INFORMATION = dynamic_import("mpfb", "MPFB_CONTEXTUAL_INFORMATION")

# The following are thus the same classes as would be found in the files in the src/mpfb/services directory.
AnimationService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["AnimationService"]
AssetService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["AssetService"]
ClothesService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["ClothesService"]
HumanService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["HumanService"]
LocationService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["LocationService"]
LogService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["LogService"]
MaterialService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["MaterialService"]
MeshService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["MeshService"]
ModifierService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["ModifierService"]
NodeService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["NodeService"]
NodeTreeService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["NodeTreeService"]
ObjectService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["ObjectService"]
RigService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["RigService"]
SocketService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["SocketService"]
SystemService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["SystemService"]
TargetService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["TargetService"]
UiService = MPFB_CONTEXTUAL_INFORMATION["SERVICES"]["UiService"]


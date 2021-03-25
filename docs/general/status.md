# Current status

This page describes the current status of the addon. As MPFB is evolving in a rapid pace, the information might be 
dated. If you discover something which is inaccurate, please report this.

Overall current status: **pre alpha / not intended for regular use**

This said, we use it ourselves on a daily basis and it mostly works.

## Remaining to port from MPFB 1

While the goal is that MPFB 2 should be at least as competent as MPFB 1, there are still features/functionality
which has yet to be ported to the new codebase. 

- Everything related to mocap / kinect
- Rig amputations
- Post import synchronization
- Expression transfer

## Incomplete / partially implemented

The following are features in development, but which remain to be finished

**General:**

- The documentation is incomplete
- Large parts of the code lack code comments
- Preferences: It should be possible to configure host/port for the socket calls
- Preferences: It should be possible to configure where MPFB user files should be stored

**MakeSkin:**

- node visualization has not been ported yet
- saving materials as blend files are not implemented
- the documentation has not been ported

**Rig/skeleton/posing:**

- There is no way to save/load presets for rig helpers
- Preserving FK pose when adding helper bones is occasionally glitchy
- Preserving IK/helper pose when switching back to FK is not implemented at all
- Rig helpers only implemented for "Default" and "Default no toes" rigs
- Rigify: No colors / bone layer separation for rigify bones
- Rigify: Ways to control the process (for example checkboxes for deciding if the meta rig should be kept, or if the final generate rig step should be done) 

## Not started

The following are large areas of development which are intended to be finished before a stable release of MPFB2,
but which has not been started yet.

- Merge/port MakeClothes 2 into the codebase

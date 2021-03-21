# Change log

Since MPFB 2 has not been released yet, there is no formal change log. However, these are the major new features since MPFB 1:

- Import from MakeHuman about three times faster
- Support for rigify
- Rig helpers with more versatile IK
- Procedural eyes
- Ability to save importer presets
- Ability to save character presets for skins
- Ability to save character presets for eyes
- MakeSkin merged into MPFB2 (with roughly the same functionality as the standalone MakeSkin plugin)
- MakeTarget merged into MPFB2 (with roughly the same functionality as the standalone MakeTarget plugin)

Under the hood there are many changes that might not be immediately visible to users:

- Complete rewrite with more coherent code structure
- Coherent logging with separation of log channels and log levels
- Materials are JSON based
- Properties are JSON based
- Functionality divided into reusable services (which can be utilized from outside MPFB2)

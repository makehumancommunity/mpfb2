LICENSE
=======

Table of contents
-----------------
A. The overall license setup for MPFB
B. The license for the source code as such
C. The license for the bundled assets
D. Concerning the output from MPFB


A. The overall license setup for MPFB
------------------------------------------

MPFB uses the same license setup as MakeHuman, but with GPLv3 as source code license
rather than AGPL (in order to put it more in line with Blender's source code license).

The MPFB addon consists of two separate parts:

* Source code: the program logic that powers the application. 
* Assets: The graphical data that the application operates on

B. The license for the source code as such
------------------------------------------

The MPFB source code is defined as files that contain program logic.
This includes python files, shell scripts and configuration files.

The MPFB source (as defined per the above) is released under GPLv3.

Copyright (C) 2001-2021  MakeHuman Team (www.makehumancommunity.org)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.
   
For the full text of the source code license, see 
[LICENSE.CODE.md](LICENSE.CODE.md)

C. The license for the bundled assets
-------------------------------------

The assets are defined as any data contributing to the output from MPFB.
This includes:

* The base mesh and proxies
* Targets and modifiers
* Textures
* Clothes (any MHCLO-based asset)
* Rigs, poses and expressions
* JSON data with mesh information

These assets have been released under CC0 1.0 Universal. In summary this means
that to the fullest extent possible, it is the intention of the MakeHuman 
team that anyone can do whatever they want with it.

For the full text of the legal statement regarding the assets, see
[LICENSE.ASSETS.md](LICENSE.ASSETS.md)

D. Concerning the output from MPFB
----------------------------------

It is the opinion of the MakeHuman team that no output from MPFB
contains any trace of program logic. That is, regardless of whether you use
the UI as such or if you call functions of MPFB via a script (such as 
an addon that extends MPFB), what you get is a combination of assets and your
own creative input. As the assets have been released under CC0, there is no
limitation on what you can do with this combined output.

To make it clear, the MakeHuman team makes no claim whatsoever over output
such as:

* Exports to files (FBX, OBJ, DAE, MHX2...)
* Graphical data generated via scripting or plugins
* Renderings
* Screenshots
* Saved model files

We regard these things as your data, which is yours to handle as you see
fit.

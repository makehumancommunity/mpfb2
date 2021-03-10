# name

* __Data type:__ string
* __What is it for:__ Marking a readable name inside the MHMAT file
* __Use when:__ You think someone will read the source of the MHMAT file
* __Implemented in MakeSkin:__ yes (as an input field in the main panel)
* __Makes visible difference in blender:__ when exported with MHX2 it is part of the material name in Blender
* __Makes visible difference in makehuman:__ only in Material Editor

The "name" key is a simple string for inserting a human readable name in the source of the MHMAT file. It is used for
information purposes, and it is used for export with MHX2 where it is appended to the asset-name. In MakeHuman, the file lists are constructing using the file name
of the mhmat file, rather than the "name" tag inside the files.

## Example

    name MyCoolMaterial 



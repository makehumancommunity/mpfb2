# viewPortColor

* __Data type:__ RGB floats 
* __What is it for:__ Controlling how the object appears in the blender viewport 
* __Use when:__ You want a particular color in the viewport solid mode
* __Implemented in MakeSkin:__ yes (it is read from the material viewport settings)
* __Makes visible difference in blender:__ yes (in the "solid" viewport mode)
* __Makes visible difference in makehuman:__ no

By changing viewPortColor, you can change the color with which objects with this material
are drawn in the solid mode in the blender viewport. 

## Example

Draw the object as light blue in the viewport:

    viewPortColor 0.8 0.8 1.0

## In MakeSkin

The viewPortColor value is read from the color setting under "viewport display" in
the material settings:

![color](viewPortColor.png)


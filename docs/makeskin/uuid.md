# uuid

* __Data type:__ UUID
* __What is it for:__ Telling two materials with the same name apart
* __Use when:__ You think there might be confusion amongst materials for the same asset
* __Implemented in MakeSkin:__ no
* __Makes visible difference in blender:__ no
* __Makes visible difference in makehuman:__ no (but this is a bug. It will probably be used in the future)

The "uuid" key is a unique identifier for the material. It is (intended to be) used for telling materials apart.
At the moment this does not work in MakeHuman.

## Example

    uuid a8b0e841-144b-4f03-8b9e-ea8fdce8c863 



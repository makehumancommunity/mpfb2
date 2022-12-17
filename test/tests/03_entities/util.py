import bpy, os, random, string

def random_name():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(15))

def delete_object_by_name(name): 
    object_to_delete = bpy.data.objects[name]
    bpy.data.objects.remove(object_to_delete, do_unlink=True)

def delete_object(object_to_delete):     
    bpy.data.objects.remove(object_to_delete, do_unlink=True)


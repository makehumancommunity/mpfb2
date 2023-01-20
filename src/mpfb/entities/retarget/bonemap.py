"""A mapping for a specific bone"""

class BoneMap:
    
    translation = False
    
    mocap_bone_name = None
    mocap_rotation_space = 'LOCAL'
    mocap_location_space = 'WORLD'
    
    target_bone_name = None
    target_rotation_space = 'LOCAL'
    target_location_space = 'WORLD'
        
    def __init__(self, mocap_bone_name, target_bone_name, *args, **kwargs):
        
        self.mocap_bone_name = mocap_bone_name
        self.target_bone_name = target_bone_name
        
        for key, value in kwargs.items():
            setattr(self, key, value)
        
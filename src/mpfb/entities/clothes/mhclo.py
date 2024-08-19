"""This module provides and information holder for MHCLO files."""

import bpy, os, sys, json
from mathutils import Vector
from ...services import ObjectService
from ...services import LogService
from ...services import LocationService

_LOG = LogService.get_logger("entities.mhclo")

_CONFIG_FILE = None

class Mhclo:
    """A representation of the values of a MHCLO file."""

    def __init__(self):
        """Create an empty MHCLO object with default values."""
        self.obj_file = None
        self.x_scale = None
        self.y_scale = None
        self.z_scale = None
        self.author = "unknown"
        self.license = "CC0"
        self.name = "imported_cloth"
        self.description = "no description"
        self.basename = None  # Filename minus extension
        self.weights_file = None
        self.material = None
        self.tags = ""
        self.zdepth = 50
        self.first = 0
        self.verts = {}
        self.delverts = []
        self.delete = False
        self.delete_group = "Delete"
        self.uuid = None
        self.max_pole = None

    def load(self, mhclo_filename, *, only_metadata=False):
        """Populate settings from contents of a MHCLO file. This will not automatically load the
        mesh or the materials."""

        if not mhclo_filename:
            raise ValueError('Cannot load empty file name')

        if not os.path.exists(mhclo_filename):
            raise IOError(mhclo_filename + " does not exist")

        _LOG.debug("Will try to parse file", mhclo_filename)

        #realpath = os.path.realpath(os.path.expanduser(mhclo_filename))
        realpath = os.path.realpath(mhclo_filename)
        folder = os.path.dirname(realpath)

        self.basename = os.path.splitext(realpath)[0]

        try:
            fp = open(mhclo_filename, "r", encoding="utf8", errors="surrogateescape")
        except:
            _LOG.error("Error trying to open file:", sys.exc_info()[0])
            return None

        vn = 0
        status = ""

        for line in fp:
            words= line.split()
            _LOG.debug("Line", words)

            l = len(words)

            if l == 0:
                status = ""
                continue

            # at least grab what you get from the comment
            #
            if words[0] == '#':
                if l > 2:
                    key = words[1].lower()
                    if "author" in key:
                        self.author = words[2]
                    elif "license" in key:
                        if "by" in line.lower():
                            self.license = "CC-BY"
                        elif "apgl" in line.lower():
                            self.license = "AGPL"
                    elif "description" in key:
                        self.description = " ".join(words[2:])
                continue

            if words[0] == "material":
                self.material = os.path.join(folder, words[1])
                continue

            if str(words[0]).startswith("vertexboneweights"):
                self.weights_file = os.path.join(folder, words[1])
                continue

            if status and only_metadata:
                continue

            # read vertices lines
            #
            if status == 'v':
                if words[0].isnumeric() is False:
                    _LOG.debug("Breaking vertex listing loop on", words)
                    status = ""
                    continue
                if l == 1:
                    v = int(words[0])
                    self.verts[vn] = {'verts': (v,v,v), 'weights': (1,0,0), 'offsets': Vector((0,0,0))}
                else:
                    v0 = int(words[0])
                    v1 = int(words[1])
                    v2 = int(words[2])
                    w0 = float(words[3])
                    w1 = float(words[4])
                    w2 = float(words[5])
                    d0 = float(words[6])
                    d1 = float(words[7])
                    d2 = float(words[8])
                    self.verts[vn] = {'verts': (v0,v1,v2), 'weights': (w0,w1,w2), 'offsets': Vector((d0,-d2,d1))}
                vn += 1
                continue
            elif status == 'd':
                if words[0].isnumeric() is False:
                    status = ""
                    continue
                sequence = False
                for v in words:
                    if v == "-":
                        sequence = True
                    else:
                        v1 = int(v)
                        if sequence:
                            for vn in range(v0,v1+1):
                                self.delverts.append(vn)
                            sequence = False
                        else:
                            self.delverts.append(v1)
                        v0 = v1
                continue

            key = words[0]
            status = ""
            if key == 'obj_file':
                self.obj_file = os.path.join(folder, words[1])
                _LOG.debug("obj_file", self.obj_file)
            elif key == 'verts':
                if len(words) > 1:
                    self.first = int(words[1])      # this value will be ignored, we always start from zero
                    status = "v"
            elif key == 'x_scale':
                self.x_scale = (int(words[1]), int(words[2]), float(words[3]))
            elif key == 'y_scale':
                self.y_scale = (int(words[1]), int(words[2]), float(words[3]))
            elif key == 'z_scale':
                self.z_scale = (int(words[1]), int(words[2]), float(words[3]))
            elif key == 'name':
                self.name = words[1]
            elif key == 'z_depth':
                self.zdepth = int(words[1])
            elif key == 'uuid':
                self.uuid = words[1]
            elif key == 'tag':
                if self.tags != "":
                    self.tags += ","
                self.tags += words[1].lower()
            elif key == 'delete_verts':
                self.delete = True
                status = 'd'

        if not self.obj_file:
            _LOG.warn("Reaching end of mhclo parsing without finding obj file")

        fp.close()

    def load_mesh(self, context):

        if self.obj_file == "" or not self.obj_file:
            raise ValueError('No obj file has been specified')

        _LOG.debug("Will try to load wavefront file", self.obj_file)
        obj = ObjectService.load_wavefront_file(self.obj_file, context)
        _LOG.debug("Loaded object:", obj)
        if obj is not None:
            self.clothes = obj
        else:
            raise IOError("Failed to load clothes mesh")
        return obj

    def get_weights_filename(self, suffix=None):
        base = self.basename
        ext = ".mhw"

        return base + ("." + suffix if suffix else "") + ext

    def _get_config_file(self):
        global _CONFIG_FILE
        if _CONFIG_FILE is None:
            metadata = LocationService.get_mpfb_data("mesh_metadata")
            config_file = os.path.join(metadata, "hm08_config.json")
            with open(config_file, 'r') as json_file:
                _CONFIG_FILE = json.load(json_file)
        return _CONFIG_FILE

    def set_scalings (self, context, human):
        mesh_config = self._get_config_file()
        for bodypart in mesh_config["dimensions"]:
            dims = mesh_config["dimensions"][bodypart]
            #
            # I think it is okay to check only one dimension to figure out on
            # what the piece of cloth was created
            #
            if self.x_scale and dims['xmin'] == self.x_scale[0] and dims['xmax'] == self.x_scale[1]:
                pass
                # TODO: Need to update with new names for makeclothes properties
                #context.active_object.MhOffsetScale = bodypart
        return

    def write_mhclo(self, filename, also_export_mhmat=False, also_export_obj=True, reference_scale=None):
        if filename is None:
            raise ValueError('No file name has been specified')

        if (also_export_mhmat or also_export_obj) and not self.clothes:
            raise ValueError("No clothes mesh has been set")

        bn = os.path.basename(filename)
        dn = os.path.dirname(filename)
        mhmat_filename = os.path.join(dn, bn.replace(".mhclo", ".mhmat"))
        obj_filename = os.path.join(dn, bn.replace(".mhclo", ".obj"))

        if also_export_mhmat:
            _LOG.debug("Will export MHMAT to", mhmat_filename)

        if also_export_obj:
            _LOG.debug("Will export OBJ to", obj_filename)
            ObjectService.save_wavefront_file(obj_filename, self.clothes)

        _LOG.debug("Writing MHCLO file", filename)
        with open(filename, "w", encoding="utf8") as mhclo_file:
            mhclo_file.write("# MHCLO asset for MakeHuman and MPFB, created using MPFB2\n#\n")

            if self.author:
                mhclo_file.write("# author: {}\n".format(self.author))

            if self.license:
                mhclo_file.write("# license: {}\n".format(self.license))

            if self.description:
                mhclo_file.write("# description: {}\n".format(self.description))

            mhclo_file.write("basemesh hm08\n\n")

            mhclo_file.write("# Basic info:\n")
            if self.name:
                mhclo_file.write("name {}\n".format(self.name))

            if self.uuid:
                mhclo_file.write("uuid {}\n".format(self.uuid))

            if also_export_obj:
                mhclo_file.write("obj_file {}\n".format(os.path.basename(obj_filename)))

            if also_export_mhmat:
                mhclo_file.write("material {}\n".format(os.path.basename(mhmat_filename)))

            if reference_scale:
                mhclo_file.write("\n# Scale references:\n")
                mhclo_file.write("x_scale {} {} {:.4f}\n".format(reference_scale["xmin"], reference_scale["xmax"], reference_scale["x_scale"]))
                # Y and Z are flipped in MakeHuman
                mhclo_file.write("y_scale {} {} {:.4f}\n".format(reference_scale["zmin"], reference_scale["zmax"], reference_scale["z_scale"]))
                mhclo_file.write("z_scale {} {} {:.4f}\n".format(reference_scale["ymin"], reference_scale["ymax"], reference_scale["y_scale"]))
            else:
                _LOG.warn("No scalings provided")

            if self.max_pole:
                mhclo_file.write("\nmax_pole {}\n".format(self.max_pole))

            if self.zdepth:
                mhclo_file.write("\nz_depth {}\n".format(self.zdepth))

            mhclo_file.write("\n# The following are matches between clothes vertices and body vertices:\nverts 0\n")

            for vert_no in self.verts.keys():
                vdef = self.verts[vert_no]
                verts = vdef['verts']
                weights = vdef['weights']
                offsets = vdef['offsets']

                if weights[0] == 1 and weights[1] == 0 and weights[2] == 0:
                    # This is an exact match
                    mhclo_file.write("{}\n".format(verts[0]))
                else:
                    # This is an offset match
                    mhclo_file.write("{} {} {} ".format(verts[0], verts[1], verts[2]))
                    mhclo_file.write("{:.4f} {:.4f} {:.4f} ".format(weights[0], weights[1], weights[2]))
                    mhclo_file.write("{:.4f} {:.4f} {:.4f}\n".format(offsets[0], offsets[1], offsets[2]))

            mhclo_file.write("\n")
            if self.delverts and len(self.delverts) > 0:
                _LOG.debug("delverts", self.delverts)
                mhclo_file.write("# The following are the vertices on the base mesh which should be hidden:\ndelete_verts\n")

                current_range = None
                for index in self.delverts:

                    if index == 4396:
                        _LOG.debug("\n\n XXXXXXXXXXXXXXX \n\n")
                    if not current_range:
                        _LOG.debug("START: Index, range", (index, current_range))
                        current_range = [index, index]
                    else:
                        last_end = current_range[1]
                        if index == current_range[1] + 1:
                            _LOG.debug("EXTENDING", (index, current_range))
                            current_range[1] = index
                        else:
                            _LOG.debug("BREAKING", (index, current_range))
                            mhclo_file.write(" {} - {}".format(current_range[0], current_range[1]))
                            current_range = [index, index]
                mhclo_file.write(" {} - {}".format(current_range[0], current_range[1]))
            else:
                mhclo_file.write("# No delete_verts have been specified\n")






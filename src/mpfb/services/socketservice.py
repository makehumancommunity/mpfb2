#!/usr/bin/python
# -*- coding: utf-8 -*-

from .logservice import LogService
from .jsoncall import JsonCall
import asyncio

_LOG = LogService.get_logger("services.socketservice")

class _SocketService():

    def __init__(self):
        _LOG.debug("Constructing socket service")
        # TODO: read these from config somehow
        self._host = "127.0.0.1"
        self._port = 12345
        self._call_cache = dict()

    def _value_from_cache(self, function_name):
        _LOG.enter()
        if function_name in self._call_cache:
            _LOG.trace("Key existed in call cache:", function_name)
            return self._call_cache[function_name]
        _LOG.trace("Key did not exist in call cache:", function_name)
        return None

    def set_host(self, host):
        _LOG.enter()
        self._host = host

    def set_port(self, port):
        _LOG.enter()
        self._port = port

    async def _call_for_json(self, call):
        _LOG.enter()
        _LOG.reset_timer()
        reader, writer = await asyncio.open_connection(self._host, self._port)

        _LOG.debug("About to send call for", call.function)
        serialized_data = call.serialize()
        _LOG.dump("Serialized data", serialized_data)
        data_to_send = serialized_data.encode()
        writer.write(data_to_send)
        await writer.drain()

        data_returned = await reader.read(-1)  # -1 = until EOF
        decoded_data = data_returned.decode()
        _LOG.dump("Decoded returned data", decoded_data)
        writer.close()
        await writer.wait_closed()

        call.populate_from_json(decoded_data)
        _LOG.time("Milliseconds it took to perform the call and deserialize data:")

    async def _call_for_binary(self, call):
        _LOG.enter()
        _LOG.reset_timer()
        reader, writer = await asyncio.open_connection(self._host, self._port)

        _LOG.debug("About to send call for", call.function)
        serialized_data = call.serialize()
        _LOG.dump("Serialized data", serialized_data)
        data_to_send = serialized_data.encode()
        writer.write(data_to_send)
        await writer.drain()

        data_returned = await reader.read(-1)  # -1 = until EOF
        decoded_data = bytearray(data_returned)
        _LOG.debug("Length of returned data", len(decoded_data))
        _LOG.dump("Decoded returned data", decoded_data)
        writer.close()
        await writer.wait_closed()
        call.data = decoded_data
        _LOG.time("Milliseconds it took to perform the call and deserialize data:")

    def get_user_dir(self):
        _LOG.enter()
        cached_value = self._value_from_cache("getUserDir")
        if not cached_value is None:
            return cached_value
        call = JsonCall("getUserDir")
        asyncio.run(self._call_for_json(call))
        self._call_cache["getUserDir"] = call.data
        return call.data

    def get_sys_dir(self):
        _LOG.enter()
        cached_value = self._value_from_cache("getSysDir")
        if not cached_value is None:
            return cached_value
        call = JsonCall("getSysDir")
        asyncio.run(self._call_for_json(call))
        self._call_cache["getSysDir"] = call.data
        return call.data

    def get_body_mesh_info(self):
        _LOG.enter()
        call = JsonCall("getBodyMeshInfo")
        asyncio.run(self._call_for_json(call))
        return call.data

    def get_body_vertices(self):
        _LOG.enter()
        call = JsonCall("getBodyVerticesBinary")
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_body_faces(self):
        _LOG.enter()
        call = JsonCall("getBodyFacesBinary")
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_body_texture_coords(self):
        _LOG.enter()
        call = JsonCall("getBodyTextureCoordsBinary")
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_body_uv_mapping(self):
        _LOG.enter()
        call = JsonCall("getBodyFaceUVMappingsBinary")
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_body_material_info(self):
        _LOG.enter()
        call = JsonCall("getBodyMaterialInfo")
        asyncio.run(self._call_for_json(call))
        return call.data

    def get_skeleton(self):
        _LOG.enter()
        call = JsonCall("getSkeleton")
        asyncio.run(self._call_for_json(call))
        return call.data

    def get_body_weight_info(self):
        _LOG.enter()
        call = JsonCall("getBodyWeightInfo")
        asyncio.run(self._call_for_json(call))
        return call.data

    def get_body_weight_vertices(self):
        _LOG.enter()
        call = JsonCall("getBodyWeightsVertList")
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_body_weights(self):
        _LOG.enter()
        call = JsonCall("getBodyWeights")
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_proxies_info(self):
        _LOG.enter()
        call = JsonCall("getProxiesInfo")
        asyncio.run(self._call_for_json(call))
        return call.data

    def get_proxy_vertices(self, uuid):
        _LOG.enter()
        call = JsonCall("getProxyVerticesBinary")
        call.params = {"uuid": uuid}
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_proxy_faces(self, uuid):
        _LOG.enter()
        call = JsonCall("getProxyFacesBinary")
        call.params = {"uuid": uuid}
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_proxy_texture_coords(self, uuid):
        _LOG.enter()
        call = JsonCall("getProxyTextureCoordsBinary")
        call.params = {"uuid": uuid}
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_proxy_uv_mapping(self, uuid):
        _LOG.enter()
        call = JsonCall("getProxyFaceUVMappingsBinary")
        call.params = {"uuid": uuid}
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_proxy_weight_info(self, uuid):
        _LOG.enter()
        call = JsonCall("getProxyWeightInfo")
        call.params = {"uuid": uuid}
        asyncio.run(self._call_for_json(call))
        return call.data

    def get_proxy_weight_vertices(self, uuid):
        _LOG.enter()
        call = JsonCall("getProxyWeightsVertList")
        call.params = {"uuid": uuid}
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_proxy_weights(self, uuid):
        _LOG.enter()
        call = JsonCall("getProxyWeights")
        call.params = {"uuid": uuid}
        asyncio.run(self._call_for_binary(call))
        return call.data

    def get_proxy_material_info(self, uuid):
        _LOG.enter()
        call = JsonCall("getProxyMaterialInfo")
        call.params = {"uuid": uuid}
        asyncio.run(self._call_for_json(call))
        return call.data

SocketService = _SocketService() # pylint: disable=C0103

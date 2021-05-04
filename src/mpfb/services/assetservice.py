"""This module contains utility functions scanning asset repositories."""

from mpfb.services.objectservice import ObjectService
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.uiservice import UiService

_LOG = LogService.get_logger("services.assetservice")

class AssetService:

    def __init__(self):
        raise RuntimeError("You should not instance AssetService. Use its static methods instead.")

    @staticmethod
    def find_asset_files_matching_pattern(in_dir, pattern="*.mhclo"):
        return []

    @staticmethod
    def list_mhclo_assets(asset_type="clothes"):
        roots = AssetService.get_asset_roots(asset_type)
        assets = []
        for root in roots:
            assets.extend(AssetService.find_asset_files_matching_pattern(root, "*.mhclo"))
        return assets

    @staticmethod
    def list_mhmat_assets(asset_type="skins"):
        roots = AssetService.get_asset_roots(asset_type)
        assets = []
        for root in roots:
            assets.extend(AssetService.find_asset_files_matching_pattern(root, "*.mhmat"))
        return assets

    @staticmethod
    def get_available_data_roots():
        user_data_root =
        return []

    @staticmethod
    def get_asset_roots(asset_type="clothes"):
        return []

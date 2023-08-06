"""Helpers to easily access data in OSEF frame dict."""
# Standard imports
import numpy as np
from numpy import typing as npt
from typing import List

# Osef imports
from osef import types


class Pose:
    """Class to handle a Pose from OSEF data."""

    def __init__(
        self, rotation: npt.NDArray[np.float32], translation: npt.NDArray[np.float32]
    ):
        """Constructor."""
        self.rotation = rotation
        self.translation = translation

    @property
    def matrix(self) -> npt.NDArray[np.float32]:
        """Get a Matrix 4x4 with the rotation and translation."""
        pose_3x4 = np.hstack(
            (
                self.rotation,
                np.transpose([self.translation]),
            )
        )
        pose_4x4 = np.vstack((pose_3x4, [0, 0, 0, 1]))

        return pose_4x4

    def __eq__(self, other: "Pose") -> bool:
        """Equality operator."""
        return (np.array_equal(self.rotation, other.rotation)) and (
            np.array_equal(self.translation, other.translation)
        )


class ObjectProperties:
    """Class to handle the object properties."""

    def __init__(
        self, oriented: bool, is_seen: bool, has_valid_slam_pose: bool, is_static: bool
    ) -> None:
        """Constructor."""
        self.oriented = oriented
        self.is_seen = is_seen
        self.has_valid_slam_pose = has_valid_slam_pose
        self.is_static = is_static

    def __eq__(self, other: "ObjectProperties") -> bool:
        """Equality operator."""
        return (
            self.oriented == other.oriented
            and self.is_seen == other.is_seen
            and self.has_valid_slam_pose == other.has_valid_slam_pose
            and self.is_static == other.is_static
        )


class ZoneBindings:
    """Class to handle the zone bindings."""

    def __init__(self, zone_index: int, object_id: int):
        """Constructor."""
        self.zone_index = zone_index
        self.object_id = object_id


class ZoneDef:
    """Class to handle zone definition."""

    def __init__(
        self, zone_name: str, zone_vertices: np.void, zone_vertical_limits: np.ndarray
    ):
        """Constructor."""
        self.zone_name = zone_name
        self.zone_vertices = zone_vertices
        self.zone_vertical_limits = zone_vertical_limits


def get_timestamp(osef_frame: dict) -> float:
    """Get timestamp from OSEF frame dict."""
    return osef_frame.get(types.OsefKeys.TIMESTAMPED_DATA.value).get(
        types.OsefKeys.TIMESTAMP_MICROSECOND.value
    )


class OsefFrame:
    """Base class for the OSEF frame helper."""

    def __init__(self, osef_frame: dict):
        """Constructor."""
        self._osef_frame = osef_frame
        self._timestamp = get_timestamp(osef_frame)

    @property
    def timestamp(self) -> float:
        """Timestamp property."""
        return self._timestamp

    @property
    def osef_frame_dict(self) -> dict:
        """Property to get the raw dict OSEF frame."""
        return self._osef_frame


class ScanFrame(OsefFrame):
    """Helper class for Scan frame."""

    def __init__(self, osef_frame: dict):
        """Constructor."""
        super().__init__(osef_frame)

        if types.OsefKeys.SCAN_FRAME.value not in self._osef_frame.get(
            types.OsefKeys.TIMESTAMPED_DATA.value
        ):
            raise ValueError(
                f"{types.OsefKeys.SCAN_FRAME.value} missing in Osef frame."
            )

        self._scan_frame = osef_frame.get(types.OsefKeys.TIMESTAMPED_DATA.value).get(
            types.OsefKeys.SCAN_FRAME.value
        )

    @property
    def pose(self) -> Pose:
        """Get the Lidar pose."""
        return Pose(
            rotation=self._scan_frame.get(types.OsefKeys.POSE.value).get("rotation"),
            translation=self._scan_frame.get(types.OsefKeys.POSE.value).get(
                "translation"
            ),
        )


class AugmentedCloud(ScanFrame):
    """Helper class for augmented cloud."""

    def __init__(self, osef_frame: dict):
        """Constructor."""
        super().__init__(osef_frame)

        if types.OsefKeys.AUGMENTED_CLOUD.value not in self._scan_frame:
            raise ValueError(
                f"{types.OsefKeys.AUGMENTED_CLOUD.value} missing in Scan frame."
            )

        self._augmented_cloud = self._scan_frame.get(
            types.OsefKeys.AUGMENTED_CLOUD.value
        )

    @property
    def number_of_points(self) -> int:
        """Get number of points in the point cloud."""
        return self._augmented_cloud.get(types.OsefKeys.NUMBER_OF_POINTS.value)

    @property
    def number_of_layers(self) -> int:
        """Get number of layers in the point cloud."""
        return self._augmented_cloud.get(types.OsefKeys.NUMBER_OF_LAYERS.value)

    @property
    def reflectivities(self) -> npt.NDArray[np.int_]:
        """Reflectivities of the point cloud"""
        return self._augmented_cloud.get(types.OsefKeys.REFLECTIVITIES.value)

    @property
    def cartesian_coordinates(self) -> npt.NDArray[np.float32]:
        """Cartesian coordinates of the point cloud"""
        return self._augmented_cloud.get(types.OsefKeys.CARTESIAN_COORDINATES.value).T

    @property
    def object_ids(self) -> npt.NDArray[np.int32]:
        """Get the object IDs corresponding to every points of the point cloud."""
        return self._augmented_cloud.get(types.OsefKeys.OBJECT_ID_32_BITS.value)

    @property
    def background_bits(self) -> npt.NDArray[np.int8]:
        """Contains a padded list of bits, 1 bit per point of the cloud.
        If the bit is set, the point is a background point."""
        return self._augmented_cloud.get(types.OsefKeys._BACKGROUND_BITS.value)


class TrackedObjects(ScanFrame):
    """Helper class for Tracked objects."""

    def __init__(self, osef_frame: dict):
        """Constructor."""
        super().__init__(osef_frame)

        if types.OsefKeys.TRACKED_OBJECTS.value not in self._scan_frame:
            raise ValueError(
                f"{types.OsefKeys.TRACKED_OBJECTS.value} missing in Scan frame."
            )

        self._tracked_objects = self._scan_frame.get(
            types.OsefKeys.TRACKED_OBJECTS.value
        )

    @property
    def number_of_objects(self) -> int:
        """Get the number of tracked objects."""
        return self._tracked_objects.get(types.OsefKeys.NUMBER_OF_OBJECTS.value)

    @property
    def object_ids(self) -> npt.NDArray[np.int32]:
        """Get numpy array of object IDs."""
        # Handle the 32 bits objects.
        return self._tracked_objects.get(
            types.OsefKeys.OBJECT_ID_32_BITS.value,
            self._tracked_objects.get(types.OsefKeys.OBJECT_ID.value),
        )

    @property
    def object_classes(self) -> npt.NDArray[np.int32]:
        """Get numpy array of object class IDs."""
        return self._tracked_objects.get(types.OsefKeys.CLASS_ID_ARRAY.value)

    @property
    def speed_vectors(self) -> npt.NDArray[np.float32]:
        """Get numpy array of object speeds."""
        return self._tracked_objects.get(types.OsefKeys.SPEED_VECTORS.value)

    @property
    def poses(self) -> List[Pose]:
        """Get object poses."""
        return [
            Pose(rotation=pose.get("rotation"), translation=pose.get("translation"))
            for pose in self._tracked_objects.get(types.OsefKeys.POSE_ARRAY.value)
        ]

    @property
    def slam_poses(self) -> List[Pose]:
        """Get object poses from SLAM."""
        return [
            Pose(rotation=pose.get("rotation"), translation=pose.get("translation"))
            for pose in self._tracked_objects.get(types.OsefKeys.SLAM_POSE_ARRAY.value)
        ]

    @property
    def bounding_boxes(self) -> npt.NDArray[np.float32]:
        """Get bounding boxes dimension."""
        return self._tracked_objects.get(types.OsefKeys.BBOX_SIZES.value)

    @property
    def object_properties(self) -> List[ObjectProperties]:
        """Get the object properties."""
        return [
            ObjectProperties(
                oriented=object_prop[0],
                is_seen=object_prop[1],
                has_valid_slam_pose=object_prop[2],
                is_static=object_prop[3],
            )
            for object_prop in self._tracked_objects.get(
                types.OsefKeys.OBJECT_PROPERTIES.value
            )
        ]


class Zones(ScanFrame):
    """Helper class to easily access data in zone data."""

    def __init__(self, osef_frame: dict):
        """Constructor."""
        super().__init__(osef_frame)
        for key in [
            types.OsefKeys.ZONES_DEF.value,
            types.OsefKeys.ZONES_OBJECTS_BINDING_32_BITS.value,
        ]:
            if key not in self._scan_frame:
                raise ValueError(f"{key} missing in scan_frame")

        self._zones_def = self._scan_frame.get(types.OsefKeys.ZONES_DEF.value)
        self._zones_binding = self._scan_frame.get(
            types.OsefKeys.ZONES_OBJECTS_BINDING_32_BITS.value,
            self._scan_frame.get(types.OsefKeys.ZONES_OBJECTS_BINDING.value),
        )

    @property
    def bindings(self) -> List[ZoneBindings]:
        """Object-zone bindings array"""
        return [
            ZoneBindings(
                zone_index=binding.get("zone_idx"), object_id=binding.get("object_id")
            )
            for binding in self._zones_binding
        ]

    @property
    def definitions(self) -> List[ZoneDef]:
        """Get the definition of each zone"""
        return [
            ZoneDef(
                zone_name=zone.get(types.OsefKeys.ZONE.value).get(
                    types.OsefKeys.ZONE_NAME.value
                ),
                zone_vertices=zone.get(types.OsefKeys.ZONE.value).get(
                    types.OsefKeys.ZONE_VERTICES.value
                ),
                zone_vertical_limits=zone.get(types.OsefKeys.ZONE.value).get(
                    types.OsefKeys.ZONE_VERTICAL_LIMITS.value
                ),
            )
            for zone in self._zones_def
        ]

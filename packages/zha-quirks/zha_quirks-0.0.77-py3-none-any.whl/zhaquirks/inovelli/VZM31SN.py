"""VZM31-SN Two in One Switch/Dimmer Module."""

from zigpy.profiles import zha
from zigpy.profiles.zha import DeviceType
from zigpy.quirks import CustomDevice
from zigpy.zcl.clusters.general import (
    Basic,
    Groups,
    Identify,
    LevelControl,
    OnOff,
    Ota,
    Scenes,
)
from zigpy.zcl.clusters.homeautomation import Diagnostic, ElectricalMeasurement
from zigpy.zcl.clusters.smartenergy import Metering

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)
from zhaquirks.inovelli import INOVELLI_AUTOMATION_TRIGGERS, Inovelli_VZM31SN_Cluster

INOVELLI_VZM31SN_CLUSTER_ID = 64561
WWAH_CLUSTER_ID = 64599


class InovelliVZM31SNv10(CustomDevice):
    """VZM31-SN 2 in 1 Switch/Dimmer Module."""

    signature = {
        MODELS_INFO: [("Inovelli", "VZM31-SN")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMABLE_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,  # 0
                    Identify.cluster_id,  # 3
                    Groups.cluster_id,  # 4
                    Scenes.cluster_id,  # 5
                    OnOff.cluster_id,  # 6
                    LevelControl.cluster_id,  # 8
                    Metering.cluster_id,  # 1794
                    ElectricalMeasurement.cluster_id,  # 2820
                    Diagnostic.cluster_id,  # 2821
                    INOVELLI_VZM31SN_CLUSTER_ID,  # 64561
                    WWAH_CLUSTER_ID,  # 64599
                ],
                OUTPUT_CLUSTERS: [Identify.cluster_id, Ota.cluster_id],  # 3  # 19
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [Basic.cluster_id, Identify.cluster_id],  # 0  # 3
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,  # 3
                    OnOff.cluster_id,  # 6
                    LevelControl.cluster_id,  # 8
                    INOVELLI_VZM31SN_CLUSTER_ID,  # 64561
                ],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMABLE_LIGHT,
                INPUT_CLUSTERS: [
                    Basic,  # 0
                    Identify,  # 3
                    Groups,  # 4
                    Scenes,  # 5
                    OnOff,  # 6
                    LevelControl,  # 8
                    Metering,  # 1794
                    ElectricalMeasurement,  # 2820
                    Diagnostic,  # 2821
                    Inovelli_VZM31SN_Cluster,  # 64561
                    WWAH_CLUSTER_ID,  # 64599
                ],
                OUTPUT_CLUSTERS: [
                    Identify,  # 3
                    OnOff,  # 6
                    LevelControl,  # 8
                    Ota,  # 19
                    Inovelli_VZM31SN_Cluster,  # 64561
                ],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [Basic, Identify],  # 0  # 3
                OUTPUT_CLUSTERS: [
                    Identify,  # 3
                    OnOff,  # 6
                    LevelControl,  # 8
                    Inovelli_VZM31SN_Cluster,  # 64561
                ],
            },
        },
    }

    device_automation_triggers = INOVELLI_AUTOMATION_TRIGGERS


class InovelliVZM31SNv9(CustomDevice):
    """VZM31-SN 2 in 1 Switch/Dimmer Module."""

    signature = {
        MODELS_INFO: [("Inovelli", "VZM31-SN")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,  # 0
                    Identify.cluster_id,  # 3
                    Groups.cluster_id,  # 4
                    Scenes.cluster_id,  # 5
                    OnOff.cluster_id,  # 6
                    LevelControl.cluster_id,  # 8
                    Metering.cluster_id,  # 1794
                    ElectricalMeasurement.cluster_id,  # 2820
                    Diagnostic.cluster_id,  # 2821
                    INOVELLI_VZM31SN_CLUSTER_ID,  # 64561
                    WWAH_CLUSTER_ID,  # 64599
                ],
                OUTPUT_CLUSTERS: [Identify.cluster_id, Ota.cluster_id],  # 3  # 19
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [Identify.cluster_id],  # 3
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,  # 3
                    OnOff.cluster_id,  # 6
                    LevelControl.cluster_id,  # 8
                    INOVELLI_VZM31SN_CLUSTER_ID,  # 64561
                ],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMABLE_LIGHT,
                INPUT_CLUSTERS: [
                    Basic,  # 0
                    Identify,  # 3
                    Groups,  # 4
                    Scenes,  # 5
                    OnOff,  # 6
                    LevelControl,  # 8
                    Metering,  # 1794
                    ElectricalMeasurement,  # 2820
                    Diagnostic,  # 2821
                    Inovelli_VZM31SN_Cluster,  # 64561
                    WWAH_CLUSTER_ID,  # 64599
                ],
                OUTPUT_CLUSTERS: [
                    Identify,  # 3
                    OnOff,  # 6
                    LevelControl,  # 8
                    Ota,  # 19
                    Inovelli_VZM31SN_Cluster,  # 64561
                ],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [Identify],  # 3
                OUTPUT_CLUSTERS: [
                    Identify,  # 3
                    OnOff,  # 6
                    LevelControl,  # 8
                    Inovelli_VZM31SN_Cluster,  # 64561
                ],
            },
        },
    }

    device_automation_triggers = INOVELLI_AUTOMATION_TRIGGERS


class InovelliVZM31SN(CustomDevice):
    """VZM31-SN 2 in 1 Switch/Dimmer Module."""

    signature = {
        MODELS_INFO: [("Inovelli", "VZM31-SN")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,  # 0
                    Identify.cluster_id,  # 3
                    Groups.cluster_id,  # 4
                    Scenes.cluster_id,  # 5
                    OnOff.cluster_id,  # 6
                    LevelControl.cluster_id,  # 8
                    Metering.cluster_id,  # 1794
                    ElectricalMeasurement.cluster_id,  # 2820
                    INOVELLI_VZM31SN_CLUSTER_ID,  # 64561
                ],
                OUTPUT_CLUSTERS: [Identify.cluster_id, Ota.cluster_id],  # 3  # 19
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [Identify.cluster_id],  # 3
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,  # 3
                    OnOff.cluster_id,  # 6
                    LevelControl.cluster_id,  # 8
                    INOVELLI_VZM31SN_CLUSTER_ID,  # 64561
                ],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMABLE_LIGHT,
                INPUT_CLUSTERS: [
                    Basic,  # 0
                    Identify,  # 3
                    Groups,  # 4
                    Scenes,  # 5
                    OnOff,  # 6
                    LevelControl,  # 8
                    Metering,  # 1794
                    ElectricalMeasurement,  # 2820
                    Diagnostic,  # 2821
                    Inovelli_VZM31SN_Cluster,  # 64561
                ],
                OUTPUT_CLUSTERS: [
                    Identify,  # 3
                    OnOff,  # 6
                    LevelControl,  # 8
                    Ota,  # 19
                    Inovelli_VZM31SN_Cluster,  # 64561
                ],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: DeviceType.DIMMER_SWITCH,
                INPUT_CLUSTERS: [Identify],  # 3
                OUTPUT_CLUSTERS: [
                    Identify,  # 3
                    OnOff,  # 6
                    LevelControl,  # 8
                    Inovelli_VZM31SN_Cluster,  # 64561
                ],
            },
        },
    }

    device_automation_triggers = INOVELLI_AUTOMATION_TRIGGERS

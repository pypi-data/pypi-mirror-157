# Copyright (c) 2022 Tulir Asokan
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from typing import Any, Dict, List, Optional
from enum import IntEnum

from attr import dataclass

from .event import EncryptionAlgorithm, EncryptionKeyAlgorithm, ToDeviceEvent
from .primitive import DeviceID, IdentityKey, SigningKey, UserID
from .util import SerializableAttrs, field


@dataclass
class UnsignedDeviceInfo(SerializableAttrs):
    device_display_name: Optional[str] = None


@dataclass
class DeviceKeys(SerializableAttrs):
    user_id: UserID
    device_id: DeviceID
    algorithms: List[EncryptionAlgorithm]
    keys: Dict[str, str]
    signatures: Dict[UserID, Dict[str, str]]
    unsigned: UnsignedDeviceInfo = None

    def __attrs_post_init__(self) -> None:
        if self.unsigned is None:
            self.unsigned = UnsignedDeviceInfo()

    @property
    def ed25519(self) -> Optional[SigningKey]:
        try:
            return SigningKey(self.keys[f"{EncryptionKeyAlgorithm.ED25519}:{self.device_id}"])
        except KeyError:
            return None

    @property
    def curve25519(self) -> Optional[IdentityKey]:
        try:
            return IdentityKey(self.keys[f"{EncryptionKeyAlgorithm.CURVE25519}:{self.device_id}"])
        except KeyError:
            return None


@dataclass
class QueryKeysResponse(SerializableAttrs):
    failures: Dict[str, Any]
    device_keys: Dict[UserID, Dict[DeviceID, DeviceKeys]]


@dataclass
class ClaimKeysResponse(SerializableAttrs):
    failures: Dict[str, Any]
    one_time_keys: Dict[UserID, Dict[DeviceID, Dict[str, Any]]]


class TrustState(IntEnum):
    UNSET = 0
    VERIFIED = 1
    BLACKLISTED = 2
    IGNORED = 3


@dataclass
class DeviceIdentity:
    user_id: UserID
    device_id: DeviceID
    identity_key: IdentityKey
    signing_key: SigningKey

    trust: TrustState
    deleted: bool
    name: str


@dataclass
class OlmEventKeys(SerializableAttrs):
    ed25519: SigningKey


@dataclass
class DecryptedOlmEvent(ToDeviceEvent, SerializableAttrs):
    keys: OlmEventKeys
    recipient: UserID
    recipient_keys: OlmEventKeys
    sender_device: Optional[DeviceID] = None
    sender_key: IdentityKey = field(hidden=True, default=None)

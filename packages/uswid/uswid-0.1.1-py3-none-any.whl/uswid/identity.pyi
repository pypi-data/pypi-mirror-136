from .entity import uSwidEntity as uSwidEntity, uSwidEntityRole as uSwidEntityRole
from .enums import uSwidGlobalMap as uSwidGlobalMap
from .errors import NotSupportedError as NotSupportedError
from .link import uSwidLink as uSwidLink
from typing import Any, Optional

class uSwidIdentity:
    tag_id: Any
    tag_version: Any
    software_name: Any
    software_version: Any
    summary: Any
    product: Any
    colloquial_version: Any
    revision: Any
    edition: Any
    generator: str
    def __init__(self, tag_id: Optional[str] = ..., tag_version: int = ..., software_name: Optional[str] = ..., software_version: Optional[str] = ...) -> None: ...
    def add_entity(self, entity: uSwidEntity) -> None: ...
    def add_link(self, link: uSwidLink) -> None: ...
    def import_bytes(self, blob: bytes) -> None: ...
    def import_xml(self, xml: bytes) -> None: ...
    def import_ini(self, ini: str) -> None: ...
    def export_bytes(self) -> bytes: ...

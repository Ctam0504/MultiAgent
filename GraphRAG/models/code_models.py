from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class CodeChunk:
    id: str
    type: str
    file_path: str
    content: str

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "type": self.type
        }
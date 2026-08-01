from dataclasses import dataclass, field


@dataclass
class MetadataResult:
    title: str = ""
    description: str = ""
    genre: str = ""
    developer: str = ""
    publisher: str = ""
    release_date: str = ""
    cover_path: str = ""

    # Additional covers found during search
    cover_options: list[str] = field(default_factory=list)

    # Source information
    source: str = ""
    source_id: str = ""

    # Confidence score 0-100
    confidence: int = 0

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "genre": self.genre,
            "developer": self.developer,
            "publisher": self.publisher,
            "release_date": self.release_date,
            "cover_path": self.cover_path,
            "cover_options": self.cover_options,
            "source": self.source,
            "source_id": self.source_id,
            "confidence": self.confidence,
        }
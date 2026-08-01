from services.metadata.metadata_result import MetadataResult


from services.metadata_service import GameMetadataService


class SteamProvider:
    """
    Steam metadata adapter.

    Converts existing Steam metadata service
    into the new provider architecture.
    """

    name = "Steam"

    def search(self, game_title):
        results = []

        try:
            metadata = GameMetadataService.fetch_metadata(
                game_title
            )

            if metadata:
                result = MetadataResult(
                    title=metadata.title,
                    description=metadata.description,
                    genre=metadata.genre,
                    developer=metadata.developer,
                    publisher=metadata.publisher,
                    release_date=metadata.release_date,
                    cover_path=metadata.cover_path,
                    source=self.name,
                    confidence=80
                )

                results.append(result)

        except Exception as error:
            print(
                f"Steam provider error: {error}"
            )

        return results
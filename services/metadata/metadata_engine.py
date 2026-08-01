from services.metadata.metadata_result import MetadataResult
from services.metadata.providers.steam_provider import SteamProvider


class MetadataEngine:
    """
    Central metadata search controller.

    All metadata providers will be accessed through this class.
    """

    def __init__(self):
        self.providers = [
            SteamProvider()
        ]

    def search(self, game_title):
        """
        Search all available providers.
        Returns a list of MetadataResult objects.
        """

        results = []

        for provider in self.providers:
            try:
                provider_results = provider.search(game_title)

                if provider_results:
                    results.extend(provider_results)

            except Exception as error:
                print(
                    f"Metadata provider error: {error}"
                )

        return self.rank_results(results)


    def rank_results(self, results):
        """
        Sort results by confidence score.
        Highest confidence first.
        """

        return sorted(
            results,
            key=lambda result: result.confidence,
            reverse=True
        )
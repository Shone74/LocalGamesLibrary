from services.metadata.metadata_engine import MetadataEngine


def main():
    engine = MetadataEngine()

    print("Testing Metadata Engine...")

    results = engine.search(
        "Resident Evil 4"
    )

    if not results:
        print("No metadata results found.")
        return

    print(
        f"Found {len(results)} result(s)"
    )

    for result in results:
        print("--------------------")
        print(
            "Title:",
            result.title
        )
        print(
            "Developer:",
            result.developer
        )
        print(
            "Publisher:",
            result.publisher
        )
        print(
            "Genre:",
            result.genre
        )
        print(
            "Cover:",
            result.cover_path
        )
        print(
            "Source:",
            result.source
        )
        print(
            "Confidence:",
            result.confidence
        )


if __name__ == "__main__":
    main()
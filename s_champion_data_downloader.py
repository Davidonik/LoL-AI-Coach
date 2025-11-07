import os
import requests
import json
from typing import Dict, Any


class ChampionDataDownloader:
    """
    Fetches and stores League of Legends champion data from Riot's Data Dragon (DDragon).
    Creates one JSON file per champion.
    """

    def __init__(self, language: str = "en_US", output_dir: str = "champions"):
        self.language = language
        self.version = self._get_latest_version()
        self.base_url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/data/{self.language}"
        self.output_dir = output_dir

        # Ensure output folder exists
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_latest_version(self) -> str:
        """Fetch the latest available DDragon version."""
        versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(versions_url)
        response.raise_for_status()
        return response.json()[0]

    def download_all_champions(self) -> None:
        """Download and save each champion’s data as a separate JSON file."""
        print(f"Fetching champion list for version {self.version}...")

        champion_list_url = f"{self.base_url}/champion.json"
        response = requests.get(champion_list_url)
        response.raise_for_status()
        champion_list = response.json()["data"]

        print(f"Found {len(champion_list)} champions. Starting download...")

        for champ_name in champion_list:
            try:
                detail_url = f"{self.base_url}/champion/{champ_name}.json"
                detail_response = requests.get(detail_url)
                detail_response.raise_for_status()

                champ_data = detail_response.json()["data"][champ_name]

                # Define file path
                file_path = os.path.join(self.output_dir, f"{champ_name}.json")

                # Save to file
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(champ_data, f, ensure_ascii=False, indent=2)

                print(f"Saved: {file_path}")

            except Exception as e:
                print(f"Failed to load {champ_name}: {e}")

        print(f"\n All champions saved to '{self.output_dir}/' for patch {self.version}")


if __name__ == "__main__":
    downloader = ChampionDataDownloader()
    downloader.download_all_champions()

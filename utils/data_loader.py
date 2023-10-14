import os
import json
import lzma
import requests
import mimetypes
import pandas as pd
from tqdm import tqdm
from glob import glob
from zipfile import ZipFile
from bs4 import BeautifulSoup
from unicodedata import normalize


class PublicBulkDataLoader:
    """
    This class is used to download and extract the bulk data from
    https://case.law/bulk/download/ website.
    """

    BASE_URL: str = "https://case.law/bulk/download"

    def __init__(self, data_path: str = "data") -> None:
        """
        Args:
            data_path (str, optional): Path to store the downloaded data. Defaults to "data".
        """

        if not os.path.isdir(data_path):
            os.mkdir(data_path)

        self.data_path = data_path
        if len(self.jsonl_file_paths) == 0:
            self.download()
        self.load()

    @property
    def jsonl_file_paths(self) -> list:
        """
        Returns the list of jsonl file paths.

        Returns:
            list: List of jsonl file paths.
        """

        return glob(f"{self.data_path}/*.jsonl")

    def _fetch(self) -> dict:
        """
        Fetches the bulk data information from the website.

        Returns:
            dict: Dictionary containing the bulk data information.
        """

        response = requests.get(self.BASE_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        _content = soup.find("div", class_="main-content")

        results = dict()
        for _item in _content.find_all("div", class_="row"):
            results[_item.find("div", class_="section-subtitle").text] = {
                _type.find("a").text: {
                    "link": _type.find("a")["href"],
                    "size": normalize(
                        "NFKD",
                        _type.find("div", class_="file-size").text,
                    ),
                }
                for _type in _item.find_all("div", class_="export-type")
            }
        return results

    def _download(self, key: str, link: str) -> str:
        """
        Downloads the bulk data from the given link.

        Args:
            key (str): Key of the fetched result.
            link (str): Link to download the bulk data.

        Returns:
            str: Path to the downloaded file.
        """

        response = requests.get(link, stream=True)
        _content_type = response.headers["content-type"]

        ext = mimetypes.guess_extension(_content_type)
        file_name = f"{self.data_path}/{key.lower().replace(' ', '-')}{ext}"

        with open(file_name, "wb") as _file:
            for _chunk in response.iter_content(chunk_size=2048):
                _file.write(_chunk)
        return file_name

    def _extract_zip(self, file_name: str) -> str:
        """
        Extracts the zip file and returns the path to the extracted file.

        Args:
            file_name (str): Path to the zip file.

        Returns:
            str: Path to the extracted file."""

        with ZipFile(file_name, "r") as _zip:
            _file = [_f for _f in _zip.infolist() if _f.filename.endswith(".xz")][0]
            _path, _zip_file_name = os.path.split(file_name)
            _file.filename = _zip_file_name.replace("zip", "jsonl.xz")
            _zip.extract(_file, self.data_path)
            return os.path.join(_path, _file.filename)

    def _extract_xz(self, file_name: str) -> str:
        """
        Extracts the xz file and returns the path to the extracted file.

        Args:
            file_name (str): Path to the xz file.

        Returns:
            str: Path to the extracted file.
        """

        xz_file = lzma.open(file_name)
        jsonl_file = file_name.replace(".xz", "")
        _file = open(jsonl_file, "wb")
        _file.write(xz_file.read())
        return jsonl_file

    def download(self) -> None:
        """
        Downloads the bulk data and extracts it.
        """
        for key, value in tqdm(
            self._fetch().items(),
            desc="Downloading bulk data",
        ):
            link = value["text"]["link"]
            zip_file_path = self._download(key, link)
            xz_file_path = self._extract_zip(zip_file_path)
            _ = self._extract_xz(xz_file_path)
            [os.remove(_f) for _f in [zip_file_path, xz_file_path]]

    def load(self) -> None:
        """
        Loads the bulk data into a pandas dataframe.

        Returns:
            pd.DataFrame: Pandas dataframe containing the bulk data.
        """

        df_list = list()
        for _file_path in self.jsonl_file_paths:
            _data = [json.loads(line) for line in open(_file_path)]
            df_list.append(pd.json_normalize(_data).convert_dtypes())

        self.df = pd.concat(df_list, axis=0, ignore_index=True)
        self.df.drop(
            labels=[
                "name_abbreviation",
                "preview",
                "casebody.status",
                "court.name_abbreviation",
                "court.slug",
                "jurisdiction.name",
                "jurisdiction.slug",
                "casebody.data.parties",
            ],
            axis=1,
            inplace=True,
        )
        self.df["volume.volume_number"] = pd.to_numeric(self.df["volume.volume_number"])
        self.df["decision_date"] = pd.to_datetime(
            self.df["decision_date"],
            format="%Y-%m-%d",
            errors="coerce",
        )

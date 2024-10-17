import io
import csv
import zipfile


class ZipService:
    """Classe para manipular zips."""

    def unzip_csv_reader(self, zip_response):
        """Extrai arquivos CSV de um ZIP e retorna um iterador do CSV reader."""
        try:
            zip_file = zipfile.ZipFile(io.BytesIO(zip_response.content))
            for filename in zip_file.namelist():
                with zip_file.open(filename) as csv_file:
                    yield csv.DictReader(io.TextIOWrapper(csv_file, "utf-8"))
        except Exception as e:
            print(f"Erro ao processar o ZIP: {str(e)}")
            return None

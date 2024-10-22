from google.cloud import bigquery
import pandas as pd

class BigQueryClient:
    def __init__(self: "BigQueryClient"):
        """Configura o ambiente e inicializa o cliente do BigQuery."""
        self.client: bigquery.Client = self.configurar_ambiente()

    def configurar_ambiente(self: "BigQueryClient") -> bigquery.Client:
        """Configura o ambiente e retorna o cliente BigQuery."""
        return bigquery.Client()

    def consultar_dados(self: "BigQueryClient", query: str) -> pd.DataFrame:
        """Consulta dados no BigQuery usando a query fornecida.
        
        Args:
            self: Instância da classe BigQueryClient.
            query: Uma string contendo a consulta SQL.

        Returns:
            pd.DataFrame: O resultado da consulta no formato de DataFrame.
        """
        query_job = self.client.query(query)
        rows = [dict(row) for row in query_job]
        return pd.DataFrame(rows)

from google.cloud import bigquery
import pandas as pd
from typing import Optional

class BigQueryClient:
    def __init__(self: "BigQueryClient"):
        """Configura o ambiente e inicializa o cliente do BigQuery."""
        self.client: bigquery.Client = self.configurar_ambiente()

    def configurar_ambiente(self: "BigQueryClient") -> bigquery.Client:
        """Configura o ambiente e retorna o cliente BigQuery."""
        return bigquery.Client()

    def consultar_dados(self: "BigQueryClient", query: str, tipos: Optional[dict] = None) -> pd.DataFrame:
        """Consulta dados no BigQuery usando a query fornecida e aplica os tipos ao DataFrame.
        
        Args:
            query (str): Uma string contendo a consulta SQL.
            tipos (dict, optional): Dicionário com os tipos das colunas do DataFrame. O formato deve ser 
                                    {'nome_coluna': tipo}. Por padrão, None.

        Returns:
            pd.DataFrame: O resultado da consulta no formato de DataFrame, com os tipos aplicados.
        """
        query_job = self.client.query(query)
        rows = [dict(row) for row in query_job]
        df = pd.DataFrame(rows)

        df = df.replace({None: pd.NA, pd.NaT: pd.NA})

        if tipos:
            # Converte as colunas para os tipos especificados
            for coluna, tipo in tipos.items():
                if coluna in df.columns:
                    df[coluna] = df[coluna].astype(tipo)
        


        return df

    def inserir_dados(self, tabela: str, linhas: list[dict]):
        """
        Insere dados em uma tabela do BigQuery.

        :param tabela: Nome completo da tabela (ex: `projeto.dataset.tabela`).
        :param linhas: Lista de dicionários representando as linhas a serem inseridas.
        """
        table_ref = self.client.dataset(tabela.split('.')[1]).table(tabela.split('.')[2])
        errors = self.client.insert_rows_json(table_ref, linhas)
        if errors:
            raise RuntimeError(f"Erros ao inserir dados: {errors}")
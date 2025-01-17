from frozendict import frozendict
import os
from typing import Final, Callable


TOKENS_MUNICIPIOS: Final[list[dict]] = [
    {"municipio": "Alagoinha", "id_sus": "260060", "token": os.getenv('ENV_ALAGOINHA_PE')},
    {"municipio": "Baraúna", "id_sus": "240145", "token": os.getenv('ENV_BARAUNA_RN')},
    #{"municipio": "Brejo de Areia", "id_sus": "210215", "token": os.getenv('ENV_BREJODEAREIA_MA')},
    {"municipio": "Jucuruçu", "id_sus": "291845", "token": os.getenv('ENV_JUCURUCU_BA')},
    {"municipio": "Lago Verde", "id_sus": "210590", "token": os.getenv('ENV_LAGOVERDE_MA')},
    {"municipio": "Lagoa do Ouro", "id_sus": "260860", "token": os.getenv('ENV_LAGOADOOURO_PE')},
    {"municipio": "Marajá do Sena", "id_sus": "210635", "token": os.getenv('ENV_MARAJADOSENA_MA')},
    {"municipio": "Monsenhor Tabosa", "id_sus": "230860", "token": os.getenv('ENV_MONSENHORTABOSA_CE')},
    #{"municipio": "Oiapoque", "id_sus": "160050", "token": os.getenv('ENV_OIAPOQUE_AP')},
    {"municipio": "Pacoti", "id_sus": "230980", "token": os.getenv('ENV_PACOTI_CE')},
    {"municipio": "Paulo Ramos", "id_sus": "210810", "token": os.getenv('ENV_PAULORAMOS_MA')},
    {"municipio": "Salvaterra", "id_sus": "150630", "token": os.getenv('ENV_SALVATERRA_PA')},
    {"municipio": "Tarrafas", "id_sus": "231325", "token": os.getenv('ENV_TARRAFAS_CE')},
    {"municipio": "Vitorino Freire", "id_sus": "211300", "token": os.getenv('ENV_VITORINOFREIRE_MA')},
]

USUARIOS_COLUNAS_TIPOS: Final[frozendict] = frozendict(
    # Define os tipos esperados nas colunas de usuarios_mvp01_segundo_ciclo
    {
        "dia_da_semana_id": int,
        "municipio_id_sus": str,
        "municipio_nome": str,
        "nome": str,
        "cns": str,
        "cpf": str,
        "documento_identificador": str,
        "telefone": str,
        "dt_nascimento": str,
        "linha_cuidado": str,
        "estabelecimento_nome": str,
        "estabelecimento_endereco": str,
        "estabelecimento_telefone": str,
        "estabelecimento_documentos": str,
        "estabelecimento_horario": str,
        "equipe_ine_vinc": str,
        "equipe_ine": str,
        "equipe_nome": str,
        "horarios_cito": str,
        "horarios_cronicos": str,
        "data_envio_primeiro_ciclo": str,
        "data_programada_segundo_ciclo": str,
    }
)

EVENTOS_COLUNAS_TIPOS: Final[frozendict] = frozendict(
    # Define os tipos esperados nas colunas de eventos_mvp01_segundo_ciclo
    {
        "municipio_id_sus": str,
        "equipe_ine_vinculo": str,
        "nome": str,
        "cns": str,
        "cpf": str,
        "documento_identificador": str,
        "telefone": str,
        "dt_nascimento": str,
        "linha_cuidado": str,
        "mensagem_tipo": int,
        "evento_status": int,
        "evento_status_code": str,
        "evento_message_code": str,
        "evento_data": str,
        "criacao_data": str,
        "atualizacao_data": str,
    }
)

IMAGEM_POR_MUNICIPIO: Final[dict[str, dict[str, dict[str, str]]]] = {
    "210810": {  # Paulo Ramos
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/4mbiyDB.png",
            "cronicos": "https://i.imgur.com/x9905Wf.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/L6WsLIi.png",
            "cronicos": "https://i.imgur.com/J3NMZd1.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/8m6z5Ew.png",
            "cronicos": "https://i.imgur.com/zgGY9cL.png",
        },
    },
    "210590": {  # Lago Verde
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/UCQaeC0.png",
            "cronicos": "https://i.imgur.com/Fs3RzoM.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/23cOHxO.png",
            "cronicos": "https://i.imgur.com/VnhK1DX.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/GKYyeLB.png",
            "cronicos": "https://i.imgur.com/65E2j4j.png",
        },
    },
    "230980": {  # Pacoti
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/Puk3nHM.png",
            "cronicos": "https://i.imgur.com/ntgrvWr.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/kikEAqt.png",
            "cronicos": "https://i.imgur.com/Tph1UDR.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/RLOSe7k.png",
            "cronicos": "https://i.imgur.com/8aUwuyI.png",
        },
    },
    "230860": {  # Monsenhor Tabosa
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/Dws7bjO.png",
            "cronicos": "https://i.imgur.com/opJea25.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/u3GYt0o.png",
            "cronicos": "https://i.imgur.com/L5LrUYu.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/7zYADGZ.png",
            "cronicos": "https://i.imgur.com/sZdkv60.png",
        },
    },
    "210635": {  # Marajá do Sena
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/FBTWDtf.png",
            "cronicos": "https://i.imgur.com/82MgSfn.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/631uFyM.png",
            "cronicos": "https://i.imgur.com/mv4bvSe.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/akcp7PA.png",
            "cronicos": "https://i.imgur.com/X9je2op.png",
        },
    },
    "260060": {  # Alagoinha
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/6UOV3Bo.png",
            "cronicos": "https://i.imgur.com/Oty4aiM.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/SZCbnVa.png",
            "cronicos": "https://i.imgur.com/0k63zu0.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/DHUi7WR.png",
            "cronicos": "https://i.imgur.com/LUM6g7n.png",
        },
    },
    "240145": {  # Baraúna
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/G2SjNkj.png",
            "cronicos": "https://i.imgur.com/z0V8ihk.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/K8pKPnR.png",
            "cronicos": "https://i.imgur.com/yGC5DQO.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/sah4CjL.png",
            "cronicos": "https://i.imgur.com/sxjOM1x.png",
        },
    },
    "291845": {  # Jucuruçu
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/qUOzJoG.png",
            "cronicos": "https://i.imgur.com/J90cOfE.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/bVEHG0l.png",
            "cronicos": "https://i.imgur.com/MesCTBw.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/J602wxv.png",
            "cronicos": "https://i.imgur.com/sCakw2S.png",
        },
    },
    "211300": {  # Vitorino Freire
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/KFAtmAM.png",
            "cronicos": "https://i.imgur.com/STqcB8z.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/1WbD1TF.png",
            "cronicos": "https://i.imgur.com/1XUjOYh.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/ljmLbCo.png",
            "cronicos": "https://i.imgur.com/tl6EaUM.png",
        },
    },
    "210215": {  # Brejo de Areia
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/McjjPAX.png",
            "cronicos": "https://i.imgur.com/iYBaohC.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/GLFz2vy.png",
            "cronicos": "https://i.imgur.com/OBNhQB4.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/aykJ41B.png",
            "cronicos": "https://i.imgur.com/0CTYJwE.png",
        },
    },
    "160050": {  # Oiapoque
        "mensagem_a": {
            "citopatologico": "",
            "cronicos": "",
        },
        "mensagem_b": {
            "citopatologico": "",
            "cronicos": "",
        },
        "mensagem_c": {
            "citopatologico": "",
            "cronicos": "",
        },
    },
    "231325": {  # Tarrafas
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/kPt8z9l.png",
            "cronicos": "https://i.imgur.com/QjE35g9.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/0l2wwp4.png",
            "cronicos": "https://i.imgur.com/3asG0Bl.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/rn88TBt.png",
            "cronicos": "https://i.imgur.com/wV2unlL.png",
        },
    },
    "150630": {  # Salvaterra
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/5SUetAi.png",
            "cronicos": "https://i.imgur.com/WgYro4n.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/iwdjo53.png",
            "cronicos": "https://i.imgur.com/T2tHkyd.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/xzihd6a.png",
            "cronicos": "https://i.imgur.com/xRu6jFU.png",
        },
    },
    "260860": {  # Lagoa do Ouro
        "mensagem_a": {
            "citopatologico": "https://i.imgur.com/t8tb5BB.png",
            "cronicos": "https://i.imgur.com/g3LRSdn.png",
        },
        "mensagem_b": {
            "citopatologico": "https://i.imgur.com/eHM4lob.png",
            "cronicos": "https://i.imgur.com/ply5VdR.png",
        },
        "mensagem_c": {
            "citopatologico": "https://i.imgur.com/6ZwMIyo.png",
            "cronicos": "https://i.imgur.com/nq6lB7T.png",
        },
    },
}


# Função para buscar o link correto no IMAGEM_POR_MUNICIPIO
def get_imagem_url(municipio_id_sus: str, template_tipo: str, linha_cuidado: str) -> str:
    return IMAGEM_POR_MUNICIPIO.get(municipio_id_sus, {}).get(template_tipo, {}).get(linha_cuidado, "")


MENSAGEM_TEMPLATE: Final[dict[str, dict[int, tuple[str, str, str, Callable[[str, str], str]]]]] = {
    "citopatologico": {
        1: ("mensagem_a", "imagem_v0", "image", get_imagem_url),
        2: ("mensagem_a", "video_v0", "video", "https://i.imgur.com/9N6AOBE.mp4"),
        3: ("mensagem_a", "texto_v0", "text", ""),
        4: ("mensagem_b", "imagem_v0", "image", get_imagem_url),
        5: ("mensagem_b", "video_v0", "video", "https://i.imgur.com/QaCizTU.mp4"),
        6: ("mensagem_b", "texto_v0", "text", ""),
        7: ("mensagem_c", "imagem_v1", "image", get_imagem_url),
        8: ("mensagem_c", "video_v1", "video", "https://i.imgur.com/KF3JOgC.mp4"),
        9: ("mensagem_c", "texto_v1", "text", ""),
    },
    "cronicos": {
        1: ("mensagem_a", "imagem_v0", "image", get_imagem_url),
        2: ("mensagem_a", "video_v0", "video", "https://i.imgur.com/bV3h2jd.mp4"),
        3: ("mensagem_a", "texto_v0", "text", ""),
        4: ("mensagem_b", "imagem_v0", "image", get_imagem_url),
        5: ("mensagem_b", "video_v0", "video", "https://i.imgur.com/b25BbpN.mp4"),
        6: ("mensagem_b", "texto_v0", "text", ""),
        7: ("mensagem_c", "imagem_v0", "image", get_imagem_url),
        8: ("mensagem_c", "video_v0", "video", "https://i.imgur.com/SKD70i6.mp4"),
        9: ("mensagem_c", "texto_v0", "text", ""),
    },
}
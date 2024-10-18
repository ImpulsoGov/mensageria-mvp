### Match com equipe e Upload na Turn
# A partir dos usuários selecionados para o dia no Passo 1, une suas informações com suas informações 
# de equipe/estabelecimentos que esta no Big Query e advem da Turn. Após isso da upload desses contatos na turn.


#### Configurações iniciais do ambiente



#### Match
# Une dados da tabela de seção diaria "ip_mensageria_camada_prata.historico_envio_mensagens" do BigQuery 
# com os dados do estabelecimento que a pessoa é pertencente, por meio do dos dados que estão registradas 
# na view "ip_mensageria_camada_prata.contact_details_turnio" no BigQuery.



# #### Upload
# Da upload no perfil respectivo ao seu municipio na Turn. Inclui os seguintes campos:
# - opted_in=true
# - 
tokens_municipios = [
    {"municipio": "Paulo Ramos", "id_sus": "210810", "token": os.getenv('ENV_PAULORAMOS_MA')},
    {"municipio": "Pacoti", "id_sus": "210810", "token": os.getenv('ENV_PACOTI_CE')},
    {"municipio": "Marajá do Sena", "id_sus": "210810", "token": os.getenv('ENV_MARAJADOSENA_MA')},
    {"municipio": "Monsenhor Tabosa", "id_sus": "210810", "token": os.getenv('ENV_MONSENHORTABOSA_CE')},
    {"municipio": "Lago Verde", "id_sus": "210590", "token": os.getenv('ENV_LAGOVERDE_MA')}                                        
]

print("Oie")
    
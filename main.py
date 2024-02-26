import json
import requests
import psycopg2

baseUrl = "https://servicodados.ibge.gov.br/api/v3"
tabelaAgregado = 4093
variaveis = "4099"
localidades = "BR|N3" #BR, Unidades Federativas
classificacao = "2[all]" #Total, Homens, Mulheres
periodos = "201201|201202|201203"


url = (f"{baseUrl}/agregados/{tabelaAgregado}/periodos/{periodos}/variaveis/{variaveis}?"
       f"localidades={localidades}&classificacao={classificacao}")

response = requests.get(url)
print(f"STATUS: {response.status_code}\n\n")
if response.status_code != 200:
    print(response.content)
    exit()


with open("results.json", "w+") as file:
    file.write(json.dumps(response.json(), indent=3))

conn = psycopg2.connect(database="casacivil",
                        host="localhost",
                        user="ibge_api",
                        password="IBGE_API_123456",
                        port="5432")

cursor = conn.cursor()

print("id_sexo,id_localidade,periodo,valor")
resultados = response.json()[0]["resultados"]
for resultado in resultados:
    sexo = ""
    id_sexo = ""
    classificacoes = resultado["classificacoes"]
    for classificacao in classificacoes:
        for chave, categoria in classificacao["categoria"].items():
            sexo = categoria
            id_sexo = chave
    for serie in resultado["series"]:
        localidade = serie["localidade"]["nome"]
        id_localidade = serie["localidade"]["id"]
        for periodo, taxa in serie["serie"].items():
            print(f"{id_sexo},{id_localidade},{periodo},{taxa},trimestral")
            sql = (f"INSERT INTO taxa_desocupacao_semana_referente_14_anos_ou_mais"
                   f"(id_sexo, id_localidade, periodo, taxa) "
                   f"VALUES (%s, %s, %s, %s)")
            try:
                cursor.execute(sql, (id_sexo, id_localidade, periodo, taxa))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(e)

cursor.close()
conn.close()

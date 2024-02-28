import json
import requests
import psycopg2

baseUrl = "https://servicodados.ibge.gov.br/api/v3"
tabelaAgregado = 4093
variaveis = "4099"
localidades = "BR|N3" #BR, Unidades Federativas
classificacao = "2[6794]" #Total, Homens, Mulheres
periodos = "201201|201202|201203|201301|201302|201303|201401|201402"


url = (f"{baseUrl}/agregados/{tabelaAgregado}/periodos/{periodos}/variaveis/{variaveis}?"
       f"localidades={localidades}&classificacao={classificacao}")

response = requests.get(url)
print(f"STATUS: {response.status_code}\n\n")
if response.status_code != 200:
    print(response.content)
    exit()


with open("dados/results.json", "w+") as file:
    file.write(json.dumps(response.json(), indent=3))

conn = psycopg2.connect(database="casacivil",
                        host="localhost",
                        user="ibge_api",
                        password="IBGE_API_123456",
                        port="5432")

cursor = conn.cursor()

print("id_sexo,id_localidade,periodo,valor")
file = open("dados/indicador.csv", "w+")
file.write("ano,valor,indicador_codigo,local_codigo,data,periodoDaFrequencia,frequencia\n")
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
            ano = int(periodo[0:4])
            frequencia = int(periodo[4:])
            print(f"{id_sexo},{id_localidade},{periodo},{taxa},trimestral")
            sql = (f"INSERT INTO indicadores"
                   f"(ano, valor, indicador_codigo, local_codigo, periodo_da_frequencia, frequencia) "
                   f"VALUES (%s, %s, 147, %s, %s, 'Trimestral')")
            file.write(f"{ano},{taxa},147,{id_localidade},{frequencia},Trimestral\n")
            try:
                cursor.execute(sql, (ano, taxa, id_localidade, frequencia))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(e)

file.close()
cursor.close()
conn.close()

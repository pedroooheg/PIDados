import MedPerUBS
import json
import csv

if __name__ == "__main__":
    with open("data/ubs_upa.json", "r", encoding="utf-8") as j:
        data_json = json.load(j)

    with open("data/medicamentos.csv", "r", encoding="utf-8") as f:
        leitor_csv_med = csv.reader(f)

        for unidade in data_json["d"]:           
            for med in leitor_csv_med:
                endereco = {
                    "end": f"{unidade['Logradouro']}, {unidade['Numero']} - {unidade['Bairro']}",
                    "lat": unidade["Geo"]["Latitude"],
                    "lng": unidade["Geo"]["Longitude"],
                }

                medicamento = {
                    "id": med[0],
                    "nome": med[1]
                }

                MedPerUBS.getDispMedicamentoPorUnidade(endereco, medicamento)
                break
            break      

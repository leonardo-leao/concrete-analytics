import requests
from datetime import datetime

class Archiver():

    @staticmethod
    def datetimeToStr(dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def pv_request(pv, date_from, date_to):
    
        query = {
            "pv": f"{pv}",
            "from": f"{date_from}",
            "to": f"{date_to}"
        }

        response = requests.get("http://10.0.38.42/retrieval/data/getData.json", params=query)
        json = response.json()
        meta = json[0]['meta']
        data = json[0]['data']
        
        # Separate data
        dt = []
        values = []

        for i in range(len(data)):
            date = datetime.fromtimestamp(data[i]['secs'])
            dt.append(date)
            values.append(data[i]['val'])
            
        return (dt, values, meta['EGU'])

    @staticmethod
    def generate_concrete_pvs():
        onlyTemp = [4, 9, 14, 19]
        complete = [5, 10, 15, 20]
        simple = [2, 3, 6, 7, 8, 11, 12, 13, 16, 17, 18]

        pvs = []
        for i in range(1, 21):
            j = i if i >= 10 else f"0{i}"
            if (i in onlyTemp) or (i in simple):
                for level in ["A", "B", "C"]:
                    pvs.append(f"TU-{j}S:SS-Concrete-5{level}P:Temp-Mon")
            if i in simple:
                for position in [7, 9]:
                    for level in ["A", "C"]:
                        pvs.append(f"TU-{j}S:SS-Concrete-{position}{level}:StrainY-Mon")
                        pvs.append(f"TU-{j}S:SS-Concrete-{position}{level}N:Temp-Mon")
            if i in complete:
                for position in [1, 3, 4, 5, 6, 7, 9]:
                    for level in ["A", "B", "C"]:
                        if position in [1, 3, 4, 6, 7, 9] and level in ["A", "C"]:
                            pvs.append(f"TU-{j}S:SS-Concrete-{position}{level}:StrainY-Mon")
                            pvs.append(f"TU-{j}S:SS-Concrete-{position}{level}:StrainZ-Mon")
                            pvs.append(f"TU-{j}S:SS-Concrete-{position}{level}N:Temp-Mon")
                        if position in [3, 4, 6, 7] and level in ["A", "C"]:
                            pvs.append(f"TU-{j}S:SS-Concrete-{position}{level}V:Temp-Mon")
                        if (position in [3, 4, 6, 7] and level in ["B"]) or (position == 5 and level in ["A", "C"]):
                            pvs.append(f"TU-{j}S:SS-Concrete-{position}{level}N:Temp-Mon")
                            pvs.append(f"TU-{j}S:SS-Concrete-{position}{level}V:Temp-Mon")

        return pvs

    # Corrigir bugs e erros
    @staticmethod
    def get_concrete_pvName(string):
        out = []
        parameters = string.split("*")
        for pv in Archiver.generate_concrete_pvs():
            str_pos = 0
            for i in range(len(parameters)):
                if parameters[i] != "":
                    while str_pos < len(pv):
                        if parameters[i] != pv[str_pos : str_pos + len(parameters[i])]:
                            str_pos = str_pos + 1
                        else:
                            str_pos = str_pos + len(parameters[i])
                            break
            if i + 1 == len(parameters) and str_pos < len(pv):
                out.append(pv)
            if string == pv:
                out.append(pv)
        return out
                    
if __name__ == "__main__":
    from archiver import Archiver as arc
    print(arc.get_concrete_pvName("TU-05S:SS-Concrete-3AN:Temp-Mon"))
from archiver import Archiver as arc
from datetime import datetime, timedelta

class Analysis():

    @staticmethod
    def changeDatetime(dt):
        if dt.minute <= 15:
            dt = dt.replace(minute = 0, second = 0)
        elif dt.minute <= 45:
            dt = dt.replace(minute = 30, second = 0)
        else:
            dt = dt + timedelta(hours = 1)
            dt = dt.replace(minute = 0, second = 0)
        return dt
    
    @staticmethod
    def temperatureAvg(ini, end):
        data = {}
        pvs = arc.get_concrete_pvName("TU*Temp")
        for i in range(len(pvs)):
            x, y, units = arc.pv_request(pvs[i], arc.datetimeToStr(ini), arc.datetimeToStr(end))
            for j in range(len(x)):
                x[j] = Analysis.changeDatetime(x[j])
                if x[j] not in data.keys():
                    data[x[j]] = [y[j]]
                else:
                    data[x[j]].append(y[j])
        
        keys = sorted(list(data.keys()))
        print(keys[-1])
        x = []; y = []
        for i in range(len(keys)):
            if ini <= keys[i] <= end:
                x.append(keys[i])
                y.append(sum(data[keys[i]])/len(data[keys[i]]))

        return (x, y)

if __name__ == "__main__":
    ini = datetime(year = 2022, month = 5, day = 1)
    end = datetime(year = 2022, month = 5, day = 5)
    print(Analysis.temperatureAvg(ini, end))
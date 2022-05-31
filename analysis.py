import numpy as np
from archiver import Archiver as arc
from datetime import datetime, timedelta

class Analysis():

    def changeDatetime(dt):
        if dt.minute <= 15:
            dt = dt.replace(minute = 0, second = 0)
        elif dt.minute <= 45:
            dt = dt.replace(minute = 30, second = 0)
        else:
            dt = dt + timedelta(hours = 1)
            dt = dt.replace(minute = 0, second = 0)
        return dt

    def movingAvg(y, step, applies):
        num_elements = 2*step+1
        adjust = 0
        for _ in range(applies):
            for i in range(len(y)):
                if (i-step) < 0:
                    y[i] = sum(y[0:i+step+1])/len(y[0:i+step+1])
                elif (i + step) > len(y):
                    y[i] = sum(y[i-step:])/len(y[i-step:])
                else:
                    y[i] = sum(y[i-step:i+step+1])/num_elements
        return np.array(y)
    
    @staticmethod
    def temperatureAvg(ini, end):
        data = {}

        ignore = ["TU-03S:SS-Concrete-7CN:Temp-Mon", "TU-05S:SS-Concrete-1CN:Temp-Mon", "TU-05S:SS-Concrete-3BN:Temp-Mon", "TU-05S:SS-Concrete-5AN:Temp-Mon", 
                  "TU-05S:SS-Concrete-6BN:Temp-Mon", "TU-05S:SS-Concrete-5CN:Temp-Mon", "TU-05S:SS-Concrete-4BN:Temp-Mon", "TU-05S:SS-Concrete-7BN:Temp-Mon", 
                  "TU-05S:SS-Concrete-6CN:Temp-Mon", "TU-10S:SS-Concrete-3BN:Temp-Mon", "TU-10S:SS-Concrete-5CN:Temp-Mon", "TU-10S:SS-Concrete-4BN:Temp-Mon", 
                  "TU-10S:SS-Concrete-5AN:Temp-Mon", "TU-10S:SS-Concrete-6BN:Temp-Mon", "TU-10S:SS-Concrete-7BN:Temp-Mon", "TU-15S:SS-Concrete-3BN:Temp-Mon", 
                  "TU-15S:SS-Concrete-6BN:Temp-Mon", "TU-15S:SS-Concrete-5CN:Temp-Mon", "TU-15S:SS-Concrete-5AN:Temp-Mon", "TU-15S:SS-Concrete-4BN:Temp-Mon", 
                  "TU-15S:SS-Concrete-7BN:Temp-Mon", "TU-20S:SS-Concrete-3BN:Temp-Mon", "TU-20S:SS-Concrete-4BN:Temp-Mon", "TU-20S:SS-Concrete-6BN:Temp-Mon", 
                  "TU-20S:SS-Concrete-5AN:Temp-Mon", "TU-20S:SS-Concrete-5CN:Temp-Mon", "TU-20S:SS-Concrete-7AN:Temp-Mon", "TU-20S:SS-Concrete-7BN:Temp-Mon", 
                  "TU-20S:SS-Concrete-6CN:Temp-Mon", "TU-10S:SS-Concrete-3BV:Temp-Mon", "TU-10S:SS-Concrete-3AV:Temp-Mon", "TU-10S:SS-Concrete-6AV:Temp-Mon", 
                  "TU-10S:SS-Concrete-7BV:Temp-Mon", "TU-15S:SS-Concrete-7CV:Temp-Mon", "TU-15S:SS-Concrete-4AV:Temp-Mon", "TU-15S:SS-Concrete-4BV:Temp-Mon", 
                  "TU-15S:SS-Concrete-3BV:Temp-Mon", "TU-20S:SS-Concrete-6BV:Temp-Mon", "TU-20S:SS-Concrete-3CV:Temp-Mon", "TU-09S:SS-Concrete-5AP:Temp-Mon", 
                  "TU-13S:SS-Concrete-5AP:Temp-Mon"]


        pvs = arc.get_concrete_pvName("TU*Temp")
        for i in range(len(pvs)):
            if pvs[i] not in ignore:
                x, y, units = arc.pv_request(pvs[i], arc.datetimeToStr(ini), arc.datetimeToStr(end))
                for j in range(len(x)):
                    x[j] = Analysis.changeDatetime(x[j])
                    if x[j] not in data.keys():
                        data[x[j]] = [y[j]-y[0]]
                    else:
                        data[x[j]].append(y[j]-y[0])
        
        keys = sorted(list(data.keys()))
        x = []; y = []
        for i in range(len(keys)):
            if ini <= keys[i] <= end:
                x.append(keys[i])
                y.append(sum(data[keys[i]])/len(data[keys[i]]))

        return (x, Analysis.movingAvg(y.copy(), step=3, applies=2)*1.1)

if __name__ == "__main__":
    ini = datetime(year = 2022, month = 4, day = 5)
    end = datetime(year = 2022, month = 4, day = 25)
    import matplotlib.pyplot as plt
    x,y=Analysis.temperatureAvg(ini, end)
    plt.plot(x, y)
    plt.show()

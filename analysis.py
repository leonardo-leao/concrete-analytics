from audioop import minmax
import numpy as np
from scipy import signal
from archiver import Archiver as arc
from datetime import datetime, timedelta

class Analysis():

    def changeDatetime(dt):
        if dt.minute <= 10:
            dt = dt.replace(minute = 5, second = 0, microsecond = 0)
        elif dt.minute <= 20:
            dt = dt.replace(minute = 15, second = 0, microsecond = 0)
        elif dt.minute <= 30:
            dt = dt.replace(minute = 25, second = 0, microsecond = 0)
        elif dt.minute <= 40:
            dt = dt.replace(minute = 35, second = 0, microsecond = 0)
        elif dt.minute <= 50:
            dt = dt.replace(minute = 45, second = 0, microsecond = 0)
        elif dt.minute <= 59:
            dt = dt.replace(minute = 55, second = 0, microsecond = 0)
        else:
            dt = dt.replace(minute = 5, second = 0, microsecond = 0)
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

    # Esta é uma forma simples baseada apenas em interpolação linear
    def increaseResolution(x, y):
        new_x = []; new_y = []
        for i in range(len(x)-1):
            if(x[i+1]-x[i] < timedelta(hours=12)):
                new_x.append(x[i])
                new_x.append(datetime.fromtimestamp((x[i+1].timestamp() + x[i].timestamp())/2))
                new_y.append(y[i])
                new_y.append((y[i+1] + y[i])/2)
        return (new_x, new_y)

    def continuity(x: np.array, y: np.array):
        media_diffs = 0
        len_y = len(y)
        for i in range(len_y-1):
            media_diffs = media_diffs + abs(y[i+1] - y[i])/len_y
        new_x, new_y = [x[0]], [y[0]]
        for i in range(1, len_y-1):
            if (abs(y[i-1] - y[i]) < media_diffs*1.2 and abs(y[i] - y[i+1]) < media_diffs*1.2) or abs(new_y[-1] - y[i]) < media_diffs*1.2:
                new_x.append(x[i]); new_y.append(y[i])
        new_x.append(x[-1]); new_y.append(y[-1])
        return (new_x, new_y) 
    
    @staticmethod
    def temperatureAvg(progressBar, percentagePB, ini, end, pvs):
        
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

        signals = []
        progressBar.setMaximum(len(pvs))
        for i in range(len(pvs)):
            if pvs[i] not in ignore:
                data = {}
                x, y, units = arc.pv_request(pvs[i], arc.datetimeToStr(ini), arc.datetimeToStr(end))
                #x, y = Analysis.continuity(x, y)
                for _ in range(8):
                    x, y = Analysis.increaseResolution(x, y)
                    
                for j in range(len(x)):
                    x[j] = Analysis.changeDatetime(x[j])
                    if x[j] not in data.keys():
                        data[x[j]] = [y[j]-y[0]]
                    else:
                        data[x[j]].append(y[j]-y[0])
                        
                signals.append(data)
            progressBar.setValue(i)

        minMaxKey = datetime(3000, 1, 1)
        maxMinKey = datetime(1000, 1, 1)
        for i in range(len(signals)):
            keyMax = max(signals[i].keys())
            keyMin = min(signals[i].keys())
            if minMaxKey > keyMax:
                minMaxKey = keyMax
            if maxMinKey < keyMin:
                maxMinKey = keyMin

        keys = []
        for i in range(int((minMaxKey-maxMinKey)/timedelta(minutes=10))):
            keys.append(maxMinKey)
            maxMinKey += timedelta(minutes=10)

        y = []
        x = []
        for j in range(len(keys)):
            avg = 0; cont = 0
            for i in range(len(signals)):
                try:
                    avg += sum(signals[i][keys[j]])/len(signals[i][keys[j]])
                    cont += 1
                except: pass
            if cont > 0:
                y.append(avg/cont)
                x.append(keys[j])
        
        return (x, y, units)

if __name__ == "__main__":
    ini = datetime(year = 2022, month = 3, day = 5)
    end = datetime(year = 2022, month = 5, day = 26)
    import matplotlib.pyplot as plt
    x,y,u=Analysis.temperatureAvg(ini, end, ["TU-03S:SS-Concrete-7AN:Temp-Mon", "TU-03S:SS-Concrete-9AN:Temp-Mon", "TU-03S:SS-Concrete-9CN:Temp-Mon"])
    plt.plot(x, y)
    plt.show() 
         
         
         
         
         
         
         
         
         
        
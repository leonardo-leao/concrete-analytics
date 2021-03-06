import statsmodels.api as sm
import numpy as np
from scipy import signal
from archiver import Archiver as arc
from datetime import datetime, timedelta

class Analysis():

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

    def changeDatetime(dt):
        if dt.minute < 15:
            dt = dt.replace(minute=0, second=0, microsecond=0)
        elif dt.minute < 45:
            dt = dt.replace(minute=30, second=0, microsecond=0)
        else:
            dt = dt + timedelta(hours=1)
            dt = dt.replace(minute=0, second=0, microsecond=0)
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

    def linearInterp(p1, p2, x):
        x1, y1 = p1
        x2, y2 = p2
        return y1 + (x - x1)*(y2 - y1)/(x2 - x1)

    # Esta ?? uma forma simples baseada apenas em interpola????o linear
    def increaseResolution(x, y):
        new_x = []; new_y = []
        for i in range(len(x)-1):
            if(x[i+1]-x[i] < timedelta(hours=12)):

                delta_t = (x[i+1]-x[i]).total_seconds()/1800
                units = int(delta_t)*3 + 4

                new_x.append(x[i])
                new_y.append(y[i])
                for j in range(units):
                    # Interpola as datas do intervalo
                    p1 = (-1, x[i].timestamp())
                    p2 = (units, x[i+1].timestamp())
                    new_x.append(datetime.fromtimestamp(Analysis.linearInterp(p1, p2, j)))
                    # Interpola os valores do intervalos
                    p1 = (-1, y[i+1])
                    p2 = (units, y[i])
                    new_y.append(Analysis.linearInterp(p1, p2, j))
        return (new_x, new_y)
    
    @staticmethod
    def dataAvg(progressBar, percentagePB, ini, end, pvs):

        if progressBar != None:
            progressBar.setMaximum(len(pvs))
            progressBar.setValue(0)

        signals = []; maxDatetimes = []; minDatetimes = []
        for i in range(len(pvs)):
            if pvs[i] not in Analysis.ignore:
                data = {}
                x, y, units = arc.pv_request(pvs[i], arc.datetimeToStr(ini), arc.datetimeToStr(end))
                if x != None and y != None:
                    x, y = Analysis.increaseResolution(x, y)
                    for j in range(len(x)):
                        x[j] = Analysis.changeDatetime(x[j])
                        if x[j] not in data.keys():
                            data[x[j]] = [y[j]-y[0]]
                        else:
                            data[x[j]].append(y[j]-y[0])
                    minDatetimes.append(x[0]); maxDatetimes.append(x[-1])
                    signals.append(data)
            if progressBar != None:
                progressBar.setValue(i)

        maxMinKey = max(minDatetimes)
        minMaxKey = min(maxDatetimes)

        keys = []
        for i in range(int((minMaxKey-maxMinKey)/timedelta(minutes=10))):
            keys.append(maxMinKey)
            maxMinKey += timedelta(minutes=10)

        x = []; y = []
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

        if progressBar != None:
            progressBar.setValue(len(pvs))
            
        print(units)
        return (x, y, units)

    @staticmethod
    def dataToDict(ini, end, dt, values):
        # Initializing the dictionary
        data = {}
        while ini <= end:
            data[ini] = []
            ini = ini + timedelta(minutes = 30)

        # Adding data to dictionary
        for i in range(len(dt)):
            for j in range(len(dt[i])):
                new_dt = Analysis.changeDatetime(dt[i][j])
                try:
                    """
                        The stored data is the temperature variation in
                        relation to the previous data
                    """
                    last = (j-1) if j > 0 else 0
                    data[new_dt].append(values[i][last] - values[i][j])
                except:
                    # The datetime is not in the range
                    pass
        return data
        
    @staticmethod
    def dictAvg(dictionary):
        for key in dictionary.keys():
            if len(dictionary[key]) > 0:
                dictionary[key] = sum(dictionary[key])/len(dictionary[key])
            else:
                dictionary[key] = None
        return dictionary

    @staticmethod
    def compressData(ini, dt, values):
        new_datetime = []
        new_values = []
        average = []
        i = 0
        
        while dt[i] <= ini:
            i += 1
        
        while i < len(dt):
            if(ini - timedelta(minutes = 15) <= dt[i] <= (ini + timedelta(minutes = 15))):
                average.append(values[i])
                i = i + 1
            else:
                new_datetime.append(ini)
                ini = ini + timedelta(minutes = 30)
                if len(average) > 0:
                    new_values.append(sum(average)/len(average))
                    average = []
                else:
                    new_values.append(values[i])
        
        return (new_datetime, new_values)

    @staticmethod
    def crossCorrelation(ini, dt_rf, rf, perimeter):

        dt_rf, rf = Analysis.compressData(ini, dt_rf, rf)

        #calculate cross correlation
        x = sm.tsa.stattools.ccf(rf, perimeter, adjusted=False)

        #calculate the time necessary to the best correlation
        units_to_best = np.where(x == max(x))[0][0]
        time_to_best = dt_rf[units_to_best] - dt_rf[0]

        ccf = (max(x)+1)*100/2

        return (time_to_best, ccf)

if __name__ == "__main__":
    ini = datetime(year = 2022, month = 3, day = 5)
    end = datetime(year = 2022, month = 5, day = 26)
    import matplotlib.pyplot as plt
    x,y,u=Analysis.dataAvg(ini, end, ["TU-03S:SS-Concrete-7AN:Temp-Mon", "TU-03S:SS-Concrete-9AN:Temp-Mon"])
    plt.plot(x, y)
    plt.show()
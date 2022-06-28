import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from analysis import Analysis
from archiver import Archiver as arc
from datetime import datetime, timedelta

class Perimeter():

    # Concrete Coefficient of Expansion
    alpha_concrete = 12e-6

    theta_sensors = [0.023, 0.338, 0.652, 1.411, 1.594, 
                     1.908, 2.223, 2.981, 3.165, 3.479, 
                     3.793, 4.552, 4.736, 5.050, 5.364,
                     6.123, 0.02]
    
    initial_radius = 85.460

    radius = [[85.460], [85.460], [85.460], [85.460], [85.460], 
              [85.460], [85.460], [85.460], [85.460], [85.460], 
              [85.460], [85.460], [85.460], [85.460], [85.460], 
              [85.460], [85.460]]

    # Fator de conversão RF -> metros:
    rf_to_meters = 864*3e8*(1/499665999 - 1/499666000)

    @staticmethod
    def linearExpansion(index, deltaTemp):
        alpha = Perimeter.alpha_concrete
        radius = Perimeter.radius[index][-1]
        expansion = alpha * radius * deltaTemp
        return expansion

    @staticmethod
    # Distance betweem two points in polar coordinates
    def pointToPoint(p1, p2):
        r_1, theta_1 = p1
        r_2, theta_2 = p2
        distance = math.sqrt(r_1**2 + r_2**2 - 2*r_1*r_2*math.cos(theta_1 - theta_2))
        return distance

    @staticmethod
    # Calc the perimeter based on the last radius data
    def calcPerimeter():
        r = Perimeter.radius
        perimeter = 0
        for i in range(len(r) - 1):
            r1 = r[i][-1]; t1 = Perimeter.theta_sensors[i]
            r2 = r[i+1][-1]; t2 = Perimeter.theta_sensors[i+1]
            perimeter += Perimeter.pointToPoint((r1, t1), (r2, t2))
        return perimeter

    @staticmethod
    def sensorPosition():
        # Setores com instrumentação do tipo simples
        setores_simples = [1, 2, 3, 6, 7, 8, 11, 12, 13, 16, 17, 18]
        arco = 2.00
        teta_simples = arco/Perimeter.initial_radius

        # Setores com instrumentação completa
        setores_completa = [5, 10, 15, 20]
        arco = 13.16
        teta_completa = arco/Perimeter.initial_radius

        # Cálculo das posições do sensores no prédio de acordo com a instrumentação
        teta_inicial = []
        for setor in range(1,21):
            if setor in setores_simples:
                teta_inicial.append(((setor - 1)/(20 - 1) * 19*math.pi/10) + teta_simples)
            elif setor in setores_completa:
                teta_inicial.append(((setor - 1)/(20 - 1) * 19*math.pi/10) + teta_completa)
        teta_inicial.append(teta_inicial[0])

        x1 = Perimeter.initial_radius * np.cos(teta_inicial)
        x2 = Perimeter.initial_radius * np.sin(teta_inicial)

        fig, ax = plt.subplots(1)
        ax.plot(x1, x2, "--o")
        ax.plot(0, 0, "ro")
        ax.set_aspect(1)
        plt.grid(linestyle='--')
        plt.title('Sensor position in the building')
        plt.savefig('avg-sensor-position.png', dpi=300)
        plt.show()

if __name__ == "__main__":
    # Poço Desligado (99.3%)
    ini = datetime(year = 2022, month = 2, day = 24)
    end = datetime(year = 2022, month = 3, day = 6)

    #ini = datetime(year = 2021, month = 8, day = 25)
    #end = datetime(year = 2021, month = 8, day = 29)

    #ini = datetime(year = 2021, month = 9, day = 15)
    #end = datetime(year = 2021, month = 9, day = 24)

    # Import data from Archiver
    tempVariation = {}
    pvs = arc.generate_concrete_pvs()

    setor_i = pvs[0][3:5]
    dt_sector = []; val_sector = []
    for i in range(len(pvs)):

        setor = pvs[i][3:5]
        if setor == setor_i:
            dict_sector = Analysis.dataToDict(ini, end, dt_sector, val_sector)
            avg_sector = Analysis.dictAvg(dict_sector)
            tempVariation[setor] = avg_sector
            dt_sector = []; val_sector = []

        dt, values, units = arc.pv_request(pvs[i], arc.datetimeToStr(ini), arc.datetimeToStr(end))
        dt_sector.append(dt)
        val_sector.append(values)
        print(i*100/len(pvs))
        

    print("OK")
    # Calculating the perimeter variation
    sectors = list(tempVariation.keys())
    perimeter = [Perimeter.calcPerimeter()]
    datetime_perimeter = [ini - timedelta(minutes = 5)]

    for dt in tempVariation[2].keys():

        for sector in sectors:
            if tempVariation[sector][dt] != None:
                index = sectors.index(sector)
                radius = Perimeter.radius[index][-1]
                deltaTemp = tempVariation[sector][dt]
                linearExpansion = Perimeter.linearExpansion(index, deltaTemp)
                newRadius = radius + linearExpansion
                Perimeter.radius[index].append(newRadius)

        perimeter.append(Perimeter.calcPerimeter())
        datetime_perimeter.append(dt)

    ####################### RF Frequency #######################

    # Getting the RF frequency (1 Hz -> 1 micro)
    dt_rf, val_rf = arc.pv_request("RF-Gen:GeneralFreq-RB", arc.datetimeToStr(ini), arc.datetimeToStr(end))
    val_rf = np.array(val_rf) * Perimeter.rf_to_meters

    perimeter = np.array(perimeter)

    # Plot around zero
    zero_perimeter = perimeter - perimeter.mean()
    zero_rf = val_rf - val_rf.mean()

    fig, ax = plt.subplots(figsize=(10,4))

    shiftTime, correlationFactor = Analysis.crossCorrelation(ini, dt_rf, zero_rf, zero_perimeter)

    datetime_perimeter = np.array(datetime_perimeter)
    lns1 = ax.plot(datetime_perimeter - timedelta(seconds=shiftTime.seconds), zero_perimeter*1e6, label="From Linear Expansion")
    ax_2 = ax.twinx()
    lns2 = ax_2.plot(dt_rf, zero_rf*1e6, "ro", markersize = 0.5, label="From RF Frequency")
    ax.set_ylabel(r"$\Delta\mu m$" + " - Linear Expansion", fontsize=12)
    ax_2.set_ylabel(r"$\Delta\mu m$" + " - RF Frequency", fontsize=12)
    ax_2.set_ylim([-200,250])
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d, %Y'))
    ax.set_xticks(np.arange(dt_rf[0], dt_rf[-1], timedelta(hours=48)))
    ax.title.set_text("Perimeter Variation - Water Well ON (Fast Cycle) | Cross-correlation factor: %.1f%% | Shift time: %dh" % (correlationFactor, shiftTime.seconds//3600))
    plt.show()
from scipy.interpolate import interp2d, griddata
import numpy as np

from teaspoon.readers import read_gtnp

if __name__ == "__main__":
    x = read_gtnp(r"C:\Users\Nick\Downloads\Borehole_864-SCH_5200-Dataset_1998-subset.csv")
    z = x.monthly()
    f = interp2d(z.long.dropna()['temperature_in_ground'].values.astype(float),
                z.long.dropna()['time'].values.astype(float),
                z.long.dropna()['depth'].values.astype(float))

    cleaned = z.long.dropna()
    cleaned['time'] = cleaned['time'].values.astype(float)
    points = cleaned.loc[:,['temperature_in_ground', 'time']].to_numpy()
    values = cleaned.loc[:,'depth'].values
    xi = np.zeros_like(points, dtype='float32') - 0.1
    xi[:,1] = points[:,1]
    xi = np.mgrid[-3:1:3j, 1:1:18728j]
    xi[:,1] = points[:,1]
    g = griddata(points, values, xi[1:1000:,:])

    np.interp()

    from matplotlib import pyplot as plt
    plt.plot(points[:,0], points[:,1], 'k.', ms=1)
    plt.show()
    def extract_isotherm(depths, temps, times, isotherm=0):
        """_summary_

        Parameters
        ----------
        depths : _type_
            _description_
        temps : _type_
            _description_
        times : _type_
            _description_
        isotherm : int, optional
            _description_, by default 0
        """
        if len(times) > 10000:
            print("too much data")
            return



import numpy as np

from .soa import StructureOfArrays

reflectivity_LUT = np.array([  # reflectivity look up table
    0.000, 0.010, 0.020, 0.030, 0.040, 0.050, 0.060, 0.070, 0.080,
    0.090, 0.100, 0.110, 0.120, 0.130, 0.140, 0.150, 0.160, 0.170,
    0.180, 0.190, 0.200, 0.210, 0.220, 0.230, 0.240, 0.250, 0.260,
    0.270, 0.280, 0.290, 0.300, 0.310, 0.320, 0.330, 0.340, 0.350,
    0.360, 0.370, 0.380, 0.390, 0.400, 0.410, 0.420, 0.430, 0.440,
    0.450, 0.460, 0.470, 0.480, 0.490, 0.500, 0.510, 0.520, 0.530,
    0.540, 0.550, 0.560, 0.570, 0.580, 0.590, 0.600, 0.610, 0.620,
    0.630, 0.640, 0.650, 0.660, 0.670, 0.680, 0.690, 0.700, 0.710,
    0.720, 0.730, 0.740, 0.750, 0.760, 0.770, 0.780, 0.790, 0.800,
    0.810, 0.820, 0.830, 0.840, 0.850, 0.860, 0.870, 0.880, 0.890,
    0.900, 0.910, 0.920, 0.930, 0.940, 0.950, 0.960, 0.970, 0.980,
    0.990, 1.000, 1.010, 1.020, 1.030, 1.040, 1.050, 1.060, 1.070,
    1.080, 1.090, 1.100, 1.110, 1.120, 1.130, 1.140, 1.150, 1.160,
    1.170, 1.180, 1.190, 1.200, 1.210, 1.220, 1.230, 1.240, 1.250,
    1.260, 1.270, 1.307, 1.345, 1.384, 1.424, 1.466, 1.509, 1.553,
    1.598, 1.644, 1.692, 1.741, 1.792, 1.844, 1.898, 1.953, 2.010,
    2.069, 2.129, 2.191, 2.254, 2.320, 2.388, 2.457, 2.529, 2.602,
    2.678, 2.756, 2.836, 2.919, 3.004, 3.091, 3.181, 3.274, 3.369,
    3.467, 3.568, 3.672, 3.779, 3.889, 4.002, 4.119, 4.239, 4.362,
    4.489, 4.620, 4.754, 4.892, 5.035, 5.181, 5.332, 5.488, 5.647,
    5.812, 5.981, 6.155, 6.334, 6.519, 6.708, 6.904, 7.105, 7.311,
    7.524, 7.743, 7.969, 8.201, 8.439, 8.685, 8.938, 9.198, 9.466,
    9.741, 10.025, 10.317, 10.617, 10.926, 11.244, 11.572, 11.909,
    12.255, 12.612, 12.979, 13.357, 13.746, 14.146, 14.558, 14.982,
    15.418, 15.866, 16.328, 16.804, 17.293, 17.796, 18.314, 18.848,
    19.396, 19.961, 20.542, 21.140, 21.755, 22.389, 23.040, 23.711,
    24.401, 25.112, 25.843, 26.595, 27.369, 28.166, 28.986, 29.830,
    30.698, 31.592, 32.511, 33.458, 34.432, 35.434, 36.466, 37.527,
    38.620, 39.744, 40.901, 42.092, 43.317, 44.578, 45.876, 47.211,
    48.586, 50.000], dtype=np.float32)

class Frame(StructureOfArrays):
    """3D points array.

    Attributes:
        timestamps
        x_raw
        y_raw
        z_raw
        positions (N*3)
        reflectivities
        reflectivities_raw
        channel_ids
        invalid
        saturated
        handle
    """
  
    def __init__(self, n=0):
        super().__init__(n)
        self.timestamps = np.zeros([n], dtype=np.uint64)
        self.x_raw = np.zeros([n], dtype=np.int16)
        self.y_raw = np.zeros([n], dtype=np.uint16)
        self.z_raw = np.zeros([n], dtype=np.int16)
        self.positions = np.zeros([n, 3], dtype=np.float32)
        self.reflectivities = np.zeros([n], dtype=np.float32)
        self.reflectivities_raw = np.zeros([n], dtype=np.uint8)
        self.channel_ids = np.zeros([n], dtype=np.uint8)
        self.flags = np.zeros([n], dtype=np.uint8)
        self.saturated = np.zeros([n], dtype=bool)
        self.low_snr = np.zeros([n], dtype=bool)
        self.frame_parity = np.zeros([n], dtype=bool)
        self.frame_boundary = np.zeros([n], dtype=bool)
        self.second_return = np.zeros([n], dtype=bool)
        self.invalid = np.zeros([n], dtype=bool)
        self.noise = np.zeros([n], dtype=bool)
        self.handle= np.zeros([1], dtype=np.uint64)

    def _finalize(self):
        CEPTON_POINT_SATURATED = 1 << 0
        CEPTON_POINT_LOW_SNR = 1 << 1
        CEPTON_POINT_FRAME_PARITY = 1 << 2
        CEPTON_POINT_FRAME_BOUNDARY = 1 << 3
        CEPTON_POINT_SECOND_RETURN = 1 << 4
        CEPTON_POINT_NO_RETURN = 1 << 5
        CEPTON_POINT_NOISE = 1 << 6

        np.multiply(np.stack([self.x_raw, self.y_raw, self.z_raw], 1), 0.005, out=self.positions)
        self.reflectivities[:] = reflectivity_LUT[self.reflectivities_raw]
        self.saturated[:] = np.bitwise_and(self.flags, CEPTON_POINT_SATURATED) != 0
        self.low_snr[:] = np.bitwise_and(self.flags, CEPTON_POINT_LOW_SNR) != 0
        self.frame_parity[:] = np.bitwise_and(self.flags, CEPTON_POINT_FRAME_PARITY) != 0
        self.frame_boundary[:] = np.bitwise_and(self.flags, CEPTON_POINT_FRAME_BOUNDARY) != 0
        self.second_return[:] = np.bitwise_and(self.flags, CEPTON_POINT_SECOND_RETURN) != 0
        self.invalid[:] = np.bitwise_and(self.flags, CEPTON_POINT_NO_RETURN) != 0
        self.noise[:] = np.bitwise_and(self.flags, CEPTON_POINT_NOISE) != 0
        
    @classmethod
    def _get_array_member_names(cls):
        return ['timestamps', 'x_raw', 'y_raw', 'z_raw', 'positions',
            'reflectivities', 'reflectivities_raw', 'channel_ids', 'saturated', 
            'low_snr', 'frame_parity', 'frame_boundary', 'second_return', 
            'invalid', 'noise', 'flags', 'handle']

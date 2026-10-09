import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.odr import ODR, Model, RealData


### power fit function for both ports (note: data is photon number which is proportional to power)
# Columns:
# 0 = Time; 1 = Motor 2 angle; 2 = Motor 1 angle; 3 = Wavelength; 4 = Power
[hwpV_ang, powerV] = np.loadtxt(
    "data_HWP_V.csv",
    delimiter=",",
    skiprows=1,
    #max_rows=4800,
    #usecols=(2, 4),
    unpack=True
)


[hwpH_ang, powerH] = np.loadtxt(
    "data_HWP_H.csv",
    delimiter=",",
    skiprows=1,
    #max_rows=4800,
    #usecols=(2, 4),
    unpack=True
)


theta = hwpH_ang

def power_both(beta, theta):
    PminH, PH, PminV, PV, theta0 = beta

    phase = np.deg2rad(2 * (theta - theta0))

    fitH = PminH + PH * np.cos(phase)**2
    fitV = PminV + PV * np.sin(phase)**2

    return np.vstack((fitH, fitV))


power_data = np.vstack((powerH, powerV))

data = RealData(
    theta,
    power_data,
    sx=0.05,
    sy=1e-6
)

odr = ODR(
    data,
    Model(power_both),
    beta0=[
        np.min(powerH),
        np.ptp(powerH),
        np.min(powerV),
        np.ptp(powerV),
        theta[np.argmax(powerH)]
    ]
)

output = odr.run()

PminH, PH, PminV, PV, theta0 = output.beta
PminH_err, PH_err, PminV_err, PV_err, theta0_err = output.sd_beta

theta0 = theta0 % 90
thetaV_max = (theta0 + 45) % 90

# Plot joint fit
theta_fit = np.linspace(
    np.min(hwpH_ang),
    np.max(hwpH_ang),
    2000
)

fit1, fit2 = power_both(output.beta, theta_fit)

plt.figure(figsize=(10, 5))

plt.plot(hwpH_ang, powerH, ".", label="Port 1 data")
plt.plot(theta_fit, fit1, "-", label="Port 1 joint fit")

plt.plot(hwpV_ang, powerV, ".", label="Port 2 data")
plt.plot(theta_fit, fit2, "-", label="Port 2 joint fit")

plt.xlabel("Motor 1 Angle (deg)")
plt.ylabel("Power (W)")
plt.title("Joint complementary PBS-output fit")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()

print("Port 1:")
print(f"Pmin          = {PminH*1000:.8e} ± {PminH_err*1000:.2e} mW")
print(f"P modulation  = {PH*1000:.8e} ± {PH_err*1000:.2e} mW")
print(f"theta_max     = {theta0:.6f} deg")

print("\nPort 2:")
print(f"Pmin          = {PminV*1000:.8e} ± {PminV_err*1000:.2e} mW")
print(f"P modulation  = {PV*1000:.8e} ± {PV_err*1000:.2e} mW")
print(f"theta_max     = {thetaV_max:.6f} deg")

print("\nShared parameters:")
print(f"theta0        = {theta0:.6f} ± {theta0_err:.6f} deg")
print("Stop reason:", output.stopreason)
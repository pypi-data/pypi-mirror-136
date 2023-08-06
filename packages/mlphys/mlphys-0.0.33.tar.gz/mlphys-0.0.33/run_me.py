import deepqis.Simulator.Distributions as dist
import deepqis.Simulator.Measurements as meas
import matplotlib.pyplot as plt
import deepqis.utils.Alpha_Measure as find_alpha
import deepqis.utils.Concurrence_Measure as find_con
import deepqis.utils.Purity_Measure as find_pm
import deepqis.network.inference as inference

bures = dist.Bures(qs=2).sample_dm(5)
tomo, tau = meas.Random_Measurements(qs=2).tomography_data(bures)
print(tomo.sum(axis=1))

pred_dm = inference.fit(tomo)
print(pred_dm.shape)
# Since we run in docker, there is not way to detect the actual cpus used by docker
# Had to manually set it
import sys
from time import time

import anndata as ad
import pandas as pd
from memory_profiler import memory_usage

import spatialtis as st

CPUs = int(sys.argv[1])
heat = False
K = 10
TIMES = 1000

dataset = ('Stereo-seq-MouseEmbryo', 'IMC-BreastCancer')
mature = ad.read_h5ad("data/E16-5.h5ad")
basel = ad.read_h5ad("data/IMC-scp-basel.h5ad")

st.Config.centroid_key = 'centroid'

nns_tb = dict(software=[],
              dataset=[],
              cpu_count=[],
              exec_time=[],
              exec_mem=[],
              )

cci_tb = dict(software=[],
              dataset=[],
              cpu_count=[],
              exec_time=[],
              exec_mem=[],
              )


def time_neighbors(data):
    s1 = time()
    st.find_neighbors(data, k=K)
    s2 = time()
    return s2 - s1


def time_na(data):
    s1 = time()
    st.cell_interaction(data, order=False, resample=TIMES)
    s2 = time()
    return s2 - s1


def time_autocorr(data):
    s1 = time()
    st.spatial_autocorr(data, method="moran_i")
    s2 = time()
    return s2 - s1


def time_all(data):
    s1 = time()
    st.find_neighbors(data, k=K)
    st.cell_interaction(data, order=False, resample=TIMES)
    s2 = time()
    return s2 - s1



mem_prof = dict(max_usage=True, multiprocess=True, retval=True)

# Test Stereo-seq data
st.Config.exp_obs = ['timepoint']
st.Config.cell_type_key = 'annotation'
nns_mem, nns_time = memory_usage((time_neighbors, (mature,)), **mem_prof)
print("Finished finding neighbor")
cci_mem, cci_time = memory_usage((time_na, (mature,)), **mem_prof)
print("Finished cell interaction")
st.Config.progress_bar = True
at_mem, at_time = memory_usage((time_autocorr, (mature,)), **mem_prof)
print("Finished spatial autocorr")
print(at_mem, at_time)

nns_tb['software'].append('SpatialTis')
nns_tb['dataset'].append(dataset[0])
nns_tb['exec_time'].append(nns_time)
nns_tb['exec_mem'].append(nns_mem)
nns_tb['cpu_count'].append(CPUs)

cci_tb['software'].append('SpatialTis')
cci_tb['dataset'].append(dataset[0])
cci_tb['exec_time'].append(cci_time)
cci_tb['exec_mem'].append(cci_mem)
cci_tb['cpu_count'].append(CPUs)

pd.DataFrame(nns_tb).to_csv(f"result/spatialtis_embryo_nns_{CPUs}core.csv", index=False)
pd.DataFrame(cci_tb).to_csv(f"result/spatialtis_embryo_cci_{CPUs}core.csv", index=False)


# Test IMC dataset, Only run when CPUS >= 8
# if CPUs >= 8:
#     st.Config.exp_obs = ['core']
#     st.Config.cell_type_key = 'cell_type'
#     multi_mem, multi_time = memory_usage((time_all, (basel,)), **mem_prof)
#
#     pd.DataFrame({
#         "software": ["SpatialTis"],
#         "dataset": [dataset[1]],
#         "cpu_count": [CPUs],
#         "exec_time": [multi_time],
#         "exec_mem": [multi_mem]
#     }).to_csv(f"result/spatialtis_multi_all_{CPUs}cores.csv", index=False)

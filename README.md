# HighThroughputGW
Package for automatic GW calculations using abinit.

dependencies
------------
The main dependence of HTGW is [AbiPy](https://github.com/abinit/abipy/ "AbiPy git repository"). HTGW does not introduce further dependencies that are not already a dependecy of AbiPy.

preparation
-----------
In order to prepare automatic gw flows through the AbiPy machinery, the manager.yml needs to be present and properly configured. The AbiPy package provides a long list of [examples](https://github.com/abinit/abipy/tree/master/abipy/data/managers "AbiPy manager examples").
To run actual calculations a properly installed version of [Abinit](https://www.abinit.org) is also requiered. Note that some features of AbiPy, e.g., configuring the opinal paralelization require also a serial version of Abinit to be present in the path.

usage
-----


Further details are provided in [Automation methodologies and large-scale validation for GW: Towards high-throughput GW calculations](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.96.155207) [free preprint](https://arxiv.org/abs/1709.07349).

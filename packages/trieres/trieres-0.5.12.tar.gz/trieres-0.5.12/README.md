# trieres
This is a python module enabling the remote execution of accelerated functions on the [cloudFPGA platform](https://www.zurich.ibm.com/cci/cloudFPGA/).

## Workflow

```
git clone --depth 1 --recursive git@github.com:cloudFPGA/trieres.git
cd trieres  
make env
source venv/bin/activate
make genlib
make dist 
make upload
```

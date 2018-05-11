# pyubx

A bunch of python utilities to make automating verilog (and VHDL) easier. Separated to provide the functionality in importable modules to be extended/customised

## Getting Started

Clone the repo to get the scripts, callable utilities are at the top level and include:

* make_wrapper
* verilog_utiles

### Prerequisites

The idea here is that this should be a self contained lib without needing anything else installed... so there's none.


### Installing

A step by step series of examples that tell you have to get a development env running


```
git clone https://github.com/padraig.ryan/pyubx
```

## Running the tests

There's some regression tests available. To run regression:
```
make tests
```

### And coding style tests

Uses 4 spaces and tries to be PEP-8 compliant

## Contributing

Padraig Ryan

## Authors

* **Padraig Ryan** - *Initial work* - [Padraig Ryan](https://github.com/padraig.ryan)

(https://github.com/padraig.ryan/pyubx) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Still To Do:

Create a utils for each of the types

<ol>
<li> rtl_utils.py
<li> vcd_utils.py
<li> phy_utils.py
<li> hal_utils.py
<LI> uvm_utils.py
</ol>

Should this include all the little tools or alternatively have the tools in <type>_<tool>.py?

### Top level Utils
#### rtl_utils
* Move the make_wrapper function into rtl_utils.py
* Move the inst_mod into the rtl/utils and add it to rtl_utils.py
* More VHDL support
* Test Cases to add
** Create a module, write to file, read back in and compare with original.

#### vcd_utils
* Move the latest VCD scripts into this workspace
* Split out the tools
#### phy_utils
#### hal_utils
#### Verilog Utils


### Importable modules


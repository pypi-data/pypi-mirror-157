# python-gatenlp-ml-tner

Token classification training and application using transformers via the tner package.

See: https://github.com/asahi417/tner / https://pypi.org/project/tner/

### Installation:

* For now this package does NOT require the packages 
  it depends on in order to avoid dependency hell. See below 
  for how to install the required packages.
* create a new environment 
  (e.g. `conda create -y -n gatenlp-tner python=3.7`) 
  and activate it
* install the PyTorch version compatible with your machine 
  see [PyTorch Installation](https://pytorch.org/get-started/locally/)
* install tner:
    * latest release: `python -m pip install -U tner`
    * or latest code from github `python -m pip install -U git+https://github.com/asahi417/tner.git`
* install gatenlp, e.g.: `python -m pip install -U gatenlp[all]`




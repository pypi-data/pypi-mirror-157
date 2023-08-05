## Introduction

RH Ceph QE Focus Groups mainly contribute test coverage features in the cephci repository. Test automation requires methods that could execute a specific workflow, verify the result and post this information to the user. At present, a QE engineer creates methods inside their own workspace. The implemented method has a high probability that it is required by another team. For example: a method to restart a specific Ceph Daemon.

These methods are generally development keeping the FGs objectives in mind. This makes it less attractive if another team wants to reuse them. This causes an explosion in the methods being create in the repository.

# Getting Started 

RHCS QE SDK for Python can be installed from Source, Pypi installation methods.

   ## From Source
   ```bash
   $ git clone https://gitlab.cee.redhat.com/rhcs-qe/rhcs-qe-sdk.git
   $ cd rhcs-qe-sdk 
   ```
   ```python
   $ python setup.py install --user  # to install in the user directory (~/.local)
   ```
   ```bash
   $ sudo python setup.py install    # to install globally
   ```
   
   ## Or using PIP:
   ```bash
   $ git clone https://gitlab.cee.redhat.com/rhcs-qe/rhcs-qe-sdk.git
   $ cd rhcs-qe-sdk 
   ```
   ```python
   $ pip install . 
   ```   
   
   ## From Pypi
   ```bash
   $ git clone https://gitlab.cee.redhat.com/rhcs-qe/rhcs-qe-sdk.git
   $ cd rhcs-qe-sdk
   ```
   ```python
   $ pip install CephQeSdk
   ```

## Install rhcs-qe-sdk's dependencies
   ```python
   $ pip install -r requirements.txt
   ```

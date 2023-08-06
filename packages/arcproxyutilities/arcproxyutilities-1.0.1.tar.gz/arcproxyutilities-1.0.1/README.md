# Python package for ArcProxyUtilities #
This package contains the utilites which can be leveraged by azure cli extensions for the proxy command of provisioned clusters.

### How to use ###
Import this package in the cli extension and make sure to add this as a dependency in the respective setup.py file by specifying the latest version number. Configure the proxy command to call client_side_proxy_wrapper() of this package with the required parameters.

### CSP Port number usage guidelines ####
While passing the csp port number in client_side_proxy_wrapper() from cli extension, make sure that you are passing a port number which is not used by other cli extensions. This will enable users to run multiple instances of proxy in future. 

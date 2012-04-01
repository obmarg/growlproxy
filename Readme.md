Growl Proxy
===

Growl proxy is a simple proxy for the GNTP protocol.  It is written in python with a web interface, as it is designed to run in the background on headless computers.

The basic functionality is written and partially tested, but as it is a work in progress, things may not work as expected/at all.

The latest version of growlproxy can be obtained from [it's github page](https://github.com/obmarg/growlproxy).

Setup
---
Growl proxy depends on the following python modules

* Jinja2
* Flask
* sqlalchemy
* gntp
* mox (for the tests)

These can be installed easily (assuming pip is setup) with the following command:

```
pip install Jinja2 Flask sqlalchemy gntp mox
```

Then, the latest version of growlproxy can be obtained using

```
git clone git://github.com/obmarg/growlproxy.git
```

At present, the `growlproxyrun.py` and `growlproxyui.py` files should be used to start the proxy itself and the user interface respectively.

In the future, a unified python script to run both of these will be provided as well as a proper setup.py, but for now this is the recommended method.



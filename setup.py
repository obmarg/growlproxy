from setuptools import setup, find_packages

setup(
        name = "growlproxy",
        version = "0.1",
        packages = find_packages(),
        scripts = [ 'growlproxyui.py', 'growlproxy.py' ],

        #TODO: Improve this dependency list
        #       Check things missing, maybe remove mox
        install_requires = [
            'gntp>=0.6',
            'mox>=0.5.3',
            'jinja2>=2.6',
            'WTForms>=0.6.3',
            'Twisted>=11.1.0',
            'SQLAlchemy>=0.7.5',
            'FlashWTF>=0.5.2',
            'Flask>=0.8'
            ],

        author = "Graeme Coupar",
        author_email = "grambo@grambo.me.uk",
        description = "A simple proxy server for growl",
        #TODO: Decide on license (am I even allowed to use GPL w/ other libs)
        license = "GPL",
        keywords = "growl proxy notifications forward",
        url = "http://github.com/obmarg"
        )


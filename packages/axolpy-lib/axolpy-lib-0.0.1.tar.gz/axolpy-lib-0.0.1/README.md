# axolpy-lib, the Axolotl Library in Python
This is the library and useful scripts of the Axolotl series in 
Python. The implementation of it aims at providing a handy all-in-one 
package for writing useful applications.

## Install axolpy-lib
```
pip install axolpy-lib
```

## Run test
Run pytest
```
pytest
```

## Build axolpy-lib package
To build with wheel:
```
python -m build
```

You will see output like this:
```
* Creating venv isolated environment...
* Installing packages in isolated environment... (setuptools>=42, wheel)
* Getting dependencies for sdist...
running egg_info
writing src/axolpy_lib.egg-info/PKG-INFO
writing dependency_links to src/axolpy_lib.egg-info/dependency_links.txt
writing requirements to src/axolpy_lib.egg-info/requires.txt
writing top-level names to src/axolpy_lib.egg-info/top_level.txt
package init file 'src/axolpy/__init__.py' not found (or not a regular file)
reading manifest file 'src/axolpy_lib.egg-info/SOURCES.txt'
adding license file 'LICENSE.md'
writing manifest file 'src/axolpy_lib.egg-info/SOURCES.txt'
* Building sdist...
running sdist
running egg_info
writing src/axolpy_lib.egg-info/PKG-INFO
writing dependency_links to src/axolpy_lib.egg-info/dependency_links.txt
writing requirements to src/axolpy_lib.egg-info/requires.txt
writing top-level names to src/axolpy_lib.egg-info/top_level.txt
package init file 'src/axolpy/__init__.py' not found (or not a regular file)
reading manifest file 'src/axolpy_lib.egg-info/SOURCES.txt'
adding license file 'LICENSE.md'
writing manifest file 'src/axolpy_lib.egg-info/SOURCES.txt'
running check
creating axolpy-lib-0.0.1
creating axolpy-lib-0.0.1/src
creating axolpy-lib-0.0.1/src/axolpy
creating axolpy-lib-0.0.1/src/axolpy/bitbucket
creating axolpy-lib-0.0.1/src/axolpy/configuration
creating axolpy-lib-0.0.1/src/axolpy/logging
creating axolpy-lib-0.0.1/src/axolpy/solidity
creating axolpy-lib-0.0.1/src/axolpy/util
creating axolpy-lib-0.0.1/src/axolpy/util/collectionfunctions
creating axolpy-lib-0.0.1/src/axolpy/util/helper
creating axolpy-lib-0.0.1/src/axolpy_lib.egg-info
copying files to axolpy-lib-0.0.1...
copying LICENSE.md -> axolpy-lib-0.0.1
copying README.md -> axolpy-lib-0.0.1
copying pyproject.toml -> axolpy-lib-0.0.1
copying setup.cfg -> axolpy-lib-0.0.1
copying setup.py -> axolpy-lib-0.0.1
copying src/axolpy/bitbucket/__init__.py -> axolpy-lib-0.0.1/src/axolpy/bitbucket
copying src/axolpy/configuration/__init__.py -> axolpy-lib-0.0.1/src/axolpy/configuration
copying src/axolpy/logging/__init__.py -> axolpy-lib-0.0.1/src/axolpy/logging
copying src/axolpy/solidity/__init__.py -> axolpy-lib-0.0.1/src/axolpy/solidity
copying src/axolpy/util/__init__.py -> axolpy-lib-0.0.1/src/axolpy/util
copying src/axolpy/util/types.py -> axolpy-lib-0.0.1/src/axolpy/util
copying src/axolpy/util/collectionfunctions/__init__.py -> axolpy-lib-0.0.1/src/axolpy/util/collectionfunctions
copying src/axolpy/util/helper/__init__.py -> axolpy-lib-0.0.1/src/axolpy/util/helper
copying src/axolpy/util/helper/string.py -> axolpy-lib-0.0.1/src/axolpy/util/helper
copying src/axolpy_lib.egg-info/PKG-INFO -> axolpy-lib-0.0.1/src/axolpy_lib.egg-info
copying src/axolpy_lib.egg-info/SOURCES.txt -> axolpy-lib-0.0.1/src/axolpy_lib.egg-info
copying src/axolpy_lib.egg-info/dependency_links.txt -> axolpy-lib-0.0.1/src/axolpy_lib.egg-info
copying src/axolpy_lib.egg-info/requires.txt -> axolpy-lib-0.0.1/src/axolpy_lib.egg-info
copying src/axolpy_lib.egg-info/top_level.txt -> axolpy-lib-0.0.1/src/axolpy_lib.egg-info
Writing axolpy-lib-0.0.1/setup.cfg
Creating tar archive
removing 'axolpy-lib-0.0.1' (and everything under it)
* Building wheel from sdist
* Creating venv isolated environment...
* Installing packages in isolated environment... (setuptools>=42, wheel)
* Getting dependencies for wheel...
running egg_info
writing src/axolpy_lib.egg-info/PKG-INFO
writing dependency_links to src/axolpy_lib.egg-info/dependency_links.txt
writing requirements to src/axolpy_lib.egg-info/requires.txt
writing top-level names to src/axolpy_lib.egg-info/top_level.txt
package init file 'src/axolpy/__init__.py' not found (or not a regular file)
reading manifest file 'src/axolpy_lib.egg-info/SOURCES.txt'
adding license file 'LICENSE.md'
writing manifest file 'src/axolpy_lib.egg-info/SOURCES.txt'
* Installing packages in isolated environment... (wheel)
* Building wheel...
running bdist_wheel
running build
running build_py
package init file 'src/axolpy/__init__.py' not found (or not a regular file)
creating build
creating build/lib
creating build/lib/axolpy
creating build/lib/axolpy/configuration
copying src/axolpy/configuration/__init__.py -> build/lib/axolpy/configuration
creating build/lib/axolpy/util
copying src/axolpy/util/__init__.py -> build/lib/axolpy/util
copying src/axolpy/util/types.py -> build/lib/axolpy/util
creating build/lib/axolpy/solidity
copying src/axolpy/solidity/__init__.py -> build/lib/axolpy/solidity
creating build/lib/axolpy/bitbucket
copying src/axolpy/bitbucket/__init__.py -> build/lib/axolpy/bitbucket
creating build/lib/axolpy/logging
copying src/axolpy/logging/__init__.py -> build/lib/axolpy/logging
creating build/lib/axolpy/util/collectionfunctions
copying src/axolpy/util/collectionfunctions/__init__.py -> build/lib/axolpy/util/collectionfunctions
creating build/lib/axolpy/util/helper
copying src/axolpy/util/helper/__init__.py -> build/lib/axolpy/util/helper
copying src/axolpy/util/helper/string.py -> build/lib/axolpy/util/helper
running egg_info
writing src/axolpy_lib.egg-info/PKG-INFO
writing dependency_links to src/axolpy_lib.egg-info/dependency_links.txt
writing requirements to src/axolpy_lib.egg-info/requires.txt
writing top-level names to src/axolpy_lib.egg-info/top_level.txt
reading manifest file 'src/axolpy_lib.egg-info/SOURCES.txt'
adding license file 'LICENSE.md'
writing manifest file 'src/axolpy_lib.egg-info/SOURCES.txt'
installing to build/bdist.macosx-10.9-x86_64/wheel
running install
running install_lib
creating build/bdist.macosx-10.9-x86_64
creating build/bdist.macosx-10.9-x86_64/wheel
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy/configuration
copying build/lib/axolpy/configuration/__init__.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/configuration
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy/util
copying build/lib/axolpy/util/__init__.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/util
copying build/lib/axolpy/util/types.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/util
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy/util/collectionfunctions
copying build/lib/axolpy/util/collectionfunctions/__init__.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/util/collectionfunctions
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy/util/helper
copying build/lib/axolpy/util/helper/__init__.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/util/helper
copying build/lib/axolpy/util/helper/string.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/util/helper
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy/solidity
copying build/lib/axolpy/solidity/__init__.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/solidity
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy/bitbucket
copying build/lib/axolpy/bitbucket/__init__.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/bitbucket
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy/logging
copying build/lib/axolpy/logging/__init__.py -> build/bdist.macosx-10.9-x86_64/wheel/axolpy/logging
running install_egg_info
Copying src/axolpy_lib.egg-info to build/bdist.macosx-10.9-x86_64/wheel/axolpy_lib-0.0.1-py3.10.egg-info
running install_scripts
adding license file "LICENSE.md" (matched pattern "LICEN[CS]E*")
creating build/bdist.macosx-10.9-x86_64/wheel/axolpy_lib-0.0.1.dist-info/WHEEL
creating '/xxxxxxxx/axolpy-lib/dist/tmpnwcd556u/axolpy_lib-0.0.1-py3-none-any.whl' and adding 'build/bdist.macosx-10.9-x86_64/wheel' to it
adding 'axolpy/bitbucket/__init__.py'
adding 'axolpy/configuration/__init__.py'
adding 'axolpy/logging/__init__.py'
adding 'axolpy/solidity/__init__.py'
adding 'axolpy/util/__init__.py'
adding 'axolpy/util/types.py'
adding 'axolpy/util/collectionfunctions/__init__.py'
adding 'axolpy/util/helper/__init__.py'
adding 'axolpy/util/helper/string.py'
adding 'axolpy_lib-0.0.1.dist-info/LICENSE.md'
adding 'axolpy_lib-0.0.1.dist-info/METADATA'
adding 'axolpy_lib-0.0.1.dist-info/WHEEL'
adding 'axolpy_lib-0.0.1.dist-info/top_level.txt'
adding 'axolpy_lib-0.0.1.dist-info/RECORD'
removing build/bdist.macosx-10.9-x86_64/wheel
Successfully built axolpy-lib-0.0.1.tar.gz and axolpy_lib-0.0.1-py3-none-any.whl
```

---
#### See more  
1. [axolpy-cli](https://github.com/tchiunam/axolpy-cli) for using Axolpy in command line

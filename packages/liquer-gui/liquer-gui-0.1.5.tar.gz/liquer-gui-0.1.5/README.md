# LiQuer GUI

This project aims provide a more powerful user interface to the [LiQuer](https://orest-d.github.io/liquer/) framework.

## Install

Assuming you have a LiQuer system set up, you can add Pointcloud viewer by

```
pip install liquer-gui
```

In the code, when importing LiQuer command modules, use

```python
import liquer_gui
```

This will mount assets of the GUI into the LiQuer store under web/gui.
Once the liquer server is started, the webapp will be accessible under

```
http://127.0.0.1:5000/liquer/web/gui
```

See e.g. *server.py* in [examples](https://github.com/orest-d/liquer-gui/tree/master/liquer-gui/examples).

## Building from source

First install the dependencies:

```
npm install
```

Webapp cab be compiled from sources with the script [build_liquer_gui.sh](https://github.com/orest-d/liquer-gui/blob/master/build_liquer_gui.sh):

```
bash buils_liquer_gui.sh
```

# News

- 2021-11-28 - v0.0.1  - initial release
- 2021-11-28 - v0.0.2  - improving directory view
- 2021-11-28 - v0.0.3  - fixes and remove data from recipes
- 2022-01-03 - v0.1.0  - many enhancements, first relatively usable release
- 2022-01-12 - v0.1.4  - bugfixes, experimental syntax highlighting editor for yaml
- 2022-01-25 - v0.1.5  - minor enhancements, fixing a faulty release

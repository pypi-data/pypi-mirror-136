# tkdialog

A wrapper library to use tkinter dialogs easily.

## Usage

```python
import tkdialog

# make open dialog
filename = tkdialog.open_dialog()

# make saveas saveas_dialog
filename = tkdialog.open_dialog()

# open a pickled file with file selector
obj = tkdialog.load_pickle_with_dialog()

# pickle an object with save dialog
dat = {'x': 100, 'y': '01234'}
tkdialog.dump_pickle_with_dialog(dat)
```

## LICENSE

MIT, see [LICENSE](LICENSE)


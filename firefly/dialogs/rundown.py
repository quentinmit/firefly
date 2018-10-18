from firefly import *

__all__ = ["PlaceholderDialog", "SubclipSelectDialog"]


class PlaceholderDialog(QDialog):
    def __init__(self,  parent, meta):
        super(PlaceholderDialog, self).__init__(parent)
        self.setWindowTitle("Rundown placeholder")
        item_role = meta.get("item_role", "placeholder")

        self.ok = False

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.addWidget(ToolBarStretcher(toolbar))

        action_accept = QAction(QIcon(pix_lib["accept"]), 'Accept changes', self)
        action_accept.setShortcut('Ctrl+S')
        action_accept.triggered.connect(self.on_accept)
        toolbar.addAction(action_accept)

        keys = []
        for k in ["title", "subtitle", "description", "color", "duration"]: #TODO
            if k in meta:
                keys.append([k, {"default": meta[k]}])

        self.form = MetaEditor(parent, keys)
        for k in keys:
            if meta_types[k[0]]["class"] == SELECT:
                self.form.inputs[k[0]].auto_data(meta_types[k[0]])
            k = k[0]
            self.form[k] = meta[k]

        layout = QVBoxLayout()
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.form, 1)
        self.setLayout(layout)

        self.setModal(True)
        self.setMinimumWidth(400)

    @property
    def meta(self):
        return self.form.meta

    def on_accept(self):
        self.ok = True
        self.close()


class SubclipSelectDialog(QDialog):
    def __init__(self,  parent, asset):
        super(SubclipSelectDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Select {} subclip to use".format(asset))
        self.ok = False
        self.asset = asset
        self.subclips = asset.meta.get("subclips", [])
        self.subclips.sort(key=lambda x: x["mark_in"])

        layout = QVBoxLayout()

        btn = QPushButton("Entire clip")
        btn.clicked.connect(functools.partial(self.on_submit, -1 ))
        layout.addWidget(btn)

        btn = QPushButton("All subclips")
        btn.clicked.connect(functools.partial(self.on_submit, -2 ))
        layout.addWidget(btn)

        for i, subclip in enumerate(self.subclips):
            btn = QPushButton("[{} - {}] {}".format(
                    s2tc(subclip["mark_in"]),
                    s2tc(subclip["mark_out"]),
                    subclip["title"],
                ))
            btn.setStyleSheet("font: monospace; text-align: left;")
            btn.clicked.connect(functools.partial(self.on_submit, i))
            layout.addWidget(btn)

        self.setLayout(layout)


    def on_submit(self, subclip):
        self.result = []

        if subclip == -1:
            self.result = [{
                    "mark_in" : self.asset["mark_in"],
                    "mark_out" : self.asset["mark_out"],
                }]

        elif subclip == -2:
            for sdata in self.subclips:
                self.result.append({
                        "mark_in" : sdata["mark_in"],
                        "mark_out" : sdata["mark_out"],
                        "title" : "{} ({})".format(self.asset["title"], sdata["title"])
                    })

        elif subclip >= 0:
            self.result = [{
                    "mark_in" : self.subclips[subclip]["mark_in"],
                    "mark_out" : self.subclips[subclip]["mark_out"],
                    "title" : "{} ({})".format(self.asset["title"], self.subclips[subclip]["title"])
                }]
        self.ok = True
        self.close()

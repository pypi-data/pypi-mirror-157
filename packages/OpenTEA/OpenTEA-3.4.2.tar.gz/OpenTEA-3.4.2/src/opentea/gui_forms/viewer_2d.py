
from tkinter import ttk

from neverd.objects import GeometricCanvas
from neverd.menus import DefaultMenubar as CanvasMenubar


def add_viewer_2d(otroot, obj_name, schema):
    # TODO: check for filename?
    # TODO: need to connect button

    title = schema.get('title', "2D dialog")
    width = schema.get('width', 800)
    height = schema.get('height', 600)

    view2d_fr = ttk.Frame(otroot.notebook, name=title)
    otroot.notebook.add(view2d_fr, text=title)

    canvas = GeometricCanvas(view2d_fr, width=width, height=height)
    canvas.pack(fill='both', expand=True)

    frame = ttk.Frame(view2d_fr)
    button = ttk.Button(frame, text='Validate')
    button.pack()

    frame.pack(side='right')

    # TODO: probably needs to be adapted
    canvas.menubar = CanvasMenubar(canvas)

    # TODO: return app instead?
    return canvas

__version__ = '0.1'


def _svg_parse_(path):
    import re
    import numpy as np

    from matplotlib.path import Path

    commands = {'M': Path.MOVETO,
                'L': Path.LINETO,
                'Q': Path.CURVE3,
                'C': Path.CURVE4,
                'Z': Path.CLOSEPOLY}
    vertices = []
    codes = []
    cmd_values = re.split("([A-Za-z])", path)[1:]  # Split over commands.
    for cmd, values in zip(cmd_values[::2], cmd_values[1::2]):
        # Numbers are separated either by commas, or by +/- signs (but not at
        # the beginning of the string).
        if cmd.upper() in ['M', 'L', 'Q', 'C']:
            points = [e.split(',') for e in values.split(' ') if e != '']
            points = [list(map(float, each)) for each in points]
        else:
            points = [(0., 0.)]
        points = np.reshape(points, (-1, 2))
        # if cmd.islower():
        #    points += vertices[-1][-1]
        for i in range(0, len(points)):
            codes.append(commands[cmd.upper()])
        vertices.append(points)
    return np.array(codes), np.concatenate(vertices)


def _add_colorbar_(ax, cmap, norm, ec, labelsize, ylabel):
    import matplotlib
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='1%', pad=1)

    cb1 = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap,
                                           norm=norm,
                                           orientation='vertical',
                                           ticklocation='left')
    cb1.ax.tick_params(labelcolor=ec, labelsize=labelsize)
    cb1.ax.set_ylabel(ylabel, color=ec, fontsize=labelsize)


def _render_data_(data, wd, cmap, norm, ax, edgecolor):
    import os.path as op
    import matplotlib.patches as patches
    from matplotlib.path import Path
    for k, v in data.items():
        fp = op.join(wd, k)
        if op.isfile(fp):
            p = open(fp).read()
            codes, verts = _svg_parse_(p)
            path = Path(verts, codes)
            c = cmap(norm(v))
            ax.add_patch(patches.PathPatch(path, facecolor=c,
                                           edgecolor=edgecolor, lw=1))
        else:
            # print('%s not found' % fp)
            pass


def _create_figure_(files, figsize, background, title, fontsize, edgecolor):
    import numpy as np
    import matplotlib.pyplot as plt

    codes, verts = _svg_parse_(' '.join(files))

    xmin, ymin = verts.min(axis=0) - 1
    xmax, ymax = verts.max(axis=0) + 1
    yoff = 0
    ymin += yoff
    verts = np.array([(x, y + yoff) for x, y in verts])

    fig = plt.figure(figsize=figsize, facecolor=background)
    ax = fig.add_axes([0, 0, 1, 1], frameon=False, aspect=1,
                      xlim=(xmin, xmax),  # centering
                      ylim=(ymax, ymin),  # centering, upside down
                      xticks=[], yticks=[])  # no ticks
    ax.set_title(title, fontsize=fontsize, y=1.03, x=0.55, color=edgecolor)
    return ax


def _render_regions_(files, ax, facecolor, edgecolor):
    from matplotlib.path import Path
    import matplotlib.patches as patches

    codes, verts = _svg_parse_(' '.join(files))
    path = Path(verts, codes)

    ax.add_patch(patches.PathPatch(path, facecolor=facecolor,
                                   edgecolor=edgecolor, lw=1))


def _get_cmap_(cmap, values, vminmax=[]):
    import matplotlib

    cmap = matplotlib.cm.get_cmap(cmap)
    if vminmax == []:
        vmin, vmax = min(values), max(values)
    else:
        vmin, vmax = vminmax
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    return cmap, norm


def plot_dk(data, cmap='Spectral', background='k', edgecolor='w', ylabel='',
             figsize=(15, 15), bordercolor='w', vminmax=[], title='',
             fontsize=15):
    """Plot cortical ROI data based on a Desikan-Killiany (DK) parcellation.

    Parameters
    ----------
    data : dict
            Data to be plotted. Should be passed as a dictionary where each key
            refers to a region from the cortical Desikan-Killiany atlas. The
            full list of applicable regions can be found in the folder
            ggseg/data/dk.
    cmap : matplotlib colormap, optional
            The colormap for specified image.
            Default='Spectral'.
    vminmax : list, optional
            Lower and upper bound for the colormap, passed to matplotlib.colors.Normalize
    background : matplotlib color, if not provided, defaults to black
    edgecolor : matplotlib color, if not provided, defaults to white
    bordercolor : matplotlib color, if not provided, defaults to white
    ylabel : str, optional
            Label to display next to the colorbar
    figsize : list, optional
            Dimensions of the final figure, passed to matplotlib.pyplot.figure
    title : str, optional
            Title displayed above the figure, passed to matplotlib.axes.Axes.set_title
    fontsize: int, optional
            Relative font size for all elements (ticks, labels, title)
    """
    import matplotlib.pyplot as plt
    import os.path as op
    from glob import glob
    import ggseg

    wd = op.join(op.dirname(ggseg.__file__), 'data', 'dk')

    # A figure is created by the joint dimensions of the whole-brain outlines
    whole_reg = ['lateral_left', 'medial_left', 'lateral_right',
                 'medial_right']
    files = [open(op.join(wd, e)).read() for e in whole_reg]
    ax = _create_figure_(files, figsize, background, title, fontsize, edgecolor)

    # Each region is outlined
    reg = glob(op.join(wd, '*'))
    files = [open(e).read() for e in reg]
    _render_regions_(files, ax, bordercolor, edgecolor)

    # For every region with a provided value, we draw a patch with the color
    # matching the normalized scale
    cmap, norm = _get_cmap_(cmap, data.values(), vminmax=vminmax)
    _render_data_(data, wd, cmap, norm, ax, edgecolor)

    # DKT regions with no provided values are rendered in gray
    data_regions = list(data.keys())
    dkt_regions = [op.splitext(op.basename(e))[0] for e in reg]
    NA = set(dkt_regions).difference(data_regions).difference(whole_reg)
    files = [open(op.join(wd, e)).read() for e in NA]
    _render_regions_(files, ax, 'gray', edgecolor)

    # A colorbar is added
    _add_colorbar_(ax, cmap, norm, edgecolor, fontsize*0.75, ylabel)

    plt.show()


def plot_jhu(data, cmap='Spectral', background='k', edgecolor='w', ylabel='',
             figsize=(17, 5), bordercolor='w', vminmax=[], title='',
             fontsize=15):
    """Plot WM ROI data based on the Johns Hopkins University (JHU) white
    matter atlas.

    Parameters
    ----------
    data : dict
            Data to be plotted. Should be passed as a dictionary where each key
            refers to a region from the Johns Hopkins University white Matter
            atlas. The full list of applicable regions can be found in the
            folder ggseg/data/jhu.
    cmap : matplotlib colormap, optional
            The colormap for specified image.
            Default='Spectral'.
    vminmax : list, optional
            Lower and upper bound for the colormap, passed to matplotlib.colors.Normalize
    background : matplotlib color, if not provided, defaults to black
    edgecolor : matplotlib color, if not provided, defaults to white
    bordercolor : matplotlib color, if not provided, defaults to white
    ylabel : str, optional
            Label to display next to the colorbar
    figsize : list, optional
            Dimensions of the final figure, passed to matplotlib.pyplot.figure
    title : str, optional
            Title displayed above the figure, passed to matplotlib.axes.Axes.set_title
    fontsize: int, optional
            Relative font size for all elements (ticks, labels, title)
    """

    import matplotlib.pyplot as plt
    import ggseg
    import os.path as op
    from glob import glob

    wd = op.join(op.dirname(ggseg.__file__), 'data', 'jhu')

    # A figure is created by the joint dimensions of the whole-brain outlines
    whole_reg = ['NA']
    files = [open(op.join(wd, e)).read() for e in whole_reg]
    ax = _create_figure_(files, figsize, background, title, fontsize, edgecolor)

    # Each region is outlined
    reg = glob(op.join(wd, '*'))
    files = [open(e).read() for e in reg]
    _render_regions_(files, ax, bordercolor, edgecolor)

    # For every region with a provided value, we draw a patch with the color
    # matching the normalized scale
    cmap, norm = _get_cmap_(cmap, data.values(), vminmax=vminmax)
    _render_data_(data, wd, cmap, norm, ax, edgecolor)

    # JHU regions with no provided values are rendered in gray
    NA = ['CSF']
    files = [open(op.join(wd, e)).read() for e in NA]
    _render_regions_(files, ax, 'gray', edgecolor)

    # A colorbar is added
    _add_colorbar_(ax, cmap, norm, edgecolor, fontsize*0.75, ylabel)

    plt.show()


def plot_aseg(data, cmap='Spectral', background='k', edgecolor='w', ylabel='',
              figsize=(15, 5), bordercolor='w', vminmax=[],
              title='', fontsize=15):
    """Plot subcortical ROI data based on the FreeSurfer `aseg` atlas

    Parameters
    ----------
    data : dict
            Data to be plotted. Should be passed as a dictionary where each key
            refers to a region from the FreeSurfer `aseg` atlas. The full list
            of applicable regions can be found in the folder ggseg/data/aseg.
    cmap : matplotlib colormap, optional
            The colormap for specified image.
            Default='Spectral'.
    vminmax : list, optional
            Lower and upper bound for the colormap, passed to matplotlib.colors.Normalize
    background : matplotlib color, if not provided, defaults to black
    edgecolor : matplotlib color, if not provided, defaults to white
    bordercolor : matplotlib color, if not provided, defaults to white
    ylabel : str, optional
            Label to display next to the colorbar
    figsize : list, optional
            Dimensions of the final figure, passed to matplotlib.pyplot.figure
    title : str, optional
            Title displayed above the figure, passed to matplotlib.axes.Axes.set_title
    fontsize: int, optional
            Relative font size for all elements (ticks, labels, title)
    """
    import matplotlib.pyplot as plt
    import os.path as op
    from glob import glob
    import ggseg

    wd = op.join(op.dirname(ggseg.__file__), 'data', 'aseg')
    reg = [op.basename(e) for e in glob(op.join(wd, '*'))]

    # Select data from known regions (prevents colorbar from going wild)
    known_values = []
    for k, v in data.items():
        if k in reg:
            known_values.append(v)

    whole_reg = ['Coronal', 'Sagittal']
    files = [open(op.join(wd, e)).read() for e in whole_reg]

    # A figure is created by the joint dimensions of the whole-brain outlines
    ax = _create_figure_(files, figsize, background,  title, fontsize, edgecolor)

    # Each region is outlined
    reg = glob(op.join(wd, '*'))
    files = [open(e).read() for e in reg]
    _render_regions_(files, ax, bordercolor, edgecolor)

    # For every region with a provided value, we draw a patch with the color
    # matching the normalized scale
    cmap, norm = _get_cmap_(cmap, known_values, vminmax=vminmax)
    _render_data_(data, wd, cmap, norm, ax, edgecolor)

    # The following regions are ignored/displayed in gray
    NA = ['Cerebellum-Cortex', 'Cerebellum-White-Matter', 'Brain-Stem']
    files = [open(op.join(wd, e)).read() for e in NA]
    _render_regions_(files, ax, '#111111', edgecolor)

    # A colorbar is added
    _add_colorbar_(ax, cmap, norm, edgecolor, fontsize*0.75, ylabel)

    plt.show()

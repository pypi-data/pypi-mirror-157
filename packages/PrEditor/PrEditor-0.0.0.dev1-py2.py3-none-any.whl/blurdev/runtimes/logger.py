from __future__ import absolute_import
import os
import sys
from argparse import ArgumentParser


def main():
    # register the blurdev import location

    blurdevpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    if blurdevpath not in sys.path:
        sys.path.insert(0, blurdevpath)

    # When blurdev is imported, it will set the ApplicationName to match this.
    os.environ['BDEV_APPLICATION_NAME'] = 'PythonLogger'

    # launch the editor
    import blurdev

    parser = ArgumentParser()
    parser.add_argument(
        '-w',
        '--runWorkbox',
        action="store_true",
        help='After the logger is shown, run the current workbox text.',
    )
    args = parser.parse_args()

    if args.runWorkbox:
        kwargs = {'runWorkbox': True}
    else:
        kwargs = None

    from blurdev.gui.loggerwindow import LoggerWindow

    # Set the app user model id here not in the LoggerWindow.__init__ so
    # if a external treegrunt tool calls setAppUserModelID then adds the
    # logger it won't change the id to PythonLogger.
    blurdev.setAppUserModelID('PythonLogger')
    blurdev.launch(LoggerWindow.instance, coreName='logger', kwargs=kwargs)


if __name__ == '__main__':
    main()

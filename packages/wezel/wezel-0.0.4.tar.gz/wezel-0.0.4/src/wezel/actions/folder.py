from wezel.core import Action

def menu(parent):

    parent.action(Open, shortcut='Ctrl+O')
    parent.action(Read)
    parent.action(Save, shortcut='Ctrl+S')
    parent.action(Restore, shortcut='Ctrl+R')
    parent.action(Close, shortcut='Ctrl+C')

class Open(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return True

    def run(self, app):
        """
        Open a DICOM folder and update display.
        """
        app.status.message("Opening DICOM folder..")
        path = app.dialog.directory("Select a DICOM folder")
        if path == '':
            app.status.message('') 
            return
        app.status.cursorToHourglass()
        app.close()
        app.open(path)
        app.status.cursorToNormal()


class Close(Action):
    """
    Close wezel.
    """ 
    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False  
        if app.folder is None:
            return False
        return app.folder.is_open()

    def run(self, app):

        closed = app.folder.close()
        if closed: 
            app.close()


class Read(Action):

    def enable(self, app):

        if app.__class__.__name__ != 'Windows':
            return False 
        if app.folder is None:
            return False  
        return app.folder.is_open()

    def run(self, app):
        """
        Read the open DICOM folder.
        """
        app.status.cursorToHourglass()
        app.closeAllSubWindows()
        app.folder.scan()
        app.status.cursorToNormal() 
        app.refresh()


class Restore(Action):

    def enable(self, app):
        
        if not hasattr(app, 'folder'):
            return False
        if app.folder is None:
            return False
        return app.folder.is_open()

    def run(self, app):
        """
        Restore the open DICOM folder.
        """
        app.folder.restore()
        app.refresh()


class Save(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False 
        if app.folder is None:
            return False  
        return app.folder.is_open()

    def run(self, app):
        """
        Saves the open DICOM folder.
        """
        app.folder.save()
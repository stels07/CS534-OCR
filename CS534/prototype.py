#-------------------------------------------------------------------------------
# Name:        prototype
# Purpose:
#
# Author:      Administrator
#
# Created:     31/03/2016
# Copyright:   (c) Administrator 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import wx                  # This module uses the new wx namespace
#----------------------------------------------------------------------
import multiclass
import imageprocessing

class DoodleWindow(wx.Window):
    menuColours = { 100 : 'Black',
                    101 : 'Yellow',
                    102 : 'Red',
                    103 : 'Green',
                    104 : 'Blue',
                    105 : 'Purple',
                    106 : 'Brown',
                    107 : 'Aquamarine',
                    108 : 'Forest Green',
                    109 : 'Light Blue',
                    110 : 'Goldenrod',
                    111 : 'Cyan',
                    112 : 'Orange',
                    113 : 'Navy',
                    114 : 'Dark Grey',
                    115 : 'Light Grey',
                    }
    maxThickness = 40


    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour("WHITE")
        self.listeners = []
        self.thickness = 40
        self.SetColour("Light Blue")
        self.lines = []
        self.x = self.y = 0
        self.MakeMenu()

        self.InitBuffer()

        # hook some mouse events
        wx.EVT_LEFT_DOWN(self, self.OnLeftDown)
        wx.EVT_LEFT_UP(self, self.OnLeftUp)
        wx.EVT_RIGHT_UP(self, self.OnRightUp)
        wx.EVT_MOTION(self, self.OnMotion)

        # the window resize event and idle events for managing the buffer
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_IDLE(self, self.OnIdle)

        # and the refresh event
        wx.EVT_PAINT(self, self.OnPaint)

        # When the window is destroyed, clean up resources.
        wx.EVT_WINDOW_DESTROY(self, self.Cleanup)


    def Cleanup(self, evt):
        if hasattr(self, "menu"):
            self.menu.Destroy()
            del self.menu


    def InitBuffer(self):
        """Initialize the bitmap used for buffering the display."""
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawLines(dc)
        self.reInitBuffer = False


    def SetColour(self, colour):
        """Set a new colour and make a matching pen"""
        self.colour = colour
        self.pen = wx.Pen(self.colour, self.thickness, wx.SOLID)
        self.Notify()


    def SetThickness(self, num):
        """Set a new line thickness and make a matching pen"""
        self.thickness = num
        self.pen = wx.Pen(self.colour, self.thickness, wx.SOLID)
        self.Notify()


    def GetLinesData(self):
        return self.lines[:]


    def SetLinesData(self, lines):
        self.lines = lines[:]
        self.InitBuffer()
        self.Refresh()


    def MakeMenu(self):
        """Make a menu that can be popped up later"""
        menu = wx.Menu()
        keys = self.menuColours.keys()
        keys.sort()
        for k in keys:
            text = self.menuColours[k]
            menu.Append(k, text, kind=wx.ITEM_CHECK)
        wx.EVT_MENU_RANGE(self, 100, 200, self.OnMenuSetColour)
        wx.EVT_UPDATE_UI_RANGE(self, 100, 200, self.OnCheckMenuColours)
        menu.Break()

        for x in range(1, self.maxThickness+1):
            menu.Append(x, str(x), kind=wx.ITEM_CHECK)
        wx.EVT_MENU_RANGE(self, 1, self.maxThickness, self.OnMenuSetThickness)
        wx.EVT_UPDATE_UI_RANGE(self, 1, self.maxThickness, self.OnCheckMenuThickness)
        self.menu = menu


    # These two event handlers are called before the menu is displayed
    # to determine which items should be checked.
    def OnCheckMenuColours(self, event):
        text = self.menuColours[event.GetId()]
        if text == self.colour:
            event.Check(True)
            event.SetText(text.upper())
        else:
            event.Check(False)
            event.SetText(text)

    def OnCheckMenuThickness(self, event):
        if event.GetId() == self.thickness:
            event.Check(True)
        else:
            event.Check(False)


    def OnLeftDown(self, event):
        """called when the left mouse button is pressed"""
        self.curLine = []
        self.x, self.y = event.GetPosition()
        self.CaptureMouse()


    def OnLeftUp(self, event):
        """called when the left mouse button is released"""
        if self.HasCapture():
            self.lines.append( (self.colour, self.thickness, self.curLine) )
            self.curLine = []
            self.ReleaseMouse()


    def OnRightUp(self, event):
        """called when the right mouse button is released, will popup the menu"""
        pt = event.GetPosition()
        self.PopupMenu(self.menu, pt)



    def OnMotion(self, event):
        """
        Called when the mouse is in motion.  If the left button is
        dragging then draw a line from the last event position to the
        current one.  Save the coordinants for redraws.
        """
        if event.Dragging() and event.LeftIsDown():
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            # dc.BeginDrawing()
            dc.SetPen(self.pen)
            pos = event.GetPosition()
            coords = (self.x, self.y, pos[0],pos[1])
            self.curLine.append(coords)
            dc.DrawLine(self.x, self.y, pos[0], pos[1])
            self.x, self.y = pos
            # dc.EndDrawing()

    def clearDC(self):
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()

    def OnSize(self, event):
        """
        Called when the window is resized.  We set a flag so the idle
        handler will resize the buffer.
        """
        self.reInitBuffer = True


    def OnIdle(self, event):
        """
        If the size was changed then resize the bitmap used for double
        buffering to match the window size.  We do it in Idle time so
        there is only one refresh after resizing is done, not lots while
        it is happening.
        """
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)


    def OnPaint(self, event):
        """
        Called when the window is exposed.
        """
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        dc = wx.BufferedPaintDC(self, self.buffer)


    def DrawLines(self,dc):
        """
        Redraws all the lines that have been drawn already.
        """
        # dc.BeginDrawing()
        for colour, thickness, line in self.lines:
            pen = wx.Pen(colour, thickness, wx.SOLID)
            dc.SetPen(pen)
            for coords in line:
                apply(dc.DrawLine, coords)
        # dc.EndDrawing()


    # Event handlers for the popup menu, uses the event ID to determine
    # the colour or the thickness to set.
    def OnMenuSetColour(self, event):
        self.SetColour(self.menuColours[event.GetId()])

    def OnMenuSetThickness(self, event):
        self.SetThickness(event.GetId())


    # Observer pattern.  Listeners are registered and then notified
    # whenever doodle settings change.
    def AddListener(self, listener):
        self.listeners.append(listener)

    def Notify(self):
        for other in self.listeners:
            other.Update(self.colour, self.thickness)


#----------------------------------------------------------------------

class DoodleFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "CS534", size=(256,343),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.Center()
        toolbar = self.CreateToolBar()
        qtool = toolbar.AddLabelTool(wx.ID_ANY, 'save', wx.Bitmap('Flag-blue-48.png'))
        ptool = toolbar.AddLabelTool(wx.ID_ANY, 'predict', wx.Bitmap('Flag-greed-48.png'))
        ctool = toolbar.AddLabelTool(wx.ID_ANY, 'clear', wx.Bitmap('Flag-red-48.png'))
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnSave, qtool)
        self.Bind(wx.EVT_TOOL, self.OnPredict, ptool)
        self.Bind(wx.EVT_TOOL, self.OnClear, ctool)
        self.doodle = DoodleWindow(self, -1)
        self.sb = self.CreateStatusBar()
        self.celsius = wx.StaticText(self, label='', pos=(220, 10))
        self.c=all_classifiers().classifier

    def OnClear(self,event):
        self.doodle.clearDC()

    def OnSave(self,event):
        dlg = wx.TextEntryDialog(frame, 'Enter some text','Text Entry')
        #dlg.SetValue("Default")
        if dlg.ShowModal() == wx.ID_OK:
            print 'You entered: %s\n' % dlg.GetValue()
        dlg.Destroy()
        self.name=dlg.GetValue()+'.bmp'
        self.doodle.buffer.SaveFile('store_images/'+self.name, type=wx.BITMAP_TYPE_BMP, palette=None)

    def OnSave_1(self):
        self.name='first.bmp'
        self.doodle.buffer.SaveFile(self.name, type=wx.BITMAP_TYPE_BMP, palette=None)

    def OnPredict(self,event):
        self.OnSave_1()
        r=imageprocessing.readImg(self.name)
        test_sample = self.get_feature_(r.imageMatrixWhole)
        print "test_sample size: ",test_sample.size
        #p=multiclass.multipredict1(test_sample)
        import affinity_predict
        a=affinity_predict.affinity_predict(test_sample)
        if(a.is_vague()):
            p=multiclass.predict_new(test_sample,self.c)
            print "svm: ",p," ap: ",a.first_nearest
        else:
            p=a.first_nearest
        #p_1=multiclass.predict_new(test_sample,self.c)
        print p
        self.sb.SetStatusText(str(p))
        self.celsius.SetLabel(str(p))


    def get_feature_(self,r):
        import feature_extraction
        f=feature_extraction.feature_extraction(r)
        return f.combine_all()


import numpy as np
#path="features_all_without_skeleton"
path="features_all_compress5"
class all_classifiers():
    def __init__(self):
        global path
        u=np.load(path+'/labels.npz')['ulabels']
        print "loading classifiers...labels are: ", u
        self.classifier={}
        self.classifier['kernel']=np.load(path+'/labels.npz')['k']
        self.classifier['labels']=u
        uu=list(u)
        for i in u:
            uu.remove(i)
            for j in uu:
                id=str(i)+","+str(j)
                bias=np.load(path+'/'+id+'.npz')['bias']
                support_multipliers = np.load(path+'/'+id+'.npz')['support_multipliers']
                support_vectors = np.load(path+'/'+id+'.npz')['support_vectors']
                support_vector_labels = np.load(path+'/'+id+'.npz')['support_vector_labels']
                c=classifier(bias,support_vectors,support_multipliers,support_vector_labels)
                self.classifier[id]=c
        print len(self.classifier)-2, "classifiers are loaded..."

class classifier():
    def __init__(self, bias, support_vectors, support_vector_multipliers, support_vector_labels):
        self.bias=bias
        self.support_vectors=support_vectors
        self.support_vectors_multipliers=support_vector_multipliers
        self.support_vector_labels=support_vector_labels



if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = DoodleFrame(None)
    frame.Show(True)
    app.MainLoop()
# -*- coding: utf-8 -*-
__author__ = 'linzhonghong'

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import os
import time
from ping import quiet_ping

import wx
import wx.lib.agw.ultimatelistctrl as ULC
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin#, TextEditMixin

from utils import call_thread,validateIP

class MyStatusBar(wx.StatusBar):
    def __init__(self, parent, version='0.0.1'):
        wx.StatusBar.__init__(self, parent)

        self.basedir = os.path.split(os.path.realpath(sys.argv[0]))[0].decode('gb2312') + os.sep + 'images'
        (self.percent_lost, self.max_tt, self.avg_tt) = (100, None, None)

        self.SetSize((-1, 24))
        self.SetFieldsCount(2)
        self.SetStatusWidths([-5, -2])
        # field one
        self.SetStatusText('主程序版本：%s' % version, 0)
        # field two
        self.SetStatusText('Written by linzhonghong', 1)
        self.total = wx.StaticText(self, -1, 'total lines: %s' % 0)
        self.total.Hide()
        self.current = wx.StaticText(self, -1, 'selected line: %s' % 0)
        self.current.Hide()
        self.third = wx.StaticText(self, -1, 'fail: %s' % 0)
        self.third.Hide()
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.PlaceIcon()

    def PlaceIcon(self):
        rect2 = self.GetFieldRect(1)
        self.total.SetPosition((rect2.x+5, rect2.y+2))
        (w, h) = self.total.GetClientSize()
        self.current.SetPosition((rect2.x+w+12, rect2.y+2))
        (x, y) = self.current.GetPositionTuple()
        (w1, h1) = self.current.GetClientSize()
        self.third.SetPosition((x+w1+6, rect2.y+2))

    def OnSize(self, event):
        self.PlaceIcon()
   
class BaseDialog(wx.Dialog):
    def __init__(self, parent, id=-1, title='',pos=wx.DefaultPosition,size=wx.DefaultSize,):
        wx.Dialog.__init__(self, parent, id, title, pos, size,style=wx.DEFAULT_DIALOG_STYLE^(wx.CLOSE_BOX|wx.CAPTION))
        self.basedir = os.path.split(os.path.realpath(sys.argv[0]))[0].decode('gb2312') + os.sep + 'images'
        #        self.SetIcon(wx.Icon(self.basedir + os.sep + 'logo_new.ico', wx.BITMAP_TYPE_ICO))
        self.__Layout()
        self.__BindEvent()

    def __Layout(self):
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.p_top = wx.Panel(self, -1)
        self.p_top.SetBackgroundColour("sky blue")
        logo = wx.StaticBitmap(self.p_top, -1, wx.Bitmap(self.basedir+os.sep+'logo16.png'))
        st = wx.StaticText(self.p_top, -1, self.GetTitle())
        st.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False,'Arial'))
        st.SetForegroundColour(wx.Colour(255, 255, 255))
        image_c = wx.Image(self.basedir + os.sep + 'close.png',wx.BITMAP_TYPE_PNG)
        close_image1 = image_c.GetSubImage((0, 0, image_c.GetWidth()/3, image_c.GetHeight())).ConvertToBitmap()
        close_image2 = image_c.GetSubImage((image_c.GetWidth()/3, 0, image_c.GetWidth()/3, image_c.GetHeight())).ConvertToBitmap()
        self.btn_close = wx.BitmapButton(self.p_top, -1, close_image1, style = wx.NO_BORDER)
        self.btn_close.SetBitmapHover(close_image2)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(logo,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL^wx.RIGHT, 8)
        hbox.Add(st,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 8)
        hbox.Add((-1,-1), 1, wx.EXPAND)
        hbox.Add(self.btn_close, 0, wx.RIGHT|wx.ALL, -1)
        self.p_top.SetSizer(hbox)
        self.main_sizer.Add(self.p_top,0,wx.BOTTOM|wx.EXPAND,10)
        self.SetSizer(self.main_sizer)

    def __BindEvent(self):
        self.Bind(wx.EVT_BUTTON, self.__OnClose, self.btn_close)
        self.p_top.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.p_top.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.p_top.Bind(wx.EVT_MOTION, self.OnMouseMove)

    def __OnClose(self, event):
        self.Hide()

    def OnLeftDown(self, evt):#1 鼠标按下
        widget = evt.GetEventObject()
        widget.CaptureMouse()
        pos = self.ClientToScreen(evt.GetPosition())
        origin = self.GetPosition()
        self.delta = wx.Point(pos.x - origin.x, pos.y - origin.y)

    def OnMouseMove(self, evt):#2 鼠标移动
        if evt.Dragging() and evt.LeftIsDown():
            pos = self.ClientToScreen(evt.GetPosition())
            newPos = (pos.x - self.delta.x, pos.y - self.delta.y)
            self.Move(newPos)

    def OnLeftUp(self, evt):#3 鼠标释放
        widget = evt.GetEventObject()
        if widget.HasCapture():
            widget.ReleaseMouse()

# 提示窗口
class WarnDialog(BaseDialog):
    def __init__(self, parent, msg, have_cancel_btn=False):
        BaseDialog.__init__(self, parent,title='警告')
        self.msg = msg
        self.have_cancel_btn = have_cancel_btn
        self._DoLayout()

    def _DoLayout(self):
        self.panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        tip = wx.StaticText(self.panel, -1, self.msg)
        tip.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False,'Arial'))
        tip.SetForegroundColour('red')
        okButton = wx.Button(self.panel, wx.ID_OK, '确定')
        btnSizer = wx.StdDialogButtonSizer()
        btnSizer.AddButton(okButton)
        if self.have_cancel_btn:
            cancelButton = wx.Button(self.panel, wx.ID_CANCEL, '取消')
            btnSizer.AddButton(cancelButton)
        btnSizer.Realize()
        sizer.Add(tip, 0,wx.ALL^wx.BOTTOM|wx.EXPAND|wx.CENTER,10)
        sizer.Add(btnSizer, 1, wx.ALL|wx.EXPAND,20)
        self.panel.SetSizer(sizer)
        self.main_sizer.Add(self.panel, wx.ALL|wx.EXPAND,10)
        self.main_sizer.Fit(self)

class BaseDialog2(wx.Dialog):
    def __init__(self, parent, id=-1, title='',pos=wx.DefaultPosition,size=wx.DefaultSize,):
        wx.Dialog.__init__(self, parent, id, title, pos, size,style=wx.DEFAULT_DIALOG_STYLE^(wx.CLOSE_BOX|wx.CAPTION))
        self.basedir = os.path.split(os.path.realpath(sys.argv[0]))[0].decode('gb2312') + os.sep + 'images'
        #        self.SetIcon(wx.Icon(self.basedir + os.sep + 'logo_new.ico', wx.BITMAP_TYPE_ICO))
        self.__Layout()

    def __Layout(self):
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.p_top = wx.Panel(self, -1)
        self.p_top.SetBackgroundColour("sky blue")
        logo = wx.StaticBitmap(self.p_top, -1, wx.Bitmap(self.basedir+os.sep+'logo16.png'))
        st = wx.StaticText(self.p_top, -1, self.GetTitle())
        st.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False,'Arial'))
        st.SetForegroundColour(wx.Colour(255, 255, 255))
        image_c = wx.Image(self.basedir + os.sep + 'close.png',wx.BITMAP_TYPE_PNG)
        close_image1 = image_c.GetSubImage((0, 0, image_c.GetWidth()/3, image_c.GetHeight())).ConvertToBitmap()
        close_image2 = image_c.GetSubImage((image_c.GetWidth()/3, 0, image_c.GetWidth()/3, image_c.GetHeight())).ConvertToBitmap()
        self.btn_close = wx.BitmapButton(self.p_top, -1, close_image1, style = wx.NO_BORDER)
        self.btn_close.SetBitmapHover(close_image2)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(logo,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL^wx.RIGHT, 8)
        hbox.Add(st,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 8)
        hbox.Add((-1,-1), 1, wx.EXPAND)
        hbox.Add(self.btn_close, 0, wx.RIGHT|wx.ALL, -1)
        self.p_top.SetSizer(hbox)
        self.main_sizer.Add(self.p_top,0,wx.BOTTOM|wx.EXPAND,10)
        self.SetSizer(self.main_sizer)

# 提示窗口
class WarnDialog2(BaseDialog2):
    def __init__(self, parent, msg, have_cancel_btn=False):
        BaseDialog2.__init__(self, parent,title='警告')
        self.msg = msg
        self.have_cancel_btn = have_cancel_btn
        self._DoLayout()

    def _DoLayout(self):
        self.panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.tip = wx.StaticText(self.panel, -1, self.msg)
        self.tip.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False,'Arial'))
        self.tip.SetForegroundColour('red')
        sizer.Add(self.tip, 0,wx.ALL|wx.EXPAND|wx.CENTER,10)
        self.panel.SetSizer(sizer)
        self.main_sizer.Add(self.panel, wx.ALL|wx.EXPAND,10)
        self.main_sizer.Fit(self)

# 注销窗口
class LogoutDialog(BaseDialog):
    def __init__(self, parent, title):
        BaseDialog.__init__(self, parent,title=title)
        self._DoLayout()

    def _DoLayout(self):
        self.panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        tip = wx.StaticText(self.panel, -1, '确定注销帐号？')
        tip.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False,'Arial'))
        tip.SetForegroundColour('red')
        okButton = wx.Button(self.panel, wx.ID_OK, '确定')
        cancelButton = wx.Button(self.panel, wx.ID_CANCEL, '取消')
        btnSizer = wx.StdDialogButtonSizer()
        btnSizer.AddButton(okButton)
        btnSizer.AddButton(cancelButton)
        btnSizer.Realize()
        sizer.Add(tip, 0,wx.ALL^wx.BOTTOM|wx.EXPAND|wx.CENTER,10)
        sizer.Add(btnSizer, 1, wx.ALL|wx.EXPAND,30)
        self.panel.SetSizer(sizer)
        self.main_sizer.Add(self.panel, wx.ALL|wx.EXPAND,10)
        self.main_sizer.Fit(self)

# 验证器
class MyValidator(wx.PyValidator):
    def __init__(self, data, key):
        wx.PyValidator.__init__(self)
        self.data = data
        self.key = key

    def Clone(self):
        """
        Note that every validator must implement the Clone() method.
        """
        return MyValidator(self.data, self.key)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        widget = self.GetWindow()
        if isinstance(widget, wx.TextCtrl):
            widget.SetValue(self.data.get(self.key, ""))
        elif isinstance(widget, wx.CheckBox):
            if self.data.get(self.key, False) == 'False':
                state = False
            elif self.data.get(self.key, False) == 'True':
                state = True
            else:
                state = False
            widget.SetValue(state)
        return True

    def TransferFromWindow(self):
        widget = self.GetWindow()
        if isinstance(widget, wx.TextCtrl):
            self.data[self.key] = widget.GetValue()
        elif isinstance(widget, wx.CheckBox):
            self.data[self.key] = widget.IsChecked()
        return True

class LoginValidator(MyValidator):
    def __init__(self, data, key, tip):
        MyValidator.__init__(self,data,key)
        self.data = data
        self.key = key
        self.tip = tip

    def Clone(self):
        """
        Note that every validator must implement the Clone() method.
        """
        return LoginValidator(self.data, self.key, self.tip)

    def Validate(self, win):
        result = True
        widget = self.GetWindow()
        text = widget.GetValue()
        if self.key=='user' and isinstance(widget, wx.TextCtrl):
            if len(text)==0:
                result = False
#            if encrypt(text) not in auth.keys():
#                self.tip.SetLabel('用户不存在')
#                self.tip.SetForegroundColour('red')
#                result = False
        elif self.key=='password':
            if len(text)<6 or len(text)>30:
                self.tip.SetLabel('密码长度错误')
                self.tip.SetForegroundColour('red')
                result = False
        if result:
            widget.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            widget.Refresh()
        else:
            widget.SetBackgroundColour('#ffcccc')
            widget.SetFocus()
            widget.Refresh()
        return result


# 登录框
class LoginDialog(wx.Dialog):
    '''
    登陆对话窗体,请勿直接调用ShowModal() ,调用Show()
    '''

    def __init__(self,parent=None,title=None,size=(-1,-1),
                 userTxtLen=None,pwdTxtLen=None
                 ,data=None):
        wx.Dialog.__init__(self,parent,-1,title,size=size,
            style=wx.DEFAULT_DIALOG_STYLE^(wx.CLOSE_BOX|wx.CAPTION))
        self.txtCtrMap={}           #缓存输入框
        self.data = data
        self.okBtn=None
        self.pwdLen = pwdTxtLen
        self.usrLen = userTxtLen
        self.basedir = os.path.split(os.path.realpath(sys.argv[0]))[0].decode('gb2312') + os.sep + 'images'
        self.CreateCompment()

    #构建label项
    def _dataTxtLabel(self):
        return (('用户',0,self._OnUserTxtInput,'user'),
                ('密码',wx.TE_PASSWORD,self._OnPwdInput,'password'))

    #构建checkbox项
    def _dataCheckBox(self):
        return (('记住密码', 0, self._SavePasswd, 'save'),
                ('自动登录', 0, self._AutoLogin, 'auto'))

    #构建button项
    def _dataWithButton(self):
        return((wx.ID_OK,'登录'),
               #               (wx.ID_CANCEL,'取消)
            )

    #构建TextCtrl项
    def _CreateTxtLabel(self, sizer, eachLabel, eachStyle, eachHandler, data, key):
        box = wx.FlexGridSizer(1, 2, 5, 10)
        label = wx.StaticText(self, -1, eachLabel, size = (40, -1))
        box.Add(label, 0, wx.ALIGN_RIGHT| wx.LEFT, 40)
        text = wx.TextCtrl(self, -1, size = (180, -1), style = eachStyle, validator=LoginValidator(data, key, self.tip))
        text.Bind(wx.EVT_TEXT, eachHandler)
        box.Add(text,1, wx.ALIGN_CENTER_HORIZONTAL| wx.RIGHT ,40)
        sizer.Add(box, 0, wx.ALIGN_CENTER| wx.ALL, 5)
        self.txtCtrMap[eachLabel]=text

    def _CreateCheckBox(self, sizer, data):
        box = wx.FlexGridSizer(1, 2, 5, 10)
        cbox = wx.BoxSizer(wx.HORIZONTAL)
        for eachLabel,eachStyle,eachHandler,key in self._dataCheckBox():
            checkbox = wx.CheckBox(self, -1, eachLabel, style = eachStyle, validator=LoginValidator(data, key, self.tip))
            self.txtCtrMap[eachLabel] = checkbox
            checkbox.Bind(wx.EVT_CHECKBOX, eachHandler)
            cbox.Add(checkbox, 0, wx.RIGHT, 5)
        box.Add(wx.StaticText(self, -1), 0)
        box.Add(cbox, 1)
        sizer.Add(box, 0, wx.ALIGN_CENTER| wx.ALL, 5)

    def _AddTip(self, sizer):
        innerBox = wx.StdDialogButtonSizer()
        innerBox.Add(self.tip, flag=wx.CENTER|wx.EXPAND)
        innerBox.Realize()
        sizer.Add(innerBox, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL^wx.BOTTOM, 5)
        pass

    def _CreateButton(self, btnSizer, eachID, eachLabel):
        btn = wx.Button(self,eachID,eachLabel)
        if eachID==wx.ID_OK:
            btn.SetDefault()
            self.okBtn=btn
            self.Bind(wx.EVT_BUTTON, self._OnOK, self.okBtn)
        #            btn.Disable()
        btnSizer.AddButton(btn)

        #根据数据项构建组建
    def CreateCompment(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.p_top = wx.Panel(self, -1)
        self.p_top.SetBackgroundColour("sky blue")
        image_c = wx.Image(self.basedir + os.sep + 'close.png',wx.BITMAP_TYPE_PNG)
        close_image1 = image_c.GetSubImage((0, 0, image_c.GetWidth()/3, image_c.GetHeight())).ConvertToBitmap()
        close_image2 = image_c.GetSubImage((image_c.GetWidth()/3, 0, image_c.GetWidth()/3, image_c.GetHeight())).ConvertToBitmap()
        logo = wx.StaticBitmap(self.p_top, -1, wx.Bitmap(self.basedir+os.sep+'logo16.png'))
        st = wx.StaticText(self.p_top, -1, self.GetTitle())
        st.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False,'Arial'))
        st.SetForegroundColour(wx.Colour(255, 255, 255))
        #st.SetFocus()
        self.btn_close = wx.BitmapButton(self.p_top, -1, close_image1, style = wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON, self._Change, self.btn_close)
        self.btn_close.SetBitmapHover(close_image2)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(logo,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL^wx.RIGHT, 8)
        hbox.Add(st,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 8)
        hbox.Add((-1,-1), 1, wx.EXPAND)
        hbox.Add(self.btn_close, 0, wx.RIGHT|wx.ALL, -1)
        self.p_top.SetSizer(hbox)
        sizer.Add(self.p_top,0,wx.BOTTOM|wx.EXPAND,10)
        self.tip = wx.StaticText(self, -1, '')
        #        self.tip.Hide()
        for eachLabel,eachStyle,eachHandler,key in self._dataTxtLabel():
            self._CreateTxtLabel(sizer,eachLabel,eachStyle,eachHandler,self.data,key)

        self._CreateCheckBox(sizer, self.data)
        self._AddTip(sizer)

        btnSizer = wx.StdDialogButtonSizer()
        for eachID,eachLabel in self._dataWithButton():
            self._CreateButton(btnSizer,eachID,eachLabel)
        btnSizer.Realize()

        sizer.Add(btnSizer,1,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL,10)
        self.sizerBottomIndex = sizer.GetItemIndex(btnSizer)
        self.SetSizer(sizer)
        self.Fit()

    def _Change(self,event):
        self.Destroy()
        event.Skip()

    def _OnUserTxtInput(self,event):
    #        self._EnableOrDisableOkBtn()
        event.Skip()

    def _OnPwdInput(self,event):
    #        self._EnableOrDisableOkBtn()
        event.Skip()

    def _SavePasswd(self, event):
        event.Skip()
        pass

    def _AutoLogin(self, event):
        event.Skip()
        pass

    def _OnOK(self, event):
        allValid = True
        for control in self.GetChildren():
            if isinstance(control, wx.TextCtrl):
                validator = control.GetValidator()
                if validator:
                    isValid = validator.Validate(control)
                    if not isValid:
                        allValid = False
                    else:
                        validator.TransferFromWindow()
        if not allValid:
            return False
        event.Skip()

    #确保两个框都有输入
    def _EnableOrDisableOkBtn(self):
        self.okBtn.Enable()
        pass

    #调用该函数将显示窗体并确定后可返回结果
    def Show(self):
        res = self.ShowModal()
        if res == wx.ID_OK:
            return res


class EditDialog(BaseDialog):
    def __init__(self, parent, title, data, modify):
    #        print parent.GetClientSize(),'size'
        self.w, self.h = parent.GetClientSize()
        self.data = data
        self.modify = modify
        BaseDialog.__init__(self, parent, title=title)
        self._DoLayout()

    def _DoLayout(self):
        self.panel = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        listsizer = wx.BoxSizer(wx.VERTICAL)
        for key, value in self.data.iteritems():
            key = str(key)
            itemsizer = wx.BoxSizer(wx.HORIZONTAL)
            itemsizer.Add(wx.TextCtrl(self.panel, -1, value[0], style=wx.TE_CENTER, size=(120, -1), name=key), 0, wx.LEFT, 10)
            itemsizer.Add(wx.ComboBox(self.panel, -1, value=value[1],choices=['A', 'CNAME'], size=(70, -1), name=key), 0, wx.LEFT, 10)
            itemsizer.Add(wx.ComboBox(self.panel, -1, value=value[2],choices=['默认', '电信', '联通', '移动'], size=(60, -1), name=key), 0, wx.LEFT, 10)
            itemsizer.Add(wx.TextCtrl(self.panel, -1, value[3], style=wx.TE_CENTER, size=(250, -1), name=key), 0, wx.LEFT, 10)
            itemsizer.Add(wx.TextCtrl(self.panel, -1, value[4], style=wx.TE_CENTER, name=key), 0, wx.LEFT, 10)
            listsizer.Add(itemsizer, 0, wx.BOTTOM, 10)
        okButton = wx.Button(self.panel, wx.ID_OK, '保存')
        cancelButton = wx.Button(self.panel, wx.ID_CANCEL, '取消')
        btnSizer = wx.StdDialogButtonSizer()
        btnSizer.AddButton(okButton)
        btnSizer.AddButton(cancelButton)
        btnSizer.Realize()
        sizer.Add(listsizer, 1,wx.ALL|wx.EXPAND|wx.CENTER,-1)
        sizer.Add(btnSizer, 0, wx.ALL|wx.EXPAND,20)
        self.panel.SetSizer(sizer)
        sizer.Fit(self.panel)
        self.main_sizer.Add(self.panel, wx.ALL^wx.TOP|wx.EXPAND,10)
#        self.panel.Fit()
        self.main_sizer.Fit(self)

class MyListCtrl(ULC.UltimateListCtrl, ListCtrlAutoWidthMixin#, TextEditMixin
                ):
    Header = [u'主机记录', u'记录类型', u'线路类型', u'记录值', 'TTL', 'REC_ID', 'ENABLED']
    def __init__(self, parent, width=0, size=wx.DefaultSize):
        ULC.UltimateListCtrl.__init__(
            self, parent, -1,
            agwStyle=wx.LC_REPORT
                     #| wx.BORDER_SUNKEN
                     | wx.BORDER_NONE
#                     | wx.LC_EDIT_LABELS
                     #| wx.LC_SORT_ASCENDING
                     #| wx.LC_NO_HEADER
#                     | wx.LC_VRULES
                     | wx.LC_HRULES
            #| wx.LC_SINGLE_SEL
                     | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
                    |ULC.ULC_AUTO_CHECK_CHILD|ULC.ULC_AUTO_CHECK_PARENT
                     | ULC.ULC_USER_ROW_HEIGHT
        )
        ListCtrlAutoWidthMixin.__init__(self)
        self.check_list = []
        self.__SetHeader(self.Header)
        self.__BindEvent()


    def __SetHeader(self, header):
        """
        # see http://xoomer.virgilio.it/infinity77/AGW_Docs/ultimatelistctrl.UltimateListItem.html#ultimatelistctrl-ultimatelistitem
        :param header:
        :return:
        """
        boldfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldfont.SetWeight(wx.BOLD)
        boldfont.SetPointSize(9)
        for index, value in enumerate(header):
            info = ULC.UltimateListItem()
            if index == 0:
                info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_CHECK | ULC.ULC_MASK_FONT | ULC.ULC_MASK_WINDOW
                info._kind = 1
            else:
                info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT
            info._format = 2
            info._text = "\n%s\n" % value
            info._font = boldfont
            self.InsertColumnInfo(index, info)
        self.SetColumnWidth(0, 180)
        self.SetColumnWidth(1, 100)
        self.SetColumnWidth(2, 100)
        self.SetColumnWidth(3, 250)
        self.SetColumnWidth(4, 115)
        self.SetColumnWidth(5, 1)
        self.SetColumnWidth(6, 1)
        self.SetColumnShown(5, shown=False)
        self.SetColumnShown(6, shown=False)
        self.SetUserLineHeight(30)

    def OnGetItemCheck(self, item):
        item=self.GetItem(item)
        return item.IsChecked()

    @call_thread
    def fill_table(self, rec_data, widget):
        try:
#            self.Freeze()
            self.DeleteAllItems()
            self.storedata = {}
            self.index = 0
            for rec in sorted(rec_data, key=lambda item:(-int(item['enabled']),item['name'])):
                if self.index < 20:
#                    self.InsertItem()
                    try:
                        wx.CallAfter(self.__AddItems, self.index, rec)
                    except:
                        print 'error......'
                self.storedata["%s|%s"%(rec['name'],rec['value'])] = [rec['name']
                                                                        , rec['type']
                                                                        , rec['line']
                                                                        , rec['value']
                                                                        , rec['ttl']
                                                                        , rec['id']
                                                                        , rec['enabled']
                                                                        ]

                self.index += 1
            widget.Destroy()
#            self.Thaw()
#            self.Update()
        except:
            import traceback
            print traceback.format_exc(),'except'

    def __AddItems(self, idx, rec):
        index = self.InsertStringItem(idx, rec['name'], it_kind=1)
        self.SetStringItem(index, 1, rec['type'])
        self.SetStringItem(index, 2, rec['line'])
        self.SetStringItem(index, 3, rec['value'])
        self.SetStringItem(index, 4, rec['ttl'])
        self.SetStringItem(index, 5, rec['id'])
        self.SetStringItem(index, 6, rec['enabled'])
        if  rec['enabled'] == '0':
            self.SetItemBackgroundColour(index, wx.Colour(238,238,238))

    def __BindEvent(self):
        self.Bind(ULC.EVT_LIST_ITEM_CHECKED, self.OnCheck)
        self.Bind(ULC.EVT_LIST_ITEM_ACTIVATED, self.OnActivate)
        pass

    def OnCheck(self, event):
        # event.GetEventObject().GetItem(event.GetIndex()).IsChecked()
        try:
            idx = self.check_list.index(event.GetIndex())
        except ValueError:
            idx = None
        if idx == None:
            self.check_list.append(event.GetIndex())
        else:
            self.check_list.pop(idx)
        event.Skip()

    def OnActivate(self, event):
        wx.CallAfter(self.PopupWindow, [event.GetIndex()], modify=True)

    def PopupWindow(self, indexs=None, modify=False, dnspod=None):
        data = {}
        if modify:
            for index in indexs:
                item = []
                # 减掉隐藏的rec_id
                for col in range(self.GetColumnCount()-1):
    #                data[col] = self.GetItem(index, col).GetText()
                    item.append(self.GetItem(index, col).GetText())
                data[index] = item
            title = '修改'
        else:
            data[0] = ['', 'CNAME', '默认', '', '600']
            title = '添加'
        dlg = EditDialog(self, title, data, modify)
        dlg.CenterOnParent()
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            itemdata = {}
            for item in dlg.panel.GetSizer().GetChildren()[0].GetSizer().GetChildren():
                item.GetSizer().GetChildren()[0].GetWindow().GetValue()
                celldata = []
                for cell in item.GetSizer().GetChildren():
                    idx = cell.GetWindow().GetName()
                    celldata.append(cell.GetWindow().GetValue())
                itemdata[int(idx)] = celldata
            if modify:
                storelist = []
                self.Freeze()
                for key, value in sorted(itemdata.iteritems(), key=lambda item:item[0], reverse=True):
                    rec_id = self.GetItem(key, col=5).GetText()
                    if not validateIP(value[3]):
                        if not value[3].endswith('.'):
                            value[3] += '.'
                    code, res = dnspod.record_modify(rec_id, sub_domain=value[0], record_type=value[1], record_line=value[2], value=value[3])
                    if code:
                        v = [value[i] for i in range(len(value))]
                        rec_st = self.GetItem(key, col=6).GetText()
                        v.extend([rec_id, rec_st])
                        storelist.append(v)
                        self.DeleteItem(key)
                        self.check_list.remove(key)
                        self.storedata.pop("%s|%s"%(data[key][0],data[key][3]))
                        self.storedata["%s|%s"%(value[0],value[3])] = v
                    else:
                        self.SetItemBackgroundColour(key, wx.Colour(255, 0, 0))
                self.Thaw()
                self.Update()
                for item in storelist:
                    idx = self.InsertStringItem(0, item[0], it_kind=1)
                    self.SetStringItem(idx, 1, item[1])
                    self.SetStringItem(idx, 2, item[2])
                    self.SetStringItem(idx, 3, item[3])
                    self.SetStringItem(idx, 4, item[4])
                    self.SetStringItem(idx, 5, item[5])
                    self.SetStringItem(idx, 6, item[6])
            else:
                for value in itemdata.itervalues():
                    code, res = dnspod.record_create(sub_domain=value[0], record_type=value[1], record_line=value[2], value=value[3])
                    if code:
                        idx = self.InsertStringItem(0, value[0], it_kind=1)
                        self.SetStringItem(idx, 1, value[1])
                        self.SetStringItem(idx, 2, value[2])
                        if not validateIP(value[3]):
                            if not value[3].endswith('.'):
                                value[3] += '.'
                        self.SetStringItem(idx, 3, value[3])
                        self.SetStringItem(idx, 4, value[4])
                        rec_id = res['rec_id']
                        rec_st = '1' if res['status'] == 'enable' else '0'
                        self.SetStringItem(idx, 5, rec_id)
                        self.SetStringItem(idx, 6, rec_st)
                        v = [value[i] for i in range(len(value))]
                        v.extend([rec_id, rec_st])
                        self.storedata["%s|%s"%(value[0],value[3])] = v

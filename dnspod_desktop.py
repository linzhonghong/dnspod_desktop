# -*- coding: utf-8 -*-
__author__ = 'linzhonghong'
__version__ = '2013.11.001'

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
import os
from signal import SIGTERM

import wx
import  wx.lib.buttons  as  buttons
from gui import MyStatusBar,MyListCtrl,WarnDialog,LogoutDialog,LoginDialog,WarnDialog2
from utils import md5,get_conf,set_conf,clear_conf,init_conf,ModifyConf,CONF_DIR,encrypt,decrypt,call_thread
from dnspod_api import dnspod_api

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="DNSPOD",size=(750, 630),
            style=wx.SIMPLE_BORDER )
        # some arg
        # 路径或者文件名存在中文则必须转换为unicode编码，str.decode('gb2312')或者str.decode('gbk')
        self.basedir = os.path.split(os.path.realpath(sys.argv[0]))[0].decode('gb2312') + os.sep + 'images'
        self.confdir = CONF_DIR
        self.data = {}
        self.is_auth = False
        self.in_or_out = 'in'
        self.SetIcon(wx.Icon(self.basedir + os.sep + 'logo.ico', wx.BITMAP_TYPE_ICO))
        init_conf()
        # do layout
        self._DoLayout()
        # check new pc
        self._IsNewPC()
        # check auto login
        self._IsAutoLogin()
        # bind event
        self._BindEvent()
        # redirect
#        redir = RedirectText('debug_linzh.log')
#        sys.stdout = redir

    def _DoLayout(self):
        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        #
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(11)
        #
        p1 = wx.Panel(p, -1)
        self.p1 = p1
        p1.SetBackgroundColour("sky blue")
        logo = wx.StaticBitmap(self.p1, -1, wx.Bitmap(self.basedir+os.sep+'4year_logo.png'))
        st = wx.StaticText(p1, -1, '')
        st.SetFont(wx.Font(16,wx.SWISS,wx.NORMAL,wx.BOLD,False,'Arial'))
        st.SetForegroundColour(wx.Colour(255, 255, 255))
        #        st.SetFocus()
        image_c = wx.Image(self.basedir + os.sep + 'close.png',wx.BITMAP_TYPE_PNG)
        close_image1 = image_c.GetSubImage((0, 0, image_c.GetWidth()/3, image_c.GetHeight())).ConvertToBitmap()
        close_image2 = image_c.GetSubImage((image_c.GetWidth()/3, 0, image_c.GetWidth()/3, image_c.GetHeight())).ConvertToBitmap()
        image_m = wx.Image(self.basedir + os.sep + 'minsize.png',wx.BITMAP_TYPE_PNG)
        min_image1 = image_m.GetSubImage((0, 0, image_m.GetWidth()/4, image_m.GetHeight())).ConvertToBitmap()
        min_image2 = image_m.GetSubImage((image_m.GetWidth()/4, 0, image_m.GetWidth()/4, image_m.GetHeight())).ConvertToBitmap()

        self.btn_min = wx.BitmapButton(p1, -1, min_image1, style = wx.NO_BORDER)
        self.btn_min.SetBitmapHover(min_image2)
        self.btn_close = wx.BitmapButton(p1, -1, close_image1, style = wx.NO_BORDER)
        self.btn_close.SetBitmapHover(close_image2)

        self.login_user = wx.StaticText(p1, -1, '')
        self.login_user.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.NORMAL,False,'Arial'))
        self.login_user.SetForegroundColour(wx.Colour(255, 255, 255))
        self.login_btn = wx.BitmapButton(p1, -1, wx.Bitmap(self.basedir+os.sep+'login_24.png'), style = wx.NO_BORDER)
        #
        sizer_top = wx.GridBagSizer()
        sizer_top.Add(logo, pos=(0,0), span=(2,1),flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, border=15)
        sizer_top.Add(st, pos=(0,1), span=(2,1),flag=wx.ALIGN_CENTER|wx.LEFT, border=10)
        sizer_top.Add(self.btn_min, pos=(0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_TOP|wx.ALL,border=-1)
        sizer_top.Add(self.btn_close, pos=(0,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_TOP|wx.ALL,border=-1)
        sizer_top.Add(self.login_user, pos=(1,3), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.ALL,border=-1)
        sizer_top.Add(self.login_btn, pos=(1,4), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.RIGHT,border=5)
        sizer_top.AddGrowableCol(2)
        sizer_top.AddGrowableRow(1)
        p1.SetSizer(sizer_top)

        # add statusbar
        self.statusbar = MyStatusBar(self, __version__)
        self.SetStatusBar(self.statusbar)

        # main panel
        main_panel = wx.Panel(p, -1)
        main_panel.SetBackgroundColour('white')
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        tools_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_btn = buttons.GenButton(main_panel, -1, '添加记录')
        self.add_btn.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        self.add_btn.SetBezelWidth(5)
        self.add_btn.SetMinSize((100, 35))
        self.add_btn.SetUseFocusIndicator(False)
        self.add_btn.SetBackgroundColour('#32CC32')
        self.add_btn.SetForegroundColour(wx.WHITE)
        self.modify_btn = buttons.GenButton(main_panel, -1, '修改')
        self.modify_btn.SetMinSize((70, 35))
        self.modify_btn.SetUseFocusIndicator(False)
        self.stop_btn = buttons.GenButton(main_panel, -1, '暂停')
        self.stop_btn.SetMinSize((70, 35))
        self.stop_btn.SetUseFocusIndicator(False)
        self.start_btn = buttons.GenButton(main_panel, -1, '启用')
        self.start_btn.SetMinSize((70, 35))
        self.start_btn.SetUseFocusIndicator(False)
        self.del_btn = buttons.GenButton(main_panel, -1, '删除')
        self.del_btn.SetMinSize((70, 35))
        self.del_btn.SetUseFocusIndicator(False)
        self.search = wx.SearchCtrl(main_panel, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.search.ShowSearchButton(True)
        self.search.ShowCancelButton(True)
        self.search.SetDescriptiveText('快速查找记录')

#        test_btn.SetF

        tools_sizer.Add(self.add_btn, 0, wx.ALL, 10)
        tools_sizer.Add(self.modify_btn, 0, wx.LEFT|wx.TOP, 10)
        tools_sizer.Add(self.stop_btn, 0, wx.TOP, 10)
        tools_sizer.Add(self.start_btn, 0, wx.TOP, 10)
        tools_sizer.Add(self.del_btn, 0, wx.TOP, 10)
        tools_sizer.Add((-1, -1), 1, wx.EXPAND)
        tools_sizer.Add(self.search, 0, wx.RIGHT|wx.TOP, 15)

        self.list = MyListCtrl(main_panel)

        main_sizer.Add(tools_sizer, 0, wx.EXPAND)
        main_sizer.Add(self.list, 1, wx.EXPAND)
        main_panel.SetSizer(main_sizer)

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.EXPAND)
        sizer.Add(main_panel, 1, wx.EXPAND)
        p.SetSizer(sizer)
        p.Fit()

        # show the frame
        self.Center()
        self.Show()

    def _IsNewPC(self):
        if sys.platform == 'win32':
            cur_name = md5(os.environ['COMPUTERNAME'])
            store_name = get_conf('perm', 'flag')
            if cur_name != store_name:
                clear_conf('db')
                set_conf('perm', 'flag', cur_name)

    def _IsAutoLogin(self):
        conf = ModifyConf(self.confdir+os.sep+'conf.ini')
        auto = conf.read('db', 'auto')
        if auto == 'True':
            user = conf.read('db', 'user')
            pwd = decrypt(16, conf.read('db', 'password'))
            try:
                self.ForAuto('', user, pwd)
                conf.write('db', **{'auth':True})
            except:
                self.in_or_out = 'in'
                conf.write('db', **{'auth':False})
                dlg = WarnDialog(self, '帐号、密码错误')
                dlg.CenterOnParent()
                dlg.ShowModal()
        else:
            conf.write('db', **{'auth':False})

    @call_thread
    def ForAuto(self, event, user, pwd):
        try:
            self.dnspod = dnspod_api(user=user,passwd=pwd,domain='yourdomain.com')
        except:
            self.in_or_out = 'in'
            wx.CallAfter(self.TipsDLG)
            return

        self.login_user.SetLabel(user)
        self.login_btn.SetBitmapLabel(wx.Bitmap(self.basedir+os.sep+'logout_24.png'))
        self.login_btn.Refresh()
        self.p1.Layout()
        self.in_or_out = 'out'
        self.get_dns_records()
        wx.CallAfter(self.ForWarnDLG)

    def TipsDLG(self):
        dlg = WarnDialog(self, '帐号、密码错误')
        dlg.CenterOnParent()
        dlg.ShowModal()

    def ForWarnDLG(self):
        self.tipdlg = WarnDialog2(self, '正在获取域名......')
        self.tipdlg.CenterOnParent()
        self.tipdlg.ShowModal()

    def _BindEvent(self):
        ##
        self.p1.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.p1.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.p1.Bind(wx.EVT_MOTION, self.OnMouseMove)
        ##
        self.Bind(wx.EVT_BUTTON, self.OnClickClose, self.btn_close)
        self.Bind(wx.EVT_BUTTON, self.OnClickMin, self.btn_min)
        #
        self.Bind(wx.EVT_BUTTON, self.OnLogin, self.login_btn)
        #
        self.Bind(wx.EVT_BUTTON, self.AddOne, self.add_btn)
        self.Bind(wx.EVT_BUTTON, self.ModifyItems, self.modify_btn)
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.stop_btn)
        self.Bind(wx.EVT_BUTTON, self.OnStart, self.start_btn)
        self.Bind(wx.EVT_BUTTON, self.DelItems, self.del_btn)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel ,self.search)
        self.Bind(wx.EVT_TEXT, self.OnSearchRT, self.search)

    def OnLeftDown(self, evt):#1 鼠标按下
        self.p1.CaptureMouse()
        pos = self.ClientToScreen(evt.GetPosition())
        origin = self.GetPosition()
        self.delta = wx.Point(pos.x - origin.x, pos.y - origin.y)

    def OnMouseMove(self, evt):#2 鼠标移动
        if evt.Dragging() and evt.LeftIsDown():
            pos = self.ClientToScreen(evt.GetPosition())
            newPos = (pos.x - self.delta.x, pos.y - self.delta.y)
            self.Move(newPos)

    def OnLeftUp(self, evt):#3 鼠标释放
        if self.p1.HasCapture():
            self.p1.ReleaseMouse()

    def OnClickClose(self, event):
        self.Close()
        self.Destroy()

    def OnClickMin(self, event):
        self.Iconize()

    def OnLogin(self, event):
        conf = ModifyConf(self.confdir+os.sep+'conf.ini')
        for k,v in conf.read_all('db'):
            self.data[k] = v
        if self.in_or_out == 'out':
            logout_dlg = LogoutDialog(self, '注销')
            logout_dlg.CenterOnParent()
            ret = logout_dlg.ShowModal()
            if ret == wx.ID_OK:
                self.in_or_out = 'in'
                self.is_auth = False
                self.data['auth'] = False
                conf.write('db', **self.data)
                self.login_user.SetLabel('')
                self.p1.Layout()
                self.login_btn.SetBitmapLabel(wx.Bitmap(self.basedir+os.sep+'login_24.png'))
                self.login_btn.Refresh()
            return

        self.data['password'] = decrypt(16, self.data['password'])
        self.login_dlg = LoginDialog(self,'登录',data=self.data)
        self.login_dlg.CenterOnParent()
        ret = self.login_dlg.Show()
        if ret == wx.ID_OK:
            try:
                self.dnspod = dnspod_api(user=self.data['user'],passwd=self.data['password'],domain='yourdomain.com')
            except:
                self.in_or_out = 'in'
                conf.write('db', **{'auth':False})
                dlg = WarnDialog(self, '帐号、密码错误')
                dlg.CenterOnParent()
                dlg.ShowModal()
                return
            if not self.data['save']:
                self.data['password'] = ''
            else:
                self.data['password'] = encrypt(16, self.data['password'])
            self.data['auth'] = True
            conf.write('db', **self.data)
            self.login_user.SetLabel(self.data['user'])
            self.p1.Layout()
            self.login_btn.SetBitmapLabel(wx.Bitmap(self.basedir+os.sep+'logout_24.png'))
            self.login_btn.Refresh()
            self.in_or_out = 'out'
            self.is_auth = True
            self.get_dns_records()
            self.tipdlg = WarnDialog2(self, '正在获取域名......')
            self.tipdlg.CenterOnParent()
            self.tipdlg.ShowModal()

    @call_thread
    def get_dns_records(self):
        try:
            all_record = []
            status = ''
            for offset in range(0,9000,3000):
#                print 'start%s' % offset
                (status,record_list) = self.dnspod.record_list(type='record',offset=offset)
                all_record.extend(record_list)
#                print len(record_list),'len'
#                if len(record_list)<3000:break
                status=status
            wx.CallAfter(self.list.fill_table, all_record, self.tipdlg)
        except:
            self.tipdlg.tip.SetLabel("蛋疼的DNSPOD，请求超时，正在重新获取！！！")
            self.tipdlg.main_sizer.Layout()
            self.tipdlg.main_sizer.Fit(self.tipdlg)
            self.tipdlg.CenterOnParent()
            self.tipdlg.Refresh()
            self.get_dns_records()

    def ModifyItems(self, event):
        count = len(self.list.check_list)
        if count == 0:
            dlg = WarnDialog(self, '请选择修改的域名！')
            dlg.CenterOnParent()
            dlg.ShowModal()
            return
        wx.CallAfter(self.list.PopupWindow, self.list.check_list, True, self.dnspod)

    def OnStop(self, event):
        count = len(self.list.check_list)
        if count == 0:
            dlg = WarnDialog(self, '请选择暂停的域名！')
            dlg.CenterOnParent()
            dlg.ShowModal()
            return
        dlg = WarnDialog(self, '确定暂停选中的 %s 个域名' % count, have_cancel_btn=True)
        dlg.CenterOnParent()
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            #do something delete dnspod record
            storelist = []
            for index in sorted(self.list.check_list, reverse=True):
                rec_id = self.list.GetItem(index, 5).GetText()
                code, res = self.dnspod.record_status(rec_id, status='disable')
                if code:
                    key = "%s|%s" % (self.list.GetItem(index, 0).GetText(), self.list.GetItem(index, 3).GetText())
                    v = [self.list.GetItem(index, i).GetText() for i in range(self.list.GetColumnCount()-1)]
                    v.append('0')
                    storelist.append(v)
                    self.list.DeleteItem(index)
                    self.list.storedata[key] = v
                    self.list.check_list.remove(index)
                else:
                    self.list.SetItemBackgroundColour(index, wx.Colour(255, 0, 0))
            for item in storelist:
                idx = self.list.InsertStringItem(0, item[0], it_kind=1)
                self.list.SetStringItem(idx, 1, item[1])
                self.list.SetStringItem(idx, 2, item[2])
                self.list.SetStringItem(idx, 3, item[3])
                self.list.SetStringItem(idx, 4, item[4])
                self.list.SetStringItem(idx, 5, item[5])
                self.list.SetStringItem(idx, 6, item[6])
                self.list.SetItemBackgroundColour(idx, wx.Colour(238,238,238))

    def OnStart(self, event):
        count = len(self.list.check_list)
        if count == 0:
            dlg = WarnDialog(self, '请选择开启的域名！')
            dlg.CenterOnParent()
            dlg.ShowModal()
            return
        dlg = WarnDialog(self, '确定开启选中的 %s 个域名' % count, have_cancel_btn=True)
        dlg.CenterOnParent()
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            #do something delete dnspod record
            storelist = []
            for index in sorted(self.list.check_list, reverse=True):
                rec_id = self.list.GetItem(index, 5).GetText()
                code, res = self.dnspod.record_status(rec_id, status='enable')
                if code:
                    key = "%s|%s" % (self.list.GetItem(index, 0).GetText(), self.list.GetItem(index, 3).GetText())
                    v = [self.list.GetItem(index, i).GetText() for i in range(self.list.GetColumnCount()-1)]
                    v.append('1')
                    storelist.append(v)
                    self.list.DeleteItem(index)
                    self.list.storedata[key] = v
                    self.list.check_list.remove(index)
                else:
                    self.list.SetItemBackgroundColour(index, wx.Colour(255, 0, 0))
            for item in storelist:
                idx = self.list.InsertStringItem(0, item[0], it_kind=1)
                self.list.SetStringItem(idx, 1, item[1])
                self.list.SetStringItem(idx, 2, item[2])
                self.list.SetStringItem(idx, 3, item[3])
                self.list.SetStringItem(idx, 4, item[4])
                self.list.SetStringItem(idx, 5, item[5])
                self.list.SetStringItem(idx, 6, item[6])

    def AddOne(self, event):
        wx.CallAfter(self.list.PopupWindow, '', '', self.dnspod)

    def DelItems(self, event):
        count = len(self.list.check_list)
        if count == 0:
            dlg = WarnDialog(self, '请选择删除的域名！')
            dlg.CenterOnParent()
            dlg.ShowModal()
            return
        dlg = WarnDialog(self, '确定删除选中的 %s 个域名' % count, have_cancel_btn=True)
        dlg.CenterOnParent()
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            #do something delete dnspod record
            for index in sorted(self.list.check_list, reverse=True):
                rec_id = self.list.GetItem(index, 5).GetText()
                code = self.dnspod.record_delete(rec_id)
                if code:
                    key = "%s|%s" % (self.list.GetItem(index, 0).GetText(), self.list.GetItem(index, 3).GetText())
                    self.list.storedata.pop(key)
                    self.list.DeleteItem(index)
                    self.list.check_list.remove(index)
                else:
                    self.list.SetItemBackgroundColour(index, wx.Colour(255, 0, 0))

    def OnSearch(self, event):
#        print self.search.GetValue()
        search_string = self.search.GetValue()
        self.list.DeleteAllItems()
        for key, value in sorted(self.list.storedata.iteritems(), key=lambda kv:(-int(kv[1][6]), kv[1][0])):
            if key.find(search_string) >= 0:
                index = self.list.InsertStringItem(sys.maxint, value[0], it_kind=1)
                self.list.SetStringItem(index, 1, value[1])
                self.list.SetStringItem(index, 2, value[2])
                self.list.SetStringItem(index, 3, value[3])
                self.list.SetStringItem(index, 4, value[4])
                self.list.SetStringItem(index, 5, value[5])
                if value[6] == '0':
                    self.list.SetItemBackgroundColour(index, wx.Colour(238,238,238))

    def OnCancel(self, event):
        self.search.Clear()

    def OnSearchRT(self, event):
        search_string = self.search.GetValue()
        if len(search_string) < 4:
            if len(self.list.storedata)>30:
                return
#        self.list.Freeze()
        self.list.DeleteAllItems()
        for key, value in sorted(self.list.storedata.iteritems(), key=lambda kv:(-int(kv[1][6]), kv[1][0])):
            if key.find(search_string) >= 0:
                index = self.list.InsertStringItem(sys.maxint, value[0], it_kind=1)
                self.list.SetStringItem(index, 1, value[1])
                self.list.SetStringItem(index, 2, value[2])
                self.list.SetStringItem(index, 3, value[3])
                self.list.SetStringItem(index, 4, value[4])
                self.list.SetStringItem(index, 5, value[5])
                if value[6] == '0':
                    self.list.SetItemBackgroundColour(index, wx.Colour(238,238,238))
#        self.list.Thaw()

class RedirectText(object):
    def __init__(self,aFile):
        self.out = aFile

    def openfile(self, string):
        with open(self.out, r'w') as f:
            f.write(string)

    def write(self,string):
#        self.openfile(string)
        wx.CallAfter(self.openfile, string)

class MyApp(wx.App):

    def __init__(self,redirect=True,filename=None):
        wx.App.__init__(self,redirect,filename)

    def OnInit(self):
        self.frame = MainFrame()
        return True

    def OnExit(self):
        os.kill(os.getpid(),SIGTERM)
        print 'OnExit'

if __name__ == "__main__":
    app = MyApp(redirect=False)
    app.MainLoop()
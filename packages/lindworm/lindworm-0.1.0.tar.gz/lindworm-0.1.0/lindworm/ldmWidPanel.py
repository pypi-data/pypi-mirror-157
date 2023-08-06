#----------------------------------------------------------------------------
# Name:         ldmWidPanel.py
# Purpose:      ldmWidPanel.py
#               GUI widget respond on size change
# Author:       Walter Obweger
#
# Created:      20200413
# CVS-ID:       $Id$
# Copyright:    (c) 2020 by Walter Obweger
# Licence:      MIT
#----------------------------------------------------------------------------

import wx
from lindworm.ldmWidCore import ldmWidCore
import lindworm.ldmGui as ldmGui

class ldmWidPanel(ldmWidCore):
    """wx panel widget abstraction, allows to add widgets
    by simply define a list of definition tuples at constructor in argument lWid.
    lWid=[
        (sCls, sName, sVal, sLnk),  # add widget
        (None),                     # add spacer wth size 5
    ],

    supported sCls identifiers:
        'lbl'   ... label, static text
        'gag'   ... gauge, sVal = max value; should be integer
        'txt'   ... text field, sVal text to set
        'txtLn' ... multiline text field, sVal text to set
        'txtRd' ... read only text field, sVal text to set
        'spn'   ... spin widget sVal= (val,(min,max))
        'lst'   ... list control
        'chc'   ... choice widget sVal=(val,[choice0,choice1, ... ,choiceN])
        'cb'    ... command button, sVal button label
        'cbBmp' ... bitmap command button, sVal defines bitmap to use
        'cbd'   ... command button browse directory (folder), sVal title
        'cbf'   ... command button browse file, sVal title, sLnk link
    """
    def getEvtDat(self,evt):
        """get event data
        data can be retrieved by id, which is already property of wx event object
        data can therefore by anything, and does not add to object size
        
        Args:
            evt (wid): wx event
        """
        try:
            # +++++ beg:
            iRet=0
            # ----- end:
            o=evt.GetEventObject()
            iId=evt.GetId()
            self.logDbg('getEvtWid iId:%d 0x%x',iId,iId)
            oDat=self.__getRegDat__(iId)
            return oDat
            w=o.FindTool(iId)
            return w
        except:
            self.logTB()
            return None
    def getFileOpen(self):
        """prepared for future implementation
        """
        try:
            # +++++ beg:
            iRet=0
            # ----- end:
            return iRet
        except:
            self.logTB()
            return -1
    def prcCmd(self,sCmd):
        """process command
        
        Args:
            sCmd (str): command to be processed
        """
        try:
            # +++++ beg:
            self.logDbg('ldmWidPanel::prcCmd sCmd:%r',sCmd)
            # ----- end:
            return 0
        except:
            self.logTB()
            return -1
    def OnCmd(self,evt):
        """GUI event handler

        Args:
            evt (wid): event object
        """
        evt.Skip()
        try:
            # +++++ beg:initialize
            oDat=self.getEvtDat(evt)
            self.logDbg('ldmWidPanel::OnCmd oDat:%r',oDat)
            iRet=self.prcCmd(oDat)
            self.logDbg('ldmWidPanel::OnCmd prcCmd iRet:%r',iRet)
            # ----- end:initialize
        except:
            self.logTB()
    def OnBwsDN(self,evt):
        """GUI event handler open dialog to brose for file system folder

        Args:
            evt (wid): event object
        """
        evt.Skip()
        try:
            # +++++ beg:initialize
            oDat=self.getEvtDat(evt)
            self.logDbg('ldmWidPanel::OnBwsDN oDat:%r',oDat)
            sWidName=oDat[0]
            sKind=oDat[1]
            # ----- end:initialize
            # +++++ beg:get widget and value
            wSub=getattr(self,sWidName)
            sOldDN=wSub.GetValue()
            # ----- end:get widget and value
            # +++++ beg:get DN
            iRet,sNewDN=ldmGui.getDN(sOldDN,self.GetWid(),
                        'choose source directory')
            # ----- end:get DN
            # +++++ beg:update data
            if iRet>0:
                wSub.SetValue(sNewDN)
                self.logDbg('fin:OnBwsDN iRet:%d %s:%s',
                            iRet,
                            sWidName,sNewDN)
            # ----- end:update data
        except:
            self.logTB()
    def OnBwsFN(self,evt):
        """GUI event handler open dialog to brose for file.

        Args:
            evt (wid): event object
        """
        evt.Skip()
        try:
            # +++++ beg:initialize
            oDat=self.getEvtDat(evt)
            self.logDbg('ldmWidPanel::OnBwsFN oDat:%r',oDat)
            iLenDat=len(oDat)
            sWidName=oDat[0]
            sKind=oDat[1]
            sWidLnk=None
            # ----- end:initialize
            # +++++ beg:get widget and value
            wSub=getattr(self,sWidName)
            sOldFN=wSub.GetValue()
            # ----- end:get widget and value
            # +++++ beg:get FN
            WILDCARD_JSON=[
                    "All files (*.*)|*.*",
                    "json file (*.json)|*.json",
                    "text file (*.txt)|*.txt",
                    "log file (*.log)|*.log",
                    "Excel file (*.xlsx)|*.xlsx",
                    "Excel file obsolete (*.xls)|*.xls",
                    ]

            iRet,sNewFN=ldmGui.getFN(sOldFN,self.GetWid(),
                        'choose file name',
                        lWildCard=WILDCARD_JSON)
            # ----- end:get FN
            # +++++ beg:update data
            if iRet>0:
                if iLenDat>2:
                    sWidLnk=oDat[2]
                if sWidLnk is not None:
                    # +++++ beg:handle linked widget, directory part
                    wLnk=getattr(self,sWidLnk)
                    sTmpDN,sTmpFN=ldmGui.getSplitFN(sNewFN)
                    if (sTmpDN is not None) and (sTmpFN is not None):
                        wLnk.SetValue(sTmpDN)
                        wSub.SetValue(sTmpFN)
                        self.log(0,'fin:OnBwsFN iRet:%d %s:%s %s:%s',
                                    iRet,
                                    sWidLnk,sTmpDN,
                                    sWidName,sTmpFN)
                    else:
                        self.logErr('sTmpDN:%r sTmpFN:%r',sTmpDN,sTmpFN)
                        wLnk.SetValue('')
                        wSub.SetValue(sNewFN)
                        self.logDbg('fin:OnBwsFN iRet:%d %s:%s',
                                    iRet,sWidName,sNewFN)
                    # ----- end:handle linked widget, directory part
                else:
                    wSub.SetValue(sNewFN)
                    self.logDbg('fin:OnBwsFN iRet:%d %s:%s',
                                iRet,sWidName,sNewFN)
            # ----- end:update data
        except:
            self.logTB()
    def __getRegDat__(self,iId):
        """get registered data by id;
        id equals widget id used on create
        each widget can have 1 data objects assigned
        
        Args:
            iID (int): identifier
        
        Returns
            obj: oDat , data object
               - None ... object not found
        """
        try:
            # +++++ beg:
            if iId in self.dIdDat:
                oDat=self.dIdDat[iId]
            else:
                oDat=None
            # ----- end:
            return oDat
        except:
            self.logTB()
            return None
    def __setRegDat__(self,oDat):
        """register object to widget,
        each widget can have 1 data object assigned,
        each widget utilizing GUI event handler should call method.
        after object is registered self.iId is incremented. 
        
        Args:
            oDat (obj): data object to register
        """
        try:
            # +++++ beg:
            self.logDbg('iId:%d oDat:%r',self.iId,oDat)
            self.dIdDat[self.iId]=oDat
            self.iId+=1
            # ----- end:
        except:
            self.logTB()
    def __bldWid__(self,tDef):
        """build widget
        
        Args:
            tDef (tuple): definition 
        """
        try:
            # +++++ beg:
            iExp=0
            iLen=len(tDef)
            sCls=tDef[0]
            if iLen>1:
                sName=tDef[1]
            else:
                sName=None
            if iLen>2:
                sVal=tDef[2]
            else:
                sVal=None
            if iLen>3:
                sLnk=tDef[3]
            else:
                sLnk=None
            self.logDbg('__bldWid__ tDef:%r',tDef)
            if sVal is None:
                sVal=''
            # ----- end:
            # +++++ beg:create widget
            wPar=self.GetWid()
            if sCls=='lbl':
                wSub=wx.StaticText(wPar, wx.ID_ANY, sVal)
            elif sCls=='gag':
                try:
                    iMax=int(sVal)
                except:
                    iMax=1000
                wSub=wx.Gauge(wPar, wx.ID_ANY, range=iMax,
                            size=(-1,8))
                iExp=1
            elif sCls=='txt':
                wSub=wx.TextCtrl(wPar, wx.ID_ANY, sVal)
                #self.Bind(wx.EVT_TEXT_ENTER, self.OnSrcDnEnter, self.txtSrcDN)
                iExp=1
            elif sCls=='txtLn':
                wSub=wx.TextCtrl(wPar, wx.ID_ANY, sVal,style=wx.TE_MULTILINE)
                iExp=1
            elif sCls=='txtRd':
                wSub=wx.TextCtrl(wPar, wx.ID_ANY, sVal,style=wx.TE_READONLY)
                iExp=1
            elif sCls=='spn':
                lLmt=sVal[1]
                wSub=wx.SpinCtrl(wPar, self.iId, sVal[0],
                                min=int(lLmt[0]), max=int(lLmt[-1]))
                self.__setRegDat__(sVal)
                iExp=1
            elif sCls=='lst':
                iStyle=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES
                wSub=wx.ListCtrl(wPar, self.iId,size=(80,40),style=iStyle)
                self.__setRegDat__(sVal)
                iExp=1
            elif sCls=='chc':
                lChc=sVal[1]
                wSub=wx.Choice(wPar, self.iId,choices=lChc)
                try:
                    iIdx=lChc.index(sVal[0])
                    wSub.SetSelection(iIdx)
                except:
                    wSub.SetSelection(0)
                self.__setRegDat__(sVal)
                iExp=1
            elif sCls=='cb':
                wSub=wx.Button(wPar, self.iId, sVal)
                self.__setRegDat__(sVal)
                wPar.Bind(wx.EVT_BUTTON, self.OnCmd, wSub)
            elif sCls=='cbBmp':
                wSub=wx.BitmapButton(wPar, self.iId, sVal)
                self.__setRegDat__(sLnk)
                wPar.Bind(wx.EVT_BUTTON, self.OnCmd, wSub)
            elif sCls=='cbd':       # directory
                wSub=wx.Button(self.GetWid(), self.iId, '...')
                self.__setRegDat__((sVal,'browse_dir'))
                wPar.Bind(wx.EVT_BUTTON, self.OnBwsDN, wSub)
            elif sCls=='cbf':       # file open
                wSub=wx.Button(wPar, self.iId, '...')
                self.__setRegDat__((sVal,'browse_file_open',sLnk))
                wPar.Bind(wx.EVT_BUTTON, self.OnBwsFN, wSub)
            else:
                wSub=None
            # ----- end:create widget
            # +++++ beg:set widget as attribute
            if wSub is not None:
                if sName is not None:
                    if getattr(self,sName,None) is None:
                        setattr(self,sName,wSub)
                    else:
                        self.logErr('sName:%s already used'%(sName))
            # ----- end:set widget as attribute
            return wSub,iExp
        except:
            self.logTB()
            return None,0
    def __initCls__(self,**kwargs):
        """class initializer, set self.clsWid to wxPython class

        Args:
            kwargs (dict): flexible keyword arguments
        """
        self.clsWid=wx.Panel
    def __initWid__(self,**kwargs):
        """initialize widget
        create container widget self.clsWid (provided by __initCls__),
        create sizer object by calling method __initSizer__ and
        add widgets defined by kwargs lWid, list of tuples to be fed
        into __bldWid__, sub widget is added to sizer object.
        
        Args:
            lWid (list): list of tuples to define sub widgets

        """
        try:
            # +++++ beg:
            self.iId=1000
            self.dIdDat={}
            self.oSzMain=None
            self.logDbg('__initWid__')
            style=wx.TAB_TRAVERSAL
            _args,_kwargs=self.GetWidArgs(kwargs,
                        ['id','name','parent','pos','size','style'],
                        {'pos':(0,0),'size':(-1,-1),'style':style})
            self.wid=self.clsWid(*_args,**_kwargs)
            self.__initSizer__(**kwargs)
            # ----- end:
            # +++++ beg:
            #self.logDbg('check lWid')
            lWid=kwargs.get('lWid',None)
            if lWid is not None:
                for tDef in lWid:
                    #self.logDbg('build')
                    #self.logDbg('build %r',tDef)
                    wSub,iExp=self.__bldWid__(tDef)
                    iR=self.__addSizerWid__(tDef,wSub,iExp)
            # ----- end:
        except:
            self.logTB()
    def __initSizer__(self,**kwargs):
        """initialize sizer, horizontal box sizer is used
        to respond to widget resizing.
        
        Args:
            kwargs (dict): keyword arguments
        """
        try:
            bDbg=self.GetVerboseDbg(20)
            if bDbg:
                self.logDbg('__initLayout__')
            self.oSzMain=wx.BoxSizer(wx.HORIZONTAL)
        except:
            self.logTB()
    def __addSizerWid__(self,tDef,wSub,iExp):
        """add sub widget to sizer object
        
        Args:
            tDef (tuple): widget definition tuple
            wSub (wid): wx widget
            iExp (int): widget expand directive for sizer
        """
        try:
            iRet=0
            if wSub is None:
                self.oSzMain.AddSpacer(5)
            else:
                if iExp<=0:
                    self.oSzMain.Add(wSub,0,0,0)
                else:
                    self.oSzMain.Add(wSub,iExp,wx.EXPAND,0)
        except:
            self.logTB()
    def __initLayout__(self,**kwargs):
        """initialize layout
        finally sizer object has to be assigned to widget.
        method is called by base class.
        
        Args:
            kwargs (dict): keyword arguments
        """
        try:
            bDbg=self.GetVerboseDbg(20)
            if bDbg:
                self.logDbg('__initLayout__')

            if self.oSzMain is not None:
                self.wid.SetSizer(self.oSzMain)
                self.wid.Layout()
        except:
            self.logTB()

class ldmWidPanelVert(ldmWidPanel):
    def __initSizer__(self,**kwargs):
        """initialize sizer, vertical box sizer is used
        to respond to widget resizing.
        
        Args:
            kwargs (dict): keyword arguments
        """
        try:
            bDbg=self.GetVerboseDbg(20)
            if bDbg:
                self.logDbg('__initLayout__')
            self.oSzMain=wx.BoxSizer(wx.VERTICAL)
        except:
            self.logTB()

class ldmWidPanelFlxGrd(ldmWidPanel):
    def __initSizer__(self,**kwargs):
        """initialize sizer, flexible grid sizer is used
        to respond to widget resizing.
        
        Args:
            kwargs (dict): key word arguments
                - iRow : number of rows
                - iCol : number of columns
        """
        try:
            bDbg=self.GetVerboseDbg(20)
            if bDbg:
                self.logDbg('__initLayout__')
            iRow=kwargs.get('iRow',None)
            iCol=kwargs.get('iCol',2)

            if iRow is not None:
                self.oSzMain=wx.FlexGridSizer(iRow, iCol, 0, 0)
            else:
                self.oSzMain=wx.FlexGridSizer(iCol, 0, 0)
        except:
            self.logTB()
    def __initLayout__(self,**kwargs):
        """initialize layout
        finally sizer object has to be assigned to widget.
        method is called by base class.
        
        Args:
            kwargs (dict): key word arguments
                - lRow ,, list of growable rows
                - lCol .. list of growable columns
        """
        try:
            bDbg=self.GetVerboseDbg(20)
            if bDbg:
                self.logDbg('__initLayout__')
            if self.oSzMain is not None:
                lCol=kwargs.get('lCol',None)
                if lCol is not None:
                    for iCol in lCol:
                        self.oSzMain.AddGrowableCol(iCol)
                lRow=kwargs.get('lRow',None)
                if lRow is not None:
                    for iRow in lRow:
                        self.oSzMain.AddGrowableRow(iRow)
                self.wid.SetSizer(self.oSzMain)
                self.wid.Layout()
        except:
            self.logTB()


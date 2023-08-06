#----------------------------------------------------------------------------
# Name:         ldmWidTree.py
# Purpose:      ldmWidTree.py
#               GUI widget respond on size change
# Author:       Walter Obweger
#
# Created:      20200405
# CVS-ID:       $Id$
# Copyright:    (c) 2020 by Walter Obweger
# Licence:      MIT
#----------------------------------------------------------------------------

import wx

import six

import lindworm.ldmTypes as ldmTypes
from lindworm.ldmWidCore import ldmWidCore
from lindworm.ldmWidImgLst import ldmWidImgLstGet

class ldmWidTree(ldmWidCore):
    """tree widget shell to harmonize widget interface
    and ease usage.
    keyword arguments:
        bTreeButtons    ... tree buttons
        bHideRoot       ... hide root
        multiple_sel    ... multiple list item selection; 0|1
        imgLst          ... image list
        map             ... mapping dictionary
    __initCfg__ modify widget configuration
        _bTreeButtons   ... default False
        _bHideRoot      ... default False
        _bMultiple      ... tree item selection mode; default=False
    """
    def __initCls__(self,**kwargs):
        """initialize class
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        self.clsWid=wx.TreeCtrl
    def __initCfg__(self,**kwargs):
        """initialize configuration
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidTree::__initCfg__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            ldmWidCore.__initCfg__(self,**kwargs)
            # +++++ beg:
            self._bTreeButtons=False
            self._bHideRoot=False
            self._bMultiple=False
            self._bSort=False
            self.FORCE_CHILDREN=False
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
    def __initObj__(self,**kwargs):
        """initialize object properties, widgets aren't present yet.
        data is supposed to be related to widgets or support their
        function.
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidTree::__initObj__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            self.IMG_EMPTY=-1
            self.iDat=1 #20200421 wro:py3 1L
            self.dDat={}
            self.dCache={}
            if kwargs.get('bTreeButtons',1)>0:
                self._bTreeButtons=True
            else:
                self._bTreeButtons=False
            if kwargs.get('bHideRoot',False)>0:
                self._bHideRoot=True
            else:
                self._bHideRoot=False
            if kwargs.get('multiple_sel',0)==0:
                self._bMultiple=False
            else:
                self._bMultiple=True
            if kwargs.get('single_sel',False)>0:
                self._bMultiple=False
            if kwargs.get('bSort',0)==1:
                self._bSort=True
            self.FORCE_CHILDREN=kwargs.get('bForceChildren',False)
            # ----- end:
            # +++++ beg:
            self._funcVal=None
            self._argsVal=()
            self._kwargsVal={}
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
    def __initWid__(self,**kwargs):
        """initialize widgets
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
                - bTreeButtons : >0 set style to have buttons
                - bHideRoot    : >0 set style to hide root element
                - multiple_sel : >0 set style to multiple selection
                - imgLst       : image list
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidTree::__initWid__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            style=0
            self.IMG_EMPTY=-1
            if self._bTreeButtons==True:
                style|=wx.TR_HAS_BUTTONS
            if self._bHideRoot==True:
                style|=wx.TR_HIDE_ROOT
            if self._bMultiple==True:
                style|=wx.TR_MULTIPLE
            _args,_kwargs=self.GetWidArgs(kwargs,
                        ['id','name','parent','pos','size','style'],
                        {'pos':(0,0),'size':(-1,-1),'style':style})
            self.wid=self.clsWid(*_args,**_kwargs)

            self.BindEvent('trCtrlAct',self.OnItemActivate)
            self.CB(self.BindEvent,'trCtrlCollapsing',self.OnItemCollapsing)
            #if self._bSort:
            #    self.CB(self.BindEvent,'trCtrlExpanding,self.OnItemSort)
        except:
            self.logTB()
        try:
            bDbg=self.GetVerboseDbg(10)
            if bDbg:
                self.logDbg('')
            self._dImg=None
            self._imgLst=None
            # ++++ beg:
            imgLst=kwargs.get('imgLst',None)
            if imgLst is not None:
                if type(imgLst)==ldmTypes.StringType:
                    w,bImgLstCreated=ldmWidImgLstGet(imgLst,oLog=self)
                    if w is not None:
                        self._sImgLst=imgLst
                        dImg0,imgLst0=w.GetObjs()
                        self.SetImageListByDict(dImg0,imgLst0)
            if self._imgLst is None:
                w,bImgLstCreated=ldmWidImgLstGet(self.__class__.__name__,
                                    dft='tree',oLog=self)
                if w is not None:
                    self._sImgLst=None
                    self._bImgLstCreated=bImgLstCreated
                    dImg0,imgLst0=w.GetObjs()
                    self.SetImageListByDict(dImg0,imgLst0)
            self.__initImageLst__()
            # ---- end:
            # ++++ beg:setup mapping
            oTmp=kwargs.get('map',None)
            if oTmp is not None:
                self.MAP=oTmp
            # ---- end:setup mapping
        except:
            self.logTB()
    def __initPrp__(self,**kwargs):
        """initialize properties, supposed to be related to widgets.
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        
        Returns:
            wid::: widget
        """
        wid=None
        try:
            # +++++ beg:initialize
            sOrg='ldmWidTree::__initPrp__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            # ----- end:
            # +++++ beg:assign values
            oTmp=kwargs.get('value',None)
            if oTmp is not None:
                self.SetValue(oTmp)
            # ----- end:assign values
            # +++++ beg:
            tFunc=kwargs.get('funcValue',None)
            if tFunc is not None:
                self.SetFuncValue(tFunc[0],*tFunc[1],**tFunc[2])
                oThd=ldmWidCore.__getThread__(self,'tree')
                if kwargs.get('build',True):
                    self.CB(self.Build)
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
        return wid
    def _getImgLstObj(self):
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            w,bFlag=ldmWidImgLstGet(self._sImgLst or self.__class__.__name__,dft='tree')
            return w
        except:
            self.logTB()
        return w
    def GetTreeEvtDat(self,evt):
        """GUI event handler

        Args:
            evt (wid): event object
        """
        try:
            if self.IsMainThread()==False:
                return
            bDbg=self.GetVerboseDbg(8)
            if bDbg:
                self.logDbg('')
            if evt is None:
                return None
            ti=evt.GetItem()
            tr=evt.GetEventObject()
            if ti.IsOk():
                dat=tr.GetItemData(ti)            #tr.GetPyData(ti)
                txt=tr.GetItemText(ti)
                v={ 'dat':dat,
                    'lbl':txt,
                    }
                return v
        except:
            self.logTB()
        return None
    def OnItemActivate(self,evt):
        """GUI event handler

        Args:
            evt (wid): event object
        """
        try:
            if self.IsMainThread()==False:
                return
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            self.Post('exec',self.GetTreeEvtDat(evt))
            if evt is not None:
                evt.Skip()
        except:
            self.logTB()
    def _prcBuild(self,tr,ti,idx,dDat,bExpand):
        """process build

        Args:
            tr (wid): widget
            ti (wid): tree item
            idx (int): index
            dDat (dict): data
            bExpand (bool): expand tree item
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            
            iR=self._funcVal(idx,dDat,*self._argsVal,**self._kwargsVal)
            self.logDbg({'iR':iR,'dDat':dDat})
            if iR<=0:
                return
            #self.__setValue__(tr,ti,dDat)
            #if ti is None:
            #    ti=tr.AddRoot('')
            #tc=tr.AppendItem(ti,'')
            self.CB(self.__setTreeItem__,tr,ti,dDat)
            if bExpand:
                self.CB(tr.Expand,ti)
        except:
            self.logTB()
    def _build(self,tr,ti,bExpand=False):
        """process build

        Args:
            tr (wid): widget
            ti (wid): tree item
            bExpand (bool): expand tree item
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            oThd=ldmWidCore.__getThread__(self,'tree')
            #oThd.DoWX
            #tr.Freeze()
            idx=None
            dDat={}
            if ti is not None:
                if ti.IsOk():
                    idx=tr.GetItemData(ti)            #tr.GetPyData(ti)
                    t=self.GetItemTup(ti,0)
                    dDat[-1]=idx
                    if t is not None:
                        dDat[0]=t[1]
                        dDat[1]=t[0]
            #else:
            #    ti=tr.AddRoot('')
            oThd.Do(self._prcBuild,tr,ti,idx,dDat,bExpand)
            #oThd.Do(self._funcVal,*self._argsVal,**self._kwargsVal)
        except:
            self.logTB()
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            #tr.Thaw()
        except:
            self.logTB()
        return ti
    def OnItemSort(self,evt):
        """GUI event handler

        Args:
            evt (wid): event object
        """
        try:
            if self.IsMainThread()==False:
                return
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            ti=evt.GetItem()
            tr=self.wid
            bC=tr.ItemHasChildren(ti)
            if bC:
                tr.SortChildren(ti)
        except:
            self.logTB()
    def OnItemExpanding(self,evt):
        """GUI event handler

        Args:
            evt (wid): event object
        """
        try:
            if self.IsMainThread()==False:
                return
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            dEvt=self.GetTreeEvtDat(evt)
            if bDbg:
                self.logDbg(dEvt)
            if evt is None:
                return None
            else:
                evt.Skip()
            ti=evt.GetItem()
            tr=self.wid
            bC=tr.ItemHasChildren(ti)
            if bC:
                tc,ck=tr.GetFirstChild(ti)
                if tc.IsOk():
                    pass
                else:
                    self._build(tr,ti,bExpand=True)
        except:
            self.logTB()
    def OnItemCollapsing(self,evt):
        """GUI event handler

        Args:
            evt (wid): event object
        """
        try:
            if self.IsMainThread()==False:
                return
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            if evt is None:
                return None
            ti=evt.GetItem()
            tr=self.wid
            if tr.GetRootItem()==ti:
                evt.Veto()
            else:
                evt.Skip()
        except:
            self.logTB()
    def SetFuncValue(self,func,*args,**kwargs):
        """set function value

        Args:
            func (callable): callable
            args (list): arguments
            kwargs (dict): keyword arguments
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            self._funcVal=func
            self._argsVal=args
            self._kwargsVal=kwargs
            wid=self.wid
            self.CB(wid.Bind,wx.EVT_TREE_ITEM_EXPANDING,self.OnItemExpanding)
        except:
            self.logTB()
    def Build(self,idx=None):
        """build

        Args:
            idx (int , optional): index
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            if idx is not None:
                ti=self.dCache[idx]
            else:
                ti=None
                self.CB(self.Clear)
            #tc=self._build(self.wid,ti)
            self.CB(self._build,self.wid,ti)
        except:
            self.logTB()
    def BindEvent(self,name,func,par=None):
        """bind event

        Args:
            name (string): event name
            func (callable): callback
            par (wid , optional): parent widget
        """
        if name.startswith('tr_'):
            wid=self.GetWid()
            if name in ['tr_item_sel','tr_item_selected']:
                self.logWrn('change name:%s to %s',name,'trCtrlExpanding')
                ldmWidCore.BindEvent(self,'trCtrlExpanding',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_SELECTED,func, par or wid)
            elif name in ['tr_item_desel','tr_item_deselected']:
                self.logWrn('change name:%s to %s',name,'trCtrlDesel')
                ldmWidCore.BindEvent(self,'trCtrlDesel',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_DESELECTED,func, par or wid)
            elif name in ['tr_item_act','tr_item_activated']:
                self.logWrn('change name:%s to %s',name,'trCtrlAct')
                ldmWidCore.BindEvent(self,'trCtrlAct',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_ACTIVATED,func, par or wid)
            elif name in ['tr_item_del','tr_item_delete']:
                self.logWrn('change name:%s to %s',name,'trCtrlDel')
                ldmWidCore.BindEvent(self,'trCtrlDel',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_DELETE,func, par or wid)
            elif name in ['tr_item_clg','tr_item_collapsing']:
                self.logWrn('change name:%s to %s',name,'trCtrlCollapsing')
                ldmWidCore.BindEvent(self,'trCtrlCollapsing',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_COLLAPSING,func, par or wid)
            elif name in ['tr_item_cld','tr_item_collapsed']:
                self.logWrn('change name:%s to %s',name,'trCtrlCollapsed')
                ldmWidCore.BindEvent(self,'trCtrlCollapsed',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_COLLAPSED,func, par or wid)
            elif name in ['tr_item_exg','tr_item_expanding']:
                self.logWrn('change name:%s to %s',name,'trCtrlExpanding')
                ldmWidCore.BindEvent(self,'trCtrlExpanding',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_EXPANDING,func, par or wid)
            elif name in ['tr_item_exd','tr_item_expanded']:
                self.logWrn('change name:%s to %s',name,'trCtrlExpanded')
                ldmWidCore.BindEvent(self,'trCtrlExpanded',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_EXPANDED,func, par or wid)
            elif name in ['tr_item_selg','tr_item_sel_changing']:
                self.logWrn('change name:%s to %s',name,'trCtrlSelChg')
                ldmWidCore.BindEvent(self,'trCtrlSelChg',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_SEL_CHANGING,func, par or wid)
            elif name in ['tr_item_seld','tr_item_selchanged']:
                self.logWrn('change name:%s to %s',name,'trCtrlSel')
                ldmWidCore.BindEvent(self,'trCtrlSel',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_SEL_CHANGED,func, par or wid)
            elif name in ['tr_item_right_click','tr_item_rgClk']:
                self.logWrn('change name:%s to %s',name,'trCtrlRclk')
                ldmWidCore.BindEvent(self,'trCtrlRclk',func,par=par)
                #wid.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,func, par or wid)
            elif name in ['tr_drag_begin']:
                self.logWrn('change name:%s to %s',name,'trCtrlDragBeg')
                ldmWidCore.BindEvent(self,'trCtrlDragBeg',func,par=par)
                #wid.Bind(wx.EVT_TREE_BEGIN_DRAG,func, par or wid)
            elif name in ['tr_drag_right_begin']:
                self.logWrn('change name:%s to %s',name,'trCtrlDragBegRg')
                ldmWidCore.BindEvent(self,'trCtrlDragBegRg',func,par=par)
                #wid.Bind(wx.EVT_TREE_BEGIN_RDRAG,func, par or wid)
            elif name in ['tr_drag_end']:
                self.logWrn('change name:%s to %s',name,'trCtrlDragEnd')
                ldmWidCore.BindEvent(self,'trCtrlDragEnd',func,par=par)
                #wid.Bind(wx.EVT_TREE_END_DRAG,func, par or wid)
            elif name in ['tr_key_click']:
                self.logWrn('change name:%s to %s',name,'lstCtrlColClkLf')
                ldmWidCore.BindEvent(self,'lstCtrlColClkLf',func,par=par)
                #wid.Bind(wx.EVT_LIST_COL_LEFT_CLICK,func, par or wid)
            elif name=='tr_col_right_click':
                self.logWrn('change name:%s to %s',name,'lstCtrlColClkRg')
                ldmWidCore.BindEvent(self,'lstCtrlColClkRg',func,par=par)
                #wid.Bind(wx.EVT_LIST_COL_RIGHT_CLICK,
                #        func, par or wid)
            else:
                self.logErr('not implemented yet name:%s',name)
        else:
            ldmWidCore.BindEvent(self,name,func,par=par)
    def GetImg(self,sTag,sFB):
        """get image

        Args:
            sTag (str): name
            sFB (str): fallback name
        """
        try:
            if self._dImg is not None:
                iImg=self._dImg.get(sTag,None)
                if iImg is None:
                    iImg=self._dImg.get(sFB,-1)
                return iImg
        except:
            self.logTB()
        return -1
    def __initImageLst__(self):
        """initialize image list
        """
        try:
            bDbg=self.GetVerboseDbg(10)
            if bDbg:
                self.logDbg('')
            
        except:
            self.logTB()
    def SetImageListByDict(self,dImg,imgLst,which=None):
        """set image list by dictionary

        Args:
            dImg (dict): image definition
            imgLst (wid): image list
            which (wid , optional)
        """
        try:
            if self.IsMainThread()==False:
                return
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            
            if imgLst is not None:
                self.IMG_EMPTY=dImg.get('empty',0)
                #iImgSortAsc=dImg.get('asc',-1)
                #iImgSortDesc=dImg.get('desc',-1)
            self.wid.SetImageList(imgLst)
            self._dImg,self._imgLst=dImg,imgLst
        except:
            self.logTB()
    def EnsureVisibleIdx(self,iIdx):
        """ensure index to be visible

        Args:
            iIdx (int): index
        """
        try:
            if iIdx in self.dCache:
                ti=self.dCache[iIdx]
                self.CB(self.wid.EnsureVisible,ti)
        except:
            self.logTB()
    def ExpandIdx(self,iIdx):
        """expand index

        Args:
            iIdx (int): index
        """
        try:
            if iIdx in self.dCache:
                ti=self.dCache[iIdx]
                self.CB(self.wid.Expand,ti)
        except:
            self.logTB()
    def _delete(self,tr,ti):
        """delete item

        Args:
            tr (wid): widget
            ti (wid): tree item
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            l=[]
            self.__getValue__(tr,ti,None,[-1],l)
            iIdx=l[0][0]
            if bDbg:
                self.logDbg({'l':l,'iIdx':iIdx,
                        'iIdxIn':iIdx in self.dCache})
            if iIdx in self.dCache:
                del self.dCache[iIdx]
        except:
            self.logTB()
        return 1
    def Delete(self,ti):
        """delete item

        Args:
            ti (wid): tree item
        """
        try:
            if self.IsMainThread()==False:
                return
            tr=self.wid.GetRootItem()
            if ti==tr:
                self.DeleteAllItems()
                return 
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('walk through children')
            self.__walk__(self.wid,ti,self._delete)
            if bDbg:
                self.logDbg('delete ti now')
            self._delete(self.wid,ti)
            self.wid.Delete(ti)
        except:
            self.logTB()
    def DelIdx(self,iIdx):
        """delete index

        Args:
            iIdx (int): index
        """
        try:
            if iIdx in self.dCache:
                ti=self.dCache[iIdx]
                del self.dCache[iIdx]
                self.CB(self.Delete,ti)
        except:
            self.logTB()
    def DelSelected(self):
        """delete selected
        """
        try:
            lSel=self.GetSelected([-2,-1])
            self.logDbg(lSel)
            lSel.reverse()
            for t in lSel:
                self.DelIdx(t[1])
        except:
            self.logTB()
    def DeleteAllItems(self):
        """delete all items
        """
        try:
            bDbg=self.GetVerboseDbg(5)
            if bDbg:
                self.logDbg('')
            if self.IsMainThread()==False:
                return
            self.widCls.DeleteAllItems(self.wid)
            self.dCache={}
        except:
            self.logTB()
    ClearAll=DeleteAllItems
    Clear=DeleteAllItems
    def __getTreeItemByHier__(self,tr,ti,lHier):
        """get tree item by hierarchy

        Args:
            tr (wid): widget
            ti (wid): tree item
            lHier (list): hierarchy
        """
        #self.logDbg('verbose :%d dbg:%r',self.GetVerbose(),self.GetVerboseDbg(0))
        bDbg=self.GetVerboseDbg(10)
        if bDbg:
            self.logDbg('hier:%r ti lbl:%r lHier:%s',lHier[0],tr.GetItemText(ti),
                    '.'.join(lHier))
        if lHier[0]==tr.GetItemText(ti):
            if len(lHier)>1:
                t=tr.GetFirstChild(ti)
                while t[0].IsOk():
                    if lHier[1]==tr.GetItemText(t[0]):        # reduce method calls
                        r=self.__getTreeItemByHier__(tr,t[0],lHier[1:])
                        if r is not None:
                            return r
                    t=tr.GetNextChild(ti,t[1])
                return None                                 # exact hierarchy match
            return ti
        return None
    def __setTreeItemDict__(self,tr,ti,d):
        """set tree item by dictionary

        Args:
            tr (wid): widget
            ti (wid): tree item
            d (dict): dictionary
        """
        #print tr.GetItemText(ti,0)
        for s,i in self.MAP:
            if i>0:
                continue
            if s in d:
                v=d[s]
                t=type(v)
                if t==ldmTypes.TupleType:
                    #tr.SetItemText(ti,v[0],i)
                    #tr.SetItemImage(ti,v[1],i,which=wx.TreeItemIcon_Normal)
                    tr.SetItemText(ti,v[0])
                    tr.SetItemImage(ti,v[1],which=wx.TreeItemIcon_Normal)
                elif t==ldmTypes.IntType:
                    #tr.SetItemImage(ti,v,i,which=wx.TreeItemIcon_Normal)
                    tr.SetItemImage(ti,v,which=wx.TreeItemIcon_Normal)
                else:
                    #tr.SetItemText(ti,v,i)
                    tr.SetItemText(ti,v)
                    
                    tr.SetItemImage(ti,self.IMG_EMPTY,which=wx.TreeItemIcon_Normal)
        bSkipImg=True
        if 0 in d:
            img=d[0]
            t=type(img)
            if t==ldmTypes.IntType:
                bSkipImg=False
            elif t==ldmTypes.StringType:
                if self._dImg is not None:
                    img=self.GetImg(img,'empty')
                    bSkipImg=False
            if bSkipImg==False:
                tr.SetItemImage(ti,img,which=wx.TreeItemIcon_Normal)
        if bSkipImg==True:
            tr.SetItemImage(ti,self.IMG_EMPTY,which=wx.TreeItemIcon_Normal)
        if -1 in d:
            v=d[-1]
            tr.SetItemData(ti,v)          #tr.SetPyData(ti,v)
            self.dCache[v]=ti
        if -2 in d:
            v=d[-2]
            if v is None:
                tr.SetItemHasChildren(ti,True)
            else:
                if self._bSort:
                    t=type(v[0])
                    if t==ldmTypes.DictType:
                        def cmpDict(a,b):
                            try:
                                for s,i in self.MAP:
                                    return cmp(a.get(s,None),b.get(s,None))
                            except:
                                pass
                            return 0
                        v.sort(cmpDict)
                self.__setValue__(tr,ti,v)
    def __setTreeItemLst__(self,tr,ti,l):
        """set tree item by list

        Args:
            tr (wid): widget
            ti (wid): tree item
            l (list): list
        """
        try:
            if l[0] is not None:
                tr.SetItemData(ti,l[0])         #tr.SetPyData(ti,l[0])
                self.dCache[l[0]]=ti
            i=0
            for v in l[1]:
                if i>0:
                    continue
                t=type(v)
                if t==ldmTypes.TupleType:
                    tr.SetItemText(ti,v[0])
                    tr.SetItemImage(ti,v[1],which=wx.TreeItemIcon_Normal)
                elif t==ldmTypes.IntType:
                    tr.SetItemImage(ti,v,which=wx.TreeItemIcon_Normal)
                else:
                    tr.SetItemText(ti,v)
                    tr.SetItemImage(ti,self.IMG_EMPTY,which=wx.TreeItemIcon_Normal)
                i+=1
            iLen=len(l)
            if iLen>2:
                self.__setValue__(tr,ti,l[2])
        except:
            self.logTB()
            self.__logError__({'l':l,'l[0]':l[0],'l[1]':l[1]})
    def __setTreeItemTup__(self,tr,ti,t):
        """set tree item tuple

        Args:
            tr (wid): widget
            ti (wid): tree item
            t (tuple): value to set
        """
        pass
    def __setTreeItem__(self,tr,ti,val):
        """set tree item

        Args:
            tr (wid): widget
            ti (wid): tree item
            val (obj): object
        """
        if ti is None:
            ti=tr.AddRoot('')
            self.CB(tr.Expand,ti)
        self.logDbg(val)
        t=type(val)
        if t==ldmTypes.DictType:
            self.__setTreeItemDict__(tr,ti,val)
        elif t==ldmTypes.ListType:
            self.__setTreeItemLst__(tr,ti,val)
        elif t==ldmTypes.TupleType:
            self.__setTreeItemTup__(tr,ti,val)
    def __setValue__(self,tr,tp,l,bRoot=False):
        """set value
        
        Args:
            tr (wid): widget
            ti (wid): tree item
            l (tuple): value to set
            bRoot (bool , optional): root element
        """
        for ll in l:
            if tp is None:
                ti=tr.AddRoot('')
            else:
                ti=tr.AppendItem(tp,'')
            if self.FORCE_CHILDREN:
                tr.SetItemHasChildren(ti,True)
            self.__setTreeItem__(tr,ti,ll)
            if tp is None:
                #if self._bSort:
                #    tr.SortChildren(ti)
                return
            #if self._bSort:
            #    tr.SortChildren(ti)
    def __getValue__(self,tr,ti,lHier,lMap,l):
        """get value
        
        """
        try:
            bDbg=self.GetVerboseDbg(10)
            if bDbg:
                self.logDbg({'lHier':lHier,'lMap':lMap,'l':l})
            
            def getVal(tr,ti,lHier,i):
                if i is None:
                    return lHier
                if i==-1:
                    try:
                        return tr.GetItemData(ti)     #tr.GetPyData(ti)
                    except:
                        return None
                elif i==-2:
                    return ti
                else:
                    if i==0:
                        try:
                            return tr.GetItemText(ti)
                        except:
                            return u''
                    else:
                        return u''
                    #return tr.GetItemText(ti,i)
            l.append([getVal(tr,ti,lHier,i) for i in lMap])
            return 1
        except:
            self.logTB()
        return 0
    def __getValueData__(self,tr,ti,l):
        try:
            data=tr.GetItemData(ti)       #tr.GetPyData(ti)
        except:
            data=None
        l.append(data)
        # 20150123 wro: catch exception and add data always
        #   this method is call also on multiple selections enabled
        #if data is not None:
        #    l.append(data)
    def __getSelectionSng__(self,tr):
        l=[]
        def cmpSel(tr,ti,iMpdSub,l):
            if tr.IsSelected(ti):
                l.append(ti)
                return 1
            return 0
        iRet=tr.WalkDeepFirst(cmpSel,l)
        if iRet>0:
            return False,l[0]
        return False,None
    def __getSelectionMulti__(self,tr):
        l=[]
        def cmpSel(tr,ti,iMpdSub,l):
            if tr.IsSelected(ti):
                l.append(ti)
            return 0
        iRet=tr.WalkDeepFirst(cmpSel,l)
        if len(l)>0:
            return True,l
        return True,[]
    def __walkFind__(self,tr,ti,func,*args,**kwargs):
        if ti.IsOk()==False:
            return None
        t=tr.GetFirstChild(ti)
        while t[0].IsOk():
            if func(tr,t[0],*args,**kwargs):
                return t[0]
            if tr.ItemHasChildren(t[0]):
                r=self.__walkFind__(tr,t[0],func,*args,**kwargs)
                if r is not None:
                    return r
            t=tr.GetNextChild(ti,t[1])
        return None
    def __walk__(self,tr,ti,func,*args,**kwargs):
        if ti.IsOk()==False:
            return 0
        t=tr.GetFirstChild(ti)
        while t[0].IsOk():
            iRet=func(tr,t[0],*args,**kwargs)
            if iRet<0:
                return iRet
            if tr.ItemHasChildren(t[0]):
                iRet=self.__walk__(tr,t[0],func,*args,**kwargs)
                if iRet<0:
                    return iRet
            t=tr.GetNextChild(ti,t[1])
        return 0
    def __walkHier__(self,tr,ti,lHier,func,*args,**kwargs):
        bDbg=self.GetVerboseDbg(5)
        
        if ti.IsOk()==False:
            return 0
        t=tr.GetFirstChild(ti)
        while t[0].IsOk():
            #lH=lHier+[tr.GetItemText(t[0],0)]
            lH=lHier+[tr.GetItemText(t[0])]
            iRet=func(tr,t[0],lH,*args,**kwargs)
            if bDbg:
                self.logDbg({'lH':lH,'lHier':lHier,'iRet':iRet})
            if iRet<0:
                return iRet
            if tr.ItemHasChildren(t[0]):
                iRet=self.__walkHier__(tr,t[0],lH,func,*args,**kwargs)
                if bDbg:
                    self.logDbg({'lH':lH,'lHier':lHier,'iRet':iRet})
                if iRet<0:
                    return iRet
            t=tr.GetNextChild(ti,t[1])
        return 0
    def __walkDeepFirst__(self,tr,ti,iMod,func,*args,**kwargs):
        if ti.IsOk()==False:
            return iMod
        t=tr.GetFirstChild(ti)
        iModRet=iMod
        while t[0].IsOk():
            if tr.ItemHasChildren(t[0]):
                iRet=self.__walkDeepFirst__(tr,t[0],iMod,func,*args,**kwargs)
                if iRet<0:
                    return iRet
                iModSub=max(iRet,iMod)
            else:
                iModSub=iMod
            iModRet=max(iModSub,iModRet)
            iRet=func(tr,t[0],iModSub,*args,**kwargs)
            if iRet<0:
                return iRet
            iModRet=max(iRet,iModRet)
            t=tr.GetNextChild(ti,t[1])
        return iModRet
    def __walkBreathFirst__(self,tr,ti,iLimit,func,*args,**kwargs):
        if ti.IsOk()==False:
            return None
        t=tr.GetFirstChild(ti)
        while t[0].IsOk():
            ret=func(tr,t[0],*args,**kwargs)
            if ret>0:
                return t[0]
            elif ret<0:
                return None
            t=tr.GetNextChild(ti,t[1])
        if iLimit>0:
            t=tr.GetFirstChild(ti)
            while t[0].IsOk():
                if tr.ItemHasChildren(t[0]):
                    r=self.__walkBreathFirst__(tr,t[0],iLimit-1,func,*args,**kwargs)
                    if r is not None:
                        return r
                t=tr.GetNextChild(ti,t[1])
        return None
    def WalkDeepFirst(self,func,*args,**kwargs):
        try:
            if self.IsMainThread()==False:
                return None
            ti=self.wid.GetRootItem()
            iRet=func(self,ti,0,*args,**kwargs)
            if iRet!=0:
                return iRet
            return self.__walkDeepFirst__(self.wid,ti,0,func,*args,**kwargs)
        except:
            self.logTB()
        return None
    def WalkBreathFirst(self,ti,iLimit,func,*args,**kwargs):
        try:
            if self.IsMainThread()==False:
                return None
            if ti is None:
                ti=self.wid.GetRootItem()
            return self.__walkBreathFirst__(self.wid,ti,iLimit,func,*args,**kwargs)
        except:
            self.logTB()
        return None
    def Walk(self,func,*args,**kwargs):
        try:
            if self.IsMainThread()==False:
                return
            self.__walk__(self.wid,self.GetRootItem(),func,*args,**kwargs)
        except:
            self.logTB()
    def WalkHier(self,ti,lHier,func,*args,**kwargs):
        try:
            if self.IsMainThread()==False:
                return
            if ti is None:
                ti=self.wid.GetRootItem()
            if lHier is None:
                tp=ti
                lHier=[]
                while tp is not None:
                    lHier.append(self.GetItemText(tp,0))
                    tp=self.GetItemParent(tp)
                    if tp.IsOk()==False:
                        break
                lHier.reverse()
                
            self.__walkHier__(self.wid,ti,lHier,func,*args,**kwargs)
        except:
            self.logTB()
    def WalkFind(self,ti,func,*args,**kwargs):
        try:
            if self.IsMainThread()==False:
                return None
            if ti is None:
                ti=self.wid.GetRootItem()
            return self.__walkFind__(self.wid,ti,func,*args,**kwargs)
        except:
            self.logTB()
        return None
    def WalkSel(self,func,*args,**kwargs):
        try:
            if self.IsMainThread()==False:
                return
            lTi=self.GetSelections()
            for ti in lTi:
                self.__walk__(self.wid,ti,func,*args,**kwargs)
                func(self,ti,*args,**kwargs)
        except:
            self.logTB()
    def WalkSelDeepFirst(self,func,*args,**kwargs):
        try:
            if self.IsMainThread()==False:
                return -1
            lTi=self.GetSelections()
            iMod=0
            for ti in lTi:
                iRet=self.__walkDeepFirst__(self.wid,ti,0,func,*args,**kwargs)
                if iRet<0:
                    return iRet
                iMod=max(iRet,iMod)
                iRet=func(self,ti,iMod,*args,**kwargs)
                if iRet<0:
                    return iRet
                iMod=max(iRet,iMod)
            return iMod
        except:
            self.logTB()
        return None
    def GetItemTup(self,ti,iKind):
        try:
            #bDbg=self.GetVerboseDbg(5)
            #if bDbg:
            #    self.logDbg('')
            if self.IsMainThread()==False:
                return None
            if ti.IsOk()==False:
                return None
            tr=self.wid
            if iKind==-1:
                return tr.GetItemData(ti)         #tr.GetPyData(ti)
            elif iKind<0:
                return None
            elif iKind==0:
                return (tr.GetItemText(ti),tr.GetItemImage(ti))
            else:
                return None
        except:
            self.logTB()
        return None
    def __getItemStr__(self,tr,ti,iKind):
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            
            if ti.IsOk()==False:
                return None
            tr=self.wid
            if iKind==-1:
                return tr.GetItemData(ti)         #tr.GetPyData(ti)
            elif iKind<0:
                return None
            elif iKind==0:
                return tr.GetItemText(ti)
            else:
                return None
        except:
            self.logTB()
    def GetItemStr(self,ti,iKind):
        try:
            #bDbg=self.GetVerboseDbg(5)
            #if bDbg:
            #    self.logDbg('')
            if self.IsMainThread()==False:
                return None
            return self.__getItemStr__(self.wid,ti,iKind)
        except:
            self.logTB()
        return None
    def GetSelections(self):
        try:
            if self.IsMainThread()==False:
                return []
            l=self.wid.GetSelections()
            bDbg=self.GetVerboseDbg(5)
            if bDbg:
                self.logDbg(l)
            return l
        except:
            self.logTB()
        return []
    def GetSelected(self,lMap=None):
        try:
            self.logDbg(''%())
            if self.IsMainThread()==False:
                return None
            l=self.GetValue(lMap=lMap or [-1,None],ti=-1)
            return l
        except:
            self.logTB()
        return None
    def __setSelected__(self,tr,ti,dSel,iKind,bFlag,lSelTi):
        try:
            bDbg=self.GetVerboseDbg(5)
            if bDbg:
                self.logDbg('')
            v=self.__getItemStr__(tr,ti,iKind)
            if v is None:
                self.__logError__('tree item invalid')
            else:
                if v in dSel:
                    dSel[v]=dSel[v]+1
                    if bDbg:
                        self.__logDebugAdd__('select',{'v':v})
                    tr.SelectItem(ti,bFlag)
                    lSelTi.append(ti)
                    if self._bMultiple==False:
                        return -1
        except:
            self.logTB()
        return 0
    def SetSelected(self,lSel,iKind=-1,ti=None,bFlag=True,bKeepSel=False,bEnsure=True):
        try:
            bDbg=self.GetVerboseDbg(5)
            if bDbg:
                self.logDbg({'bEnsure':bEnsure,'iKind':iKind,
                        'bFlag':bFlag,'bKeepSel':bKeepSel,
                        'lSel':lSel,})
            else:
                self.logDbg(''%())
            if self.IsMainThread()==False:
                return -2
            tr=self.wid
            if ti is None:
                ti=tr.GetRootItem()
            if self._bMultiple==True:
                if bKeepSel==False:
                    lSelTi=self.GetSelected([-2])
                    for tiOld in lSelTi:
                        if bDbg:
                            self.__logDebugAdd__('deselect',{'tiOld':tiOld})
                        tr.SelectItem(tiOld[0],False)
        except:
            self.logTB()
        try:
            dSel={}
            lSelTi=[]
            lSelKey=[]
            for iK in lSel:
                if iK in dSel:
                    self.__logError__(['key already present',iK])
                else:
                    dSel[iK]=0
                    lSelKey.append(iK)
                    if self._bMultiple==False:
                        break
            #dSel[None]=0
            if iKind==-1:
                for iK in lSel:
                    if iK in self.dCache:
                        ti=self.dCache[iK]
                        if bDbg:
                            self.__logDebugAdd__('select',{'iK':iK})
                        tr.SelectItem(ti,bFlag)
                        lSelTi.append(ti)
                        if self._bMultiple==False:
                            break
            else:
                self.__walk__(tr,ti,self.__setSelected__,dSel,iKind,bFlag,lSelTi)
            bDbg=self.GetVerboseDbg(5)
            if bDbg:
                self.logDbg({'bEnsure':bEnsure,
                        'lSel':lSel,'lSelKey':lSelKey,'lSelTi':lSelTi})
            if bEnsure:
                if len(lSelTi)>0:
                    tr.EnsureVisible(lSelTi[0])
            return lSelKey
            return lSelTi
            #return self.__setSelected__(lst,l,bFlag=bFlag)
        except:
            self.logTB()
        return -1
    def SetValue(self,l,lHier=None,bChildren=False):
        """set value
        ### parameter
            l       ... values to set, dictionary or list
            lHier   ... hierarchy (list of label) to find tree item or tree item
            bChildren . data considered to be child
        ### return
              3 ... set children values
              2 ... add child value
              1 ... set value
             -1 ... exception
             -2 ... called by thread
            -10 ...hierarchy nor found
        """
        try:
            bDbg=self.GetVerboseDbg(5)
            if bDbg:
                self.logDbg('')
            if self.IsMainThread()==False:
                return -2
            
            tr=self.wid
            #iCols=tr.GetColumnCount()
            
            if lHier is None:
                tr.DeleteAllItems()
                ti=tr.AddRoot('')
                if self._bHideRoot:
                    self.__setValue__(tr,ti,l)
                else:
                    self.__setTreeItem__(tr,ti,l)
                    tr.Expand(ti)
                #self.__setValue__(tr,None,l)
            else:
                if type(lHier)==ldmTypes.ListType:
                    ti=self.__getTreeItemByHier__(tr,tr.GetRootItem(),lHier)
                    if ti is None:
                        self.logErr('%s;ti not found'%('.'.join(lHier)))
                        return -10
                else:
                    ti=lHier
                if bChildren==True:
                    if type(l)==ldmTypes.ListType:
                        self.__setValue__(tr,ti,l)
                        return 3
                    else:
                        tc=tr.AppendItem(ti,'')
                        self.__setTreeItem__(tr,tc,l)
                        return 2
                else:
                    self.__setTreeItem__(tr,ti,l)
                    return 1
        except:
            self.logTB()
            return -1
    def __getHier__(self,tr,ti,l,r):
        #l.append(tr.GetItemText(ti,0))
        if self._bHideRoot:
            if ti==r:
                return
        if ti.IsOk():
            l.append(tr.GetItemText(ti))
            tp=tr.GetItemParent(ti)
            self.__getHier__(tr,tp,l,r)
    def GetHier(self,ti):
        """get hierarchy of tree element
        ### parameter
            ti      ... tree item to retrieve
        ### return
            lst ... list of labels
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            if self.IsMainThread()==False:
                return None
            l=[]
            if self._bHideRoot:
                r=self.wid.GetRootItem()
            else:
                r=None
            self.__getHier__(self.wid,ti,l,r)
            l.reverse()
            return l
        except:
            self.logTB()
        return None
    def GetValue(self,lMap=None,ti=None):
        """get value data mapped to specific information
        ### parameter
            lMap    ... mapping definition
                -2  ... tree item (wxTreeItem)
                -1  ... data
                0   ... label
            ti      ... tree item to retrieve
                None .. entire tree
        ### return
            lst ... list of mapped element data
        """
        try:
            if self.IsMainThread()==False:
                return None
            bDbg=self.GetVerboseDbg(5)
            self.logDbg(''%())
            l=[]
            tr=self.wid
            if ti is None:
                ti=tr.GetRootItem()
                #if self._bHideRoot:
                #    self.__logError__('well this is kind of stupid')
            elif type(ti)!=ldmTypes.IntType:
                if lMap is None:
                    self.__getValueData__(tr,ti,l)
                else:
                    lH=self.GetHier(ti)
                    self.__getValue__(tr,ti,lH,lMap,l)
                if bDbg:
                    self.logDbg(l)
                return l
                
            elif ti==-1:
                lTi=self.GetSelections()
                for ti in lTi:
                    if lMap is None:
                        self.__getValueData__(tr,ti,l)
                    else:
                        lH=self.GetHier(ti)
                        self.__getValue__(tr,ti,lH,lMap,l)
                if bDbg:
                    self.logDbg(l)
                return l
            if lMap is None:
                self.__getValueData__(tr,ti,l)
                self.__walk__(tr,ti,self.__getValueData__,l)
            else:
                lH=self.GetHier(ti)
                if bDbg:
                    self.logDbg({'lH':lH,'ti':ti,
                            'r':self.wid.GetRootItem()})
                self.__getValue__(tr,ti,lH,lMap,l)
                self.__walkHier__(tr,ti,lH,
                                self.__getValue__,lMap,l)
            if bDbg:
                self.logDbg(l)
            return l
        except:
            self.logTB()
        return None

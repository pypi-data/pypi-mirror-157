#----------------------------------------------------------------------------
# Name:         ldmWidList.py
# Purpose:      ldmWidList.py
#               GUI widget respond on size change
# Author:       Walter Obweger
#
# Created:      20200405
# CVS-ID:       $Id$
# Copyright:    (c) 2020 by Walter Obweger
# Licence:      MIT
#----------------------------------------------------------------------------

import sys
import wx

import six

import lindworm.ldmTypes as ldmTypes
from lindworm.ldmWidCore import ldmWidCore

class ldmWidList(ldmWidCore):
    """list control widget shell to harmonize widget interface
    and ease usage.
    keyword arguments:
        lCol            ... column definition
        single_sel      ... single list item selection; 0|1
        multiple_sel    ... multiple list item selection; 0|1
    __initCfg__ modify widget configuration
        _bMultiple      ... list item selection mode; default=False
    """
    def __initCls__(self,**kwargs):
        """initialize class
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        self.clsWid=wx.ListCtrl
    def __initCfg__(self,**kwargs):
        """initialize configuration
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidList::__initCfg__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            ldmWidCore.__initCfg__(self,**kwargs)
            # +++++ beg:
            self._bMultiple=False
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
            sOrg='ldmWidList::__initObj__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            self.IMG_EMPTY=-1
            self.iDat=1 #20200421 wro:py3 1L
            self.dDat={}
            if kwargs.get('multiple_sel',0)==0:
                self._bMultiple=False
            else:
                self._bMultiple=True
            if kwargs.get('single_sel',False)>0:
                self._bMultiple=False
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
                lCol ... column formating
                    [
                        (100,'l),       # 100 pixel, left alignment
                        (200,'lf),      # 200 pixel, left alignment
                        (100,'c),       # 100 pixel, center alignment
                        (200,'ct),      # 200 pixel, center alignment
                        (100,'r),       # 100 pixel, right alignment
                        (200,'rg),      # 200 pixel, right alignment
                        (-1,'l),        # growable factor 1, left alignment
                        (-2,'lf),       # growable factor 2, left alignment
                    ],
                map ... mapping
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidList::__initWid__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES
            if self._bMultiple==False:
                style|=wx.LC_SINGLE_SEL
            _args,_kwargs=self.GetWidArgs(kwargs,
                        ['id','name','parent','pos','size','style'],
                        {'pos':(0,0),'size':(-1,-1),'style':style})
            self.wid=self.clsWid(*_args,**_kwargs)
            self._it=wx.ListItem()
            # ----- end:
            # +++++ beg:setup columns
            lCol=kwargs.get('lCol',None)
            if lCol is not None:
                for tCol in lCol:
                    if tCol[1] in ['l','lf']:
                        fmt=wx.LIST_FORMAT_LEFT
                    elif tCol[1] in ['r','rg']:
                        fmt=wx.LIST_FORMAT_RIGHT
                    elif tCol[1] in ['c','ct']:
                        fmt=wx.LIST_FORMAT_CENTER
                    else:
                        fmt=wx.LIST_FORMAT_LEFT
                    self.wid.AppendColumn(tCol[0],
                                    format=fmt,
                                    width=tCol[2])
            # ----- end:setup columns
        except:
            self.logTB()
        try:
            # +++++ beg:setup mapping
            oTmp=kwargs.get('map',None)
            if oTmp is not None:
                self.MAP=oTmp
            else:
                self.MAP=None
            # ----- end:setup mapping
            # +++++ beg:
            self._dImg=None
            self._imgLst=None
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
    def SetItem(self,idx,i,v):
        """set list column item
        
        Args:
            idx (int): index 
            i (int): column
                - <0  ... data
                - >=0 ... column
            v (obj): value
                - integer value, interpreted as image index
                - tuple, t[0] string value, t[1] image index
                - string or unicode value, image cleared
        
        Returns:
            return code
                - >0 : okay 
                - =0 : okay nop
                - <0 : error
        """
        try:
            if self.IsMainThread()==False:
                return -2
            if i<0:
                i=self.wid.GetItemData(idx)
                i=self.__add_data__(v,i)
                self.wid.SetItemData(idx,i)
                return 0
            t=type(v)
            if t==ldmTypes.TupleType:
                self.wid.SetStringItem(idx,i,v[0],v[1])
            elif t==ldmTypes.IntType:
                self.wid.SetStringItem(idx,i,u'',v)
            else:
                self.wid.SetStringItem(idx,i,v,-1)
            return 0
        except:
            self.logTB()
    def GetItemTup(self,idx,i):
        """get item value
        
        Args:
            idx (int): row index
            i (int): column
                - -1  ... data
                - -3  ... data key
                - <0  ... None
                - >=0 ... column value as tuple, string and image index
        
        Returns:
            obj or tuple
                item text

                item image identifier


        """
        try:
            if self.IsMainThread()==False:
                return None
            if i==-1:
                i=self.wid.GetItemData(idx)
                if i>0:
                    return self.dDat.get(i,None)
                return None
            elif i==-3:
                return self.wid.GetItemData(idx)
            elif i<0:
                return None
            it=self.wid.GetItem(idx,i)
            t=(it.GetText()[:],it.GetImage())
            return t
        except:
            self.logTB()
    def GetItemStr(self,idx,i):
        """get item string

        Args:
            idx (int): index
            i (int): column
                - -1  ... data
                - -3  ... data key
                - <0  ... None
                - >=0 ... column value as tuple, string and image index

        Returns:
            obj or item text
        """
        try:
            if self.IsMainThread()==False:
                return None
            if i==-1:
                i=self.wid.GetItemData(idx)
                if i>0:
                    return self.dDat.get(i,None)
                return None
            elif i==-3:
                return self.wid.GetItemData(idx)
            elif i<0:
                return None
            it=self.wid.GetItem(idx,i)
            return it.GetText()[:]
        except:
            self.logTB()
    def GetCount(self):
        """get row count

        Returns:
            int: item count
        """
        try:
            if self.IsMainThread()==False:
                return -1
            return self.wid.GetItemCount()
        except:
            self.logTB()
    def __add_data__(self,data,i=0):
        """add data to cache
        
        Args:
            data (obj): object to cache
            i (int): key
                - 0   ... use attribute iDat
        """
        try:
            if i==0:
                i=self.iDat
                self.iDat+=1
            self.dDat[i]=data
            return i
        finally:
            pass
        return -1
    def SetDictMap(self,lMap):
        """set MAP property to be used item set by dictionary 
        
        Args:
            lMap (list): mapping list of tuples keys to column number
                - key 0 : bitmap index (integer) or name (string)
                - key -1 : data to be cached and referenced to list item
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('SetDictMap')
            self.MAP=lMap
        except:
            self.logTB()
    def __setItemDict__(self,lst,idx,d):
        """set item by dictionary defined by property MAP
        
        Args:
            lst (wid): widget
            idx (int): row
            d (dict): dictionary values, property MAP used
        """
        #print tr.GetItemText(ti,0)
        for s,i in self.MAP:
            if s in d:
                v=d[s]
                t=type(v)
                if t==ldmTypes.TupleType:
                    lst.SetStringItem(idx,i,v[0],v[1])
                elif t==ldmTypes.IntType:
                    lst.SetStringItem(idx,i,u'',v)
                else:
                    lst.SetStringItem(idx,i,v,-1)
        if 0 in d:
            self._it.Clear()
            img=d[0]
            bSkipImg=True
            t=type(img)
            if t==ldmTypes.IntType:
                self._it.SetImage(img)
                bSkipImg=False
            elif t==ldmTypes.StringType:
                if self._dImg is not None:
                    self._it.SetImage(self._dImg[img])
                    bSkipImg=False
            if bSkipImg==False:
                self._it.SetMask(wx.LIST_MASK_IMAGE)
                self._it.SetId(idx)
                lst.SetItem(self._it)
                #lst.SetItem(idx,self._it)
        if -1 in d:
            i=lst.GetItemData(idx)
            i=self.__add_data__(d[-1],i)
            lst.SetItemData(idx,i)
        #if -2 in d:
        #    self.__setValue__(tr,ti,d[-2])
    def __setItemLst__(self,lst,idx,l):
        """set item by list
        
        Args:
            lst (wid): widget
            idx (int): row
            l (list): list values, data and column values
        """
        try:
            if l[0] is not None:
                i=self.wid.GetItemData(idx)
                i=self.__add_data__(l[0],i)
                lst.SetItemData(idx,i)
            i=0
            for v in l[1]:
                t=type(v)
                if t==ldmTypes.TupleType:
                    lst.SetItem(idx,i,v[1]) #v[0],
                elif t==ldmTypes.IntType:
                    lst.SetItem(idx,i,u'')# v is image
                else:
                    lst.SetItem(idx,i,v)
                i+=1
        except:
            self.logTB()
            self.__logError__('l:%r;l[0]:%r;l[1]:%r'%(l,
                    l[0],l[1]))
    def __setItemTup__(self,tr,ti,t):
        """
        Args:
            tr (wid): widget
            ti (wid): tree item
            t (tuple): tuple
        """
        pass
    def __setItem__(self,lst,idx,val):
        """set item, various types. are handled
        
        Args:
            lst (wid): widget
            idx (int): row
            val (obj): values, dictionary or list
        """
        t=type(val)
        if t==ldmTypes.DictType:
            self.__setItemDict__(lst,idx,val)
        elif t==ldmTypes.ListType:
            self.__setItemLst__(lst,idx,val)
        elif t==ldmTypes.TupleType:
            self.__setItemTup__(lst,idx,val)
    def __setValue__(self,lst,l,idx=-1):
        """set value
        
        Args:
            lst (wid): widget
            l (list): list of values, dictionary or list
            idx (int): row
        """
        if idx<0:
            idx=0
        iCnt=lst.GetItemCount()
        for val in l:
            if idx>=iCnt:
                idx=lst.InsertItem(idx,'',self.IMG_EMPTY)
                iCnt+=1
            self.__setItem__(lst,idx,val)
            idx+=1
        return idx-1
    def __getValue__(self,lst,idx,lMap,l):
        """get item value
        
        Args:
            lst (wid): widget
            idx (int): row
            lMap (list): list of columns to get
                - None, delivers [-2]
                - >=0 ... text of column
                - -1  ... cached data
                - -2  ... index
                - -3  ... cache key
            l (list): list of values to return
        """
        def getVal(lst,idx,i):
            """

            Args:
                lst (wid): widget
                idx (int): index
                i (int): column
            """
            if i==-1:
                i=lst.GetItemData(idx)
                if i>0:
                    return self.dDat.get(i,None)
                return None
            elif i==-2:
                return idx
            elif i==-3:
                return lst.GetItemData(idx)
            else:
                it=lst.GetItem(idx,i)
                return it.GetText()[:]
        if lMap is None:
            l.append(getVal(lst,idx,-2))
        else:
            l.append([getVal(lst,idx,i) for i in lMap])
    def __getValueData__(self,lst,idx,l):
        """get value data
        
        Args:
            lst (wid): widget
            idx (int): row
            l (list): list of values to return
        """
        i=lst.GetItemData(idx)
        if i>0:
            l.append(self.dDat.get(i,None))
    def __insert__(self,lst,l,idx=-1):
        """insert
        
        Args:
            lst (wid): widget
            l (list): list of data and values to insert
            idx (int): row
                - -1 : insert at the end
        
        Returns:
            - >0 : okay processing done
            - =0 : okay nop
            - <0 : error
            - -1 : exception
            - -3 : l is None
        """
        try:
            if l is None:
                return -3
            if idx<0:
                idx=lst.GetItemCount()
                for val in l:
                    idx=lst.InsertItem(idx+1,'')
                    self.__setItem__(lst,idx,val)
            else:
                idx-=1
                for val in l:
                    idx+=1
                    idx=lst.InsertItem(idx,'',self.IMG_EMPTY)
                    self.__setItem__(lst,idx,val)
            return idx
        except:
            self.logTB()
        return -1
    def Insert(self,l,idx=-1):
        """insert
        
        Args:
            l (wid): list of data and values to insert
            idx (int): row
                - -1 : insert at the end
        
        Returns:
            return code
              - >0 : okay processing done
              - =0 : okay nop
              - <0 : error
              - -1 : exception
              - -2 : not called from main thread
              - -3 : l is None
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('Insert')
            if self.IsMainThread()==False:
                return -2
            w=self.wid
            return self.__insert__(w,l,idx=idx)
        except:
            self.logTB()
        return -1
    def SetValue(self,l,idx=-1):
        """set value
        
        Args:
            l (wid): list of data and values to set
            idx (int): row
                - >=0 : item index to start set, in case more
                        items are delivered to set, 
                - -1 : clear items
        
        Returns:
            return code
                - >0 : okay processing done
                - =0 : okay nop
                - <0 : error
                - -1 : exception
                - -2 : not called from main thread
                - -3 : l is None
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('SetValue')
            if self.IsMainThread()==False:
                return -2
            w=self.wid
            #iCols=w.GetColumnCount()
            iRet=-2
            if idx==-1:
                w.DeleteAllItems()
                iRet=self.__insert__(w,l,idx=idx)
            else:
                iRet=self.__setValue__(w,l,idx=idx)
            #self.Sort()
            return iRet
        except:
            self.logTB()
        return -1
    def GetValue(self,lMap=None,idx=None):
        """get value
        
        Args:
            lMap (list): list of columns to get
                - None: cached data
                - >=0 : text of column
                - -1  : cached data
                - -2  : index
                - -3  : cache key
            idx     ... row
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('GetValue')
            if self.IsMainThread()==False:
                return None
            l=[]
            lst=self.wid
            if idx is None:
                idx=0
                iCnt=-1
            elif idx<0:
                idx=0
                iCnt=-1
            else:
                iCnt=1
            if iCnt<0:
                iCnt=lst.GetItemCount()
            if lMap is None:
                for i in six.moves.xrange(idx,idx+iCnt):
                    self.__getValueData__(lst,i,l)
            else:
                for i in six.moves.xrange(idx,idx+iCnt):
                    self.__getValue__(lst,i,lMap,l)
            if bDbg:
                self.logDbg('GetValue:%r',l)
            return l
        except:
            self.logTB()
        return None
    def PrcFct(self,idx,bDbg,fct,*args,**kwargs):
        """process function on item
        
        Args:
            idx (int): index
            bDbg (bool): debugging flag
            fct (callable): callable applied on each item in addition
                        to args and kwargs following values are passed
                - iOfs : current processing number starting at 0
                - iCnt : total number of calls
                - iIdx : item index
            args (list): arguments
            kwargs (dict): keyword arguments
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('PrcFct iIdx:%r args:%r kwargs:%r',idx,args,kwargs)
            lst=self.wid
            if idx is None:
                idx=0
                iCnt=-1
            elif idx<0:
                idx=0
                iCnt=-1
            else:
                iCnt=1
            if iCnt<0:
                iCnt=lst.GetItemCount()
            if bDbg:
                self.logDbg('iCnt:%d iIdx:%d',iCnt,idx)
            iOfs=0
            for i in six.moves.xrange(idx,idx+iCnt):
                if bDbg:
                    self.logDbg('iOfs:%d-%d iIdx:%d',iOfs,iCnt,i)
                iRet=fct(iOfs,iCnt,i,*args,**kwargs)
                if iRet<=0:
                    return iRet
                iOfs+=1
            return 1
        except:
            self.logTB()
            return -1
    def __setState__(self,lst,l,bFlag,iState):
        """set state
        
        Args:
            lst (wid): widget
            l (list): list of index
            bFlag (bool): flag
            iState (int): item status
        """
        try:
            iCnt=lst.GetItemCount()
            iIdxFirst=-1
            if bFlag==True:
                if l is None:
                    pass
                else:
                    if self._bMultiple==False:      # 20150727 wro:single sel 
                        lst.SetItemState(l[0],iState,iState)
                        return l[0]
                    for i in l:
                        lst.SetItemState(i,iState,iState)
                        if iIdxFirst<0:
                            iIdxFirst=i
                    return iIdxFirst
            else:
                if l is None:
                    for i in six.moves.xrange(iCnt):
                        lst.SetItemState(i,0,iState)
                        if iIdxFirst<0:
                            iIdxFirst=i
                    return iIdxFirst
                else:
                    for i in l:
                        lst.SetItemState(i,0,iState)
                        if iIdxFirst<0:
                            iIdxFirst=i
                    return iIdxFirst
            return 0
        except:
            self.logTB()
        return -1
    def __setSelected__(self,lst,l,bFlag):
        """set selected status
        
        Args:
            lst (wid): widget
            l (list): list of index
            bFlag (bool): flag
        """
        return self.__setState__(lst,l,bFlag,wx.LIST_STATE_SELECTED)
    def __getState__(self,lst,lMap,l,iState):
        """get item values with state set
        
        Args:
            lst (wid): widget
            lMap (list): list of columns to get
                - None: delivers [-2]
                - >=0 : text of column
                - -1  : cached data
                - -2  : index
                - -3  : cache key
            l (list): list of values to return
            iState (int): state
        
        Returns:
            number of items matching state
        """
        try:
            iCnt=lst.GetItemCount()
            iSel=0
            for i in six.moves.xrange(0,iCnt):
                if (lst.GetItemState(i,iState)&iState)==iState:
                    self.__getValue__(lst,i,lMap,l)
                    iSel+=1
            return iSel
        except:
            self.logTB()
        return -1
    def __getSelected__(self,lst,lMap,l):
        """get selected item values
        
        Args:
            lst (wid): widget
            lMap (list): list of columns to get
                - None: delivers [-2]
                - >=0 : text of column
                - -1  : cached data
                - -2  : index
                - -3  : cache key
            l (list): list of values to return
        
        Returns:
            number of items matching state
        """
        return self.__getState__(lst,lMap,l,wx.LIST_STATE_SELECTED)
    def SetSelected(self,l,bFlag=True,lMapChk=None,bKeepSel=False,bEnsure=True):
        """set selected
        ### parameter
            l       ... dictionary

            bFlag   ... flag, True or False
            lMapChk ... mapping 
                if check is None, and l is dictionary lMapChk is constructed
                    integer keys are added
                    keys found in MAP property
            bKeepSel .. keep selected
            bEnsure ... ensure first selected to be visible
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('SetSelected')
            bDb0=self.GetVerboseDbg(0)
            bDbg=self.GetVerboseDbg(10)
            if self.IsMainThread()==False:
                return -2
            lst=self.wid
            if self._bMultiple==True:
                if bKeepSel==False:
                    lSel=[]
                    self.__getSelected__(lst,None,lSel)
                    self.__setSelected__(lst,lSel,bFlag=False)
            t=type(l)
            if t==ldmTypes.DictType:
                if lMapChk is None:
                    lKeys=l.keys()
                    lMapChk=[]
                    ll=[]
                    for sK in lKeys:
                        if type(sK)==ldmTypes.IntType:
                            lMapChk.append(sK)
                            ll.append(l[sK])
                        else:
                            try:
                                bFound=False
                                for tM in self.MAP:
                                    if tM[0]==sK:
                                        lMapChk.append(tM[1])
                                        bFound=True
                                        break
                                if bFound==True:
                                    ll.append(l[sK])
                                else:
                                    self.logErr('mapping faulty %r',
                                            {'sK':sK,'MAP':self.MAP})
                            except:
                                self.logTB()
                    l=[ll]
                    if bDb0:
                        self.logDbg('%r',{'lMapChk':lMapChk})
            if lMapChk is None:
                idx=self.__setSelected__(lst,l,bFlag=bFlag)
            else:
                iCntChk=len(lMapChk)
                iCnt=lst.GetItemCount()
                if iCntChk==1:
                    if iCnt>0:
                        t=type(l[0])
                        if t==ldmTypes.ListType:
                            pass
                        elif t==ldmTypes.ListType:
                            pass
                        else:   # 20150118 wro:values need to be list,
                                #       convert l from [1,2] to l=[[1],[2]]
                            ll=[]
                            for v in l:
                                ll.append([v])
                            l=ll
                lIdx=[]
                
                for i in six.moves.xrange(iCnt):
                    ll=[]
                    self.__getValue__(lst,i,lMapChk,ll)
                    for val in l:
                        if bDbg:
                            self.logDbg('%r',{'ll':ll,'val':val})
                        if ll[0]==val:
                            
                            if bDbg:
                                self.logDbg('%r',{'ll[0]':ll[0],'val':val})
                            lIdx.append(i)
                if bDb0:
                    self.logDbg('%r',lIdx)
                idx=self.__setSelected__(lst,lIdx,bFlag=bFlag)
            if bEnsure==True:
                if idx>=0:
                    lst.EnsureVisible(idx)
            return idx
        except:
            self.logTB()
        return -1
    def GetSelected(self,lMap=None):
        """get selected elements
        
        Args:
            lMap (list): list of column offsets to retrieve
                        None will deliver [-2,-1]
                - -3  : cache key
                - -2  : index
                - -1  : cached data
                - >=0 : text of column
        
        Returns:
            list of selected items, holding mapped values
        """
        try:
            self.logDbg('GetSelected lMap:%r',lMap)
            if self.IsMainThread()==False:
                return
            l=[]
            lst=self.wid
            self.__getSelected__(lst,lMap or [-2,-1],l)
            return l
        except:
            self.logTB()
        return None
    def DelIdx(self,iIdx):
        """delete index
        
        Args:
            iIdx (int): item to delete form list
        """
        try:
            self.wid.DeleteItem(iIdx)
        except:
            self.logTB()
    def DelSelected(self):
        """delete selected
        """
        try:
            lSel=self.GetSelected([-2,-1])
            self.logDbg('DelSelected lSel:%r',lSel)
            lSel.reverse()
            for t in lSel:
                self.DelIdx(t[0])
        except:
            self.logTB()

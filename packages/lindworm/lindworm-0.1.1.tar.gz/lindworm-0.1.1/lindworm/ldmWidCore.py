#----------------------------------------------------------------------------
# Name:         ldmWidCore.py
# Purpose:      ldmWidCore.py
#               core widget
# Author:       Walter Obweger
#
# Created:      20200405
# CVS-ID:       $Id$
# Copyright:    (c) 2020 by Walter Obweger
# Licence:      MIT
#----------------------------------------------------------------------------

import types
import six
import json
import os

import wx

from lindworm.logUtil import ldmUtilLog
from lindworm.ldmWidCoreEvt import ldmWidCoreEvt
from lindworm.ldmGuiThd import ldmGuiThd

gdCtrlId={}

def ldmWidCoreCtrlId(sKey,sSub=None):
    """widget control ID

    Args:
        sKey (str): widget name
        sSub (str): widget sub name
    """
    try:
        global gdCtrlId
        if sKey in gdCtrlId:
            d=gdCtrlId[sKey]
        else:
            d={}
            gdCtrlId[sKey]=d
        if sSub in d:
            iId=d[sSub]
        else:
            iId=wx.NewIdRef()
            d[sSub]=iId
        return iId
    except:
        vpc.logTB(__name__)
        return wx.NewIdRef()

def ldmWidCoreGetIcon(bmp):
    """get icon
    """
    icon = wx.EmptyIcon()
    icon.CopyFromBitmap(bmp)
    return icon

class ldmWidCore(ldmUtilLog,ldmWidCoreEvt):
    """core widget class, all widget should be derived from it.
    common interface is established to remove burden to use IDE
    to create widgets. Simple lists without to deep knowledge about
    underlying GUI library, currently wxPython is required to create
    a fully featured GUI.
    """
    def __init__(self,sLogger='',iLv=1,iVerbose=0,sCfgFN=None,**kwargs):
        """constructor
        several sub constructor methods are called in that order
        
            - __initCls__: initialize class
            - __initCfg__: initialize object configuration
            - __initDat__: initialize internal data
            - __initObj__: initialize object data
            - __initWid__: initialize widget
            - __initEvt__: initialize widget event
            - __initPrp__: initialize properties, widget data
        
        Args:
            sLogger (str , optional): log origin
            iLv (int , optional): logging level
                - 0       ... debug
                - 1       ... info
                - 2       ... warning
                - 3       ... error
                - 4       ... critical
                - x       ... debug
            iVerbose (int , optional): higher values add more logs
            sCfgFN (str , optional) json configuration file
            kwargs (dict): keyword arguments passed to all init methods
        """
        ldmUtilLog.__init__(self,sLogger,iLv=iLv,
                    iVerbose=iVerbose)
        try:
            if sCfgFN is not None:
                self.loadCfgWid(sCfgFN=sCfgFN)
        except:
            self.logTB()
        try:
            self.__initCls__(**kwargs)
            self.__initCfg__(**kwargs)
            self.__initDat__(**kwargs)
            self.__initObj__(**kwargs)
            self.__initWid__(**kwargs)
            self.__initEvt__(**kwargs)
            self.__initPrp__(**kwargs)
        except:
            self.logTB()
        try:
            self.__initLayout__(**kwargs)
        except:
            self.logTB()
    def __initCls__(self,**kwargs):
        """initialize class
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        self.clsWid=None
    def __initCfg__(self,**kwargs):
        """initialize configuration
        setup default values for configurable properties in self.dCfgWid
        or by means of self.setCfgWid
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidCore::__initCfg__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            if hasattr(self,'dCfgWid'):
                pass
            else:
                self.dCfgWid=None
            # ----- end:
            # +++++ beg:
            self.dCfgWidDft={
                'common':{
                    'bmpWidth':32,
                    },
                }
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
    def __initDat__(self,**kwargs):
        """initialize internal data, intended to application
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidCore::__initDat__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
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
            sOrg='ldmWidCore::__initObj__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
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
        """
        wid=None
        try:
            # +++++ beg:initialize
            sOrg='ldmWidCore::__initWid__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
        return wid
    def __initEvt__(self,**kwargs):
        """initialize event handling, widgets are already created
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidCore::__initEvt__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
    def __initLayout__(self,**kwargs):
        """initialize layout
        
        Args:
            kwargs (dict): keyword arguments passed to all init methods
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidCore::__initLayout__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
    def __initPrp__(self,**kwargs):
        """initialize properties, supposed to be related to widgets.
        
        Args:
            kwargs (dict:) keyword arguments passed to all init methods
        
        Returns:
            wid: widget
        """
        wid=None
        try:
            # +++++ beg:initialize
            sOrg='ldmWidCore::__initPrp__'
            self.logDbg('beg:%s'%(sOrg))
            # ----- end:initialize
            # +++++ beg:
            # ----- end:
            # +++++ beg:finalize
            self.logDbg('end:%s'%(sOrg))
            # ----- end:finalize
        except:
            self.logTB()
        return wid
    def __str__(self):
        """get object string
        
        Returns:
            str: object string
        """
        return self.sOrg
    def __repr__(self):
        """get object representation
        
        Returns:
            str: representation string
        """
        return self.sOrg
    def GetWid(self):
        """get main widget.
        panel some times.
        
        Returns:
            wid: widget
        """
        return self.wid
    def GetWidMod(self):
        """ get widget to indicate modification.
        
        Returns:
            wid: widget
        """
        return self.wid
    def GetWidChild(self):
        """future extension
        ### parameter
        ### return
            None .. future
        """
        return None
    def GetCacheDict(self,sAttr,bChk=False):
        """get dictionary for caching data,
        create empty dictionary if attribute isn't present yet.
        
        Args:
            sAttr (str): dictionary name, object attribute
            bChk (bool , optional): check only
        
        Returns:
            return obj
                - dictionary, if bChk==False
                - bool, boolean check if bChk==True
                    - True : attribute present
                    - False : or not
                - None : exception
        """
        try:
            bDbg=self.GetVerboseDbg(0)
            if bDbg:
                self.logDbg('')
            if bChk==True:
                if hasattr(self,sAttr):
                    return True
                else:
                    return False
            if hasattr(self,sAttr):
                dTmp=getattr(self,sAttr)
            else:
                dTmp={}
                setattr(self,sAttr,dTmp)
            return dTmp
        except:
            self.logTB()
        return None
    def GetCtrlId(self,sKey,sSub=None):
        """get widget (control) id, used in GUI framework
        reuse id for similar controls, which are cached
        in global dictionary, build by use of ldmWidCoreCtrlId.
        
        Args:
            sKey (str): primary key
                - None uses class name instead
            sSub (str): secondary key
        
        Returns
            int: widget id
        """
        if sKey is None:
            return ldmWidCoreCtrlId(self.__class__.__name__,sSub)
        else:
            return ldmWidCoreCtrlId(sKey,sSub)
    def GetKw(self,kwargs,lKey,dDft=None,kag=None):
        """get keyword arguments lightweight copy with
        defaults mixed in.
        
        Args:
            kwargs (dict): original keyword arguments at constructor
            lKey (list): list of required keyword arguments returned
            dDft (dict): default values
            kag (obj): dictionary preset, None create a new dictionary
        
        Returns:
            dict: kag, key word arguments dictionary
        """
        if kag is None:
            kag={}
        for s in lKey:
            if s in kwargs:
                kag[s]=kwargs[s]
        if dDft is not None:
            for k,it in six.iteritems(dDft):
                if k not in kag:
                    kag[k]=it
                else:
                    if kag[k] is None:
                        kag[k]=it
        return kag
    def GetWidArgs(self,kwargs,lKey,dDft,kag=None,sSub=None,
                bValidate=True,par=None,lArg=None):
        """get widget arguments to be passed at constructor
        
        gui frameworks are restrict when it comes to arguments 
        accepted. depending on widget class a specific set
        of arguments and keyword arguments are needed.
        this method provide a way to construct arguments and
        keyword arguments by mixing in defaults to lightweight 
        copy of original kwargs.
        
        method GetCtrlId is used to get widget id determined by
        parent name and sSub. similar ids shall be used through
        entire application.

        additional arguments might be:
            - pos (obj , optional): widget position (wx.DefaultPosition)
            - size (obj , optional): widget size (wx.DefaultSize)
        
        Args:
            kwargs (dict): original keyword arguments at constructor
            lKey (list): list of required keyword arguments returned
            dDft (dict): default values
            kag (dict , optional): dictionary preset, None create a new dictionary
            sSub (str , optional): sub name
            bValidate (bool , optional): enforce elementary arguments to be present,
            par (wid , optional): parent object/widget, determine parent name
                - GetWid is used to retrieve widget of object
            lArg (list): list of arguments removed from keyword 
        
        Returns:
            tuple
                list: arg, argument list
                dict: kag, key word arguments dictionary
        """
        lArgs=[]
        kag=self.GetKw(kwargs,lKey,dDft,kag=kag)
        if 'pos' not in kag:
            kag['pos']=wx.DefaultPosition
        if 'size' not in kag:
            kag['size']=wx.DefaultSize
        if bValidate==True:
            if kag['pos'] is None:
                kag['pos']=wx.DefaultPosition
            if kag['size'] is None:
                kag['size']=wx.DefaultSize
        #else:
        #    sz=kag['size']
        if sSub is None:
            if 'sSub' in kwargs:
                sSub=kwargs['sSub']
                #print self.__class__.__name__,sSub
            else:
                # 20150112 wro: is this really a good idea?
                if 'name' in kwargs:
                    #sSub=kwargs['name']
                    #print self.__class__.__name__,sSub,'name'
                    pass
        if par is None:
            sNamePar=self.__class__.__name__
        else:
            sNamePar=par.GetName()
        if 'id' not in kag:
            iId=self.GetCtrlId(sNamePar,sSub)
            kag['id']=iId
        else:
            if kag['id'] is None:
                iId=self.GetCtrlId(self.__class__.__name__,sSub)
                kag['id']=iId
            else:
                iId=kag['id']
        if 'parent' in kag:
            parent=kag['parent']
            if hasattr(parent,'GetWid'):
                par=parent.GetWid()
                kag['parent']=par
        #if 'style' not in kag:
        #    kag['style']=wx.TAB_TRAVERSAL
        #else:
        #    if kag['style'] is None:
        #        kag['style']=wx.TAB_TRAVERSAL
        #self.logDbg({'kag':kag,'name':self.__class__.__name__,
        #        'kwargs':kwargs,'lKey':lKey,'dDft':dDft})
        if lArg is not None:
            for sK in lArg:
                if sK in kag:
                    lArgs.append(kag[sK])
                    del kag[sK]
                else:
                    lArgs.append(None)
        arg=tuple(lArgs)
        return arg,kag
    def CB(self,func,*args,**kwargs):
        """callback func/method in main thread
        widget manipulation inside a thread may cause
        stability issues.
        
        Args:
            func (callable): callable
            args (list): arguments to pass
            kwargs (dict): keyword arguments to pass
        """
        try:
            wx.CallAfter(func,*args,**kwargs)
        except:
            self.logTB()
    def CallBackDelayed(self,zSleep,func,*args,**kwargs):
        """delayed callback func/method in main thread
        widget manipulation inside a thread may cause
        stability issues.
        
        Args:
            zSleep (float): delay time in seconds
            func (callable): callable
            args (list): arguments to pass
            kwargs (dict): keyword arguments to pass
        """
        try:
            wx.CallAfter(wx.FutureCall,int(zSleep*1000),func,*args,**kwargs)
        except:
            self.logTB()
    def setCfgWid(self,sGrp,sKey,sVal,iMode=1):
        """get configuration value
        
        Args:
            sGrp (str): configuration group
            sKey (str): configuration key
            sVal (str): value
            iMode (int): configuration dictionary to change
                - 1   : default dictionary
                - 2   : active dictionary
                - 3   : both
                - <=0 : default dictionary
        
        Returns:
            return code
                - >0 : okay processing done
                - =0 : okay nop
                - <0 : error
        """
        try:
            # +++++ beg:initialize
            iRet=0
            # ----- end:initialize
            # +++++ beg:adapt faulty iMode
            if iMode<=0:
                iMode=1
            # ----- end:adapt faulty iMode
            # +++++ beg:set value in default dictionary
            if (iMode & 1)==1:
                if self.dCfgWidDft is None:
                    self.dCfgWidDft={}
                if sGrp in self.dCfgWidDft:
                    dGrp=self.dCfgWidDft[sGrp]
                else:
                    dGrp={}
                    self.dCfgWidDft[sGrp]=dGrp
                dGrp[sKey]=sVal
                iRet+=1
            # ----- end:set value in default dictionary
            # +++++ beg:set value in active dictionary
            if (iMode & 2)==2:
                if self.dCfgWid is not None:
                    if sGrp in self.dCfgWid:
                        dGrp=self.dCfgWid[sGrp]
                    else:
                        dGrp={}
                        self.dCfgWid[sGrp]=dGrp
                        dGrp[sKey]=sVal
                iRet+=2
            # ----- end:set value in active dictionary
            return iRet
        except:
            self.logTB()
            return -1
    def getCfgWidTup(self,sGrp,sKey,sType=None,oDft=None):
        """get configuration value and return code
        
        Args:
            sGrp (str): configuration group
            sKey (str): configuration key
            sType (str , optional): type enforcement
            oDft (obj , optional): default value
        
        Returns:
            tuple
                return code
                    - 1  : value taken from defaults dictionary
                    - 2  : value taken from active dictionary
                    - >0 : okay processing done
                    - =0 : okay nop
                    - <0 : error
                
                value
        """
        try:
            # +++++ beg:initialize
            iRet=0
            oVal=oDft
            # ----- end:initialize
            # +++++ beg:find value
            if self.dCfgWid is not None:
                if sGrp in self.dCfgWid:
                    dGrp=self.dCfgWid[sGrp]
                    if sKey in dGrp:
                        iRet=2
                        oVal=dGrp[sKey]
            # ----- end:find value
            # +++++ beg:find default value
            if iRet==0:
                if self.dCfgWidDft is not None:
                    if sGrp in self.dCfgWidDft:
                        dGrp=self.dCfgWidDft[sGrp]
                        if sKey in dGrp:
                            iRet=1
                            oVal=dGrp[sKey]
            # ----- end:find default value
            # +++++ beg:type enforcement
            if iRet>0:
                if sType=='int':
                    try:
                        iVal=int(oVal)
                        return iRet,iVal
                    except:
                        iVal=oDft
                        return iRet,iVal
            # ----- end:type enforcement
            return iRet,oVal
        except:
            self.logTB()
            return -1,None
    def getCfgWid(self,sGrp,sKey,sType=None,oDft=None):
        """get configuration value
        
        Args:
            sGrp (str): configuration group
            sKey (str): configuration key
            sType (str , optional): type enforcement
            oDft (obj , optional): default value
        
        Returns:
            obj: value
        """
        try:
            # +++++ beg:initialize
            iRet=0
            # ----- end:initialize
            # +++++ beg:get value
            iRet,oVal=self.getCfgWidTup(sGrp,sKey,sType=sType,oDft=oDft)
            # ----- end:get value
            return oVal
        except:
            self.logTB()
            return oDft
    def loadCfgWid(self,sCfgFN='cfg.json'):
        """read configuration file, given in json format
        configuration is place in dCfgWid, or it's None
        
        Args:
            sCfgFN (str , optional): configuration file name
        
        Returns:
            return code
                - >0 : okay processing done
                - =0 : okay nop
                - <0 : error
        """
        try:
            # +++++ beg:initialize
            sOrg='ldmWidCore::loadCfgWid'
            self.oLog.debug('beg:%s iVerbose:%d'%(sOrg,self.iVerbose))
            iRet=0
            # ----- end:initialize
            # +++++ beg:read cfg file
            self.sCfgWidFN=sCfgFN
            self.dCfgWid=None
            if os.path.exists(self.sCfgWidFN):
                with open(self.sCfgWidFN,'r') as oFile:
                    self.dCfgWid=json.loads(oFile.read())
                iRet=1
            # ----- end:read cfg file
            # +++++ beg:verbose cfg dict
            if self.iVerbose>=30:
                self.oLog.debug('%r %r',self.sCfgWidFN,self.dCfgWid)
            # ----- end:verbose cfg dict
            # +++++ beg:finalize
            self.oLog.debug('end:%s  iRet:%d'%(sOrg,iRet))
            # ----- end:finalize
            return iRet
        except:
            self.logTB()
            return -1
    def IsMainThread(self,bMain=True,bSilent=False):
        """is main thread, important, widget might be sensitive from where they are manipulated

        Returns:
            return code
                - True: main thread, manipulation is safe
                - False: thread, unsafe to manipulate
        """
        return True
        if wx.Thread_IsMain()!=bMain:
            if bSilent==False:
                if bMain:
                    self.logCri('called by thread'%())
                else:
                    self.logCri('called by main thread'%())
            return False
        return True
    def __getThread__(self,sName):
        """get thread by name, create if not present already

        Args:
            sName (str): thread name
        
        Returns:
            ldmGuiThd: thread object
        """
        try:
            bDbg=self.GetVerboseDbg(10)
            if bDbg:
                self.logDbg(''%())
            sThdName='_oThd'+sName
            if hasattr(self,sThdName)==False:
                oThd=ldmGuiThd()
                self.__dict__[sThdName]=oThd
                return oThd
            else:
                return self.__dict__[sThdName]
        except:
            self.logTB()

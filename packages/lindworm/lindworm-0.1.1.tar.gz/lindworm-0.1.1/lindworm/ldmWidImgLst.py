#----------------------------------------------------------------------------
# Name:         ldmWidImgLst.py
# Purpose:      ldmWidImgLst.py
#               GUI widget respond on size change
# Author:       Walter Obweger
#
# Created:      20210813
# CVS-ID:       $Id$
# Copyright:    (c) 2021 by Walter Obweger
# Licence:      MIT
#----------------------------------------------------------------------------

import lindworm.logUtil as logUtil

try:
    import wx
    import six

    import lindworm.ldmTypes as ldmTypes
    import lindworm.ldmGuiArt as ldmGuiArt
except:
    logUtil.logTB()

gdImgLst={}

def ldmWidImgLstGet(sName,which=0,dft=None,lDef=[],oLog=None,**kw):
    try:
        global gdImgLst
        if sName in gdImgLst:
            return gdImgLst[sName],False
        else:
            w=ldmWidImgLst(which=which,dft=dft,lDef=lDef,oLog=oLog)
            gdImgLst[sName]=w
            return w,True
    except:
        logUtil.logTB()
    return None,False

class ldmWidImgLst:
    """
    """
    def __init__(self,which=0,dft='list',lDef=[],oLog=None,**kw):
        """constructor

        Args:
            which (int): appearance 
            dft (str, optional): control
                - 'list'
                - 'tree'
            lDef (list , optional): list of definition
            oLog (ldmUtilLog , optional): logging object
            kw (dict): keyword arguments
        """
        if (which is None) or (which==wx.IMAGE_LIST_SMALL):
            imgLst=wx.ImageList(16,16)
        elif which==0:
            imgLst=wx.ImageList(16,16)
        else:
            imgLst=wx.ImageList(16,16)
            which=None
        self._dImg={}
        self._imgLst=imgLst
        if dft=='list':
            self.CreateDftList()
        elif dft=='tree':
            self.CreateDftTree()
        self.AddImageList(lDef,bForce=False,oLog=oLog)
    def GetObjs(self):
        """get objects

        Returns:
            tuple
                dict: image dictionary
                list: wx image list 
        """
        return self._dImg,self._imgLst
    def AddImageList(self,lDef,bForce=False,oLog=None):
        """add image list

        Args:
            lDef (list): list of definition
            bForce (bool , optional): force
            oLog (ldmUtilLog , optional): logging object
        """
        try:
            iVerbose=0
            if oLog is not None:
                iVerbose=1
            if iVerbose>0:
                oLog.logDbg("beg:ldmWidImgLst::AddImageList")
            if lDef is None:
                return
            dImg=self._dImg
            imgLst=self._imgLst
            for sK,it in lDef:
                if iVerbose>0:
                    oLog.logDbg('  sK:%s it:%r',sK,it)
                if bForce==False:
                    if sK in dImg:
                        continue
                try:
                    t=type(it)
                    def getImg(bmp):
                        if type(bmp)==ldmTypes.StringType:
                            iOfs=bmp.find('imgCore.get')
                            if iOfs==0:
                                return ldmGuiArt.getBmp('core',bmp[11:-8])
                            iOfs=bmp.find('.')
                            if iOfs==-1:
                                return ldmGuiArt.getBmp('core',bmp)
                            return eval(bmp)
                        else:
                            return bmp
                    def addImg(imgLst,bmp):
                        try:
                            ret=imgLst.Add(getImg(bmp))
                        except:
                            logUtil.logTB()
                            logUtil.logErr('bmp:%r',bmp)
                            bmpFB=wx.ArtProvider.GetBitmap(wx.ART_QUESTION)
                            ret=imgLst.Add(bmpFB)
                        return ret
                    if t==ldmTypes.TupleType:
                        lImg=[addImg(imgLst,bmp) for bmp in it]
                    elif t==ldmTypes.ListType:
                        lImg=[addImg(imgLst,bmp) for bmp in it]
                    else:
                        lImg=addImg(imgLst,it)
                    dImg[sK]=lImg
                except:
                    logUtil.logTB()
        except:
            logUtil.logTB()
    def CreateDftList(self):
        """create default list
        """
        try:
            self.AddImageList([
                    ('empty',       ldmGuiArt.getBmp('core','Invisible')),
                    ('asc',         ldmGuiArt.getBmp('core','UpSml')),
                    ('desc',        ldmGuiArt.getBmp('core','DnSml')),
                    ])
        except:
            logUtil.logTB()
    def CreateDftTree(self):
        """create default tree
        """
        try:
            self.AddImageList([
                    ('empty',       ldmGuiArt.getBmp('core','Invisible')),
                    #('asc',         vGuiArt.getBmp('core','UpSml')),
                    #('desc',        vGuiArt.getBmp('core','DnSml')),
                    ])
        except:
            logUtil.logTB()
    def GetImg(self,sTag,sFB):
        """get image

        Args:
            sTag (str): image name
            sFB (str): fallback image name
        
        Returns:
            return code
                - >=0 : image identifier
                - ==-1 : error
        """
        try:
            if self._dImg is not None:
                iImg=self._dImg.get(sTag,None)
                if iImg is None:
                    iImg=self._dImg.get(sFB,-1)
                return iImg
        except:
            logUtil.logTB()
        return -1

#----------------------------------------------------------------------------
# Name:         ldmGuiArt.py
# Purpose:      ldmGuiArt.py
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
    import lindworm.ldmTypes as ldmTypes
    from wx import NullBitmap,NullImage,EmptyIcon,EmptyBitmap,EmptyImage
    
    import fnmatch
except:
    logUtil.logTB()

class ldmGuiArtProvider:
    """art provider stores images and bitmaps to be retrieved by name
    as global object.
    
    Attributes:
        bmpNull (obj): null bitmap
        imgNull (obj): null image
        dCache (dict): dictionary to cache bitmaps
        dCacheImg (dict): dictionary to cache images
        dMod (dict): dictionary of modules
        dImg (dict): dictionary of images
    """
    def __init__(self):
        """
        """
        self.bmpNull=NullBitmap
        self.imgNull=NullImage
        self.dCache={}
        self.dCacheImg={}
        self.dMod={}
        self.dImg={}
        self.setUp()
    def setUp(self):
        """
        """
        try:
            import imgCore as imgCore
            self.AddMod('ldmCore',imgCore)
        except:
            logUtil.logTB()
        try:
            import lindworm.ldmWidImgMed as ldmWidImgMed
            self.AddMod('ldmMed',ldmWidImgMed)
        except:
            logUtil.logTB()
    def addMod(self,sK,mod):
        """add module
        store module in attribute dMod

        Args:
            sK (str): key
            mod (obj): module
        """
        self.dMod[sK]=mod
    def AddMod(self,sK,mod):
        """add module

        Args:
            sK (str): key
            mod (obj): module
        """
        try:
            self.addMod(sK,mod)
            self.addBitmaps(sK)
        except:
            logUtil.logTB()
    def __getImgModByName__(self,sClt,iRec=5):
        """

        Args:
            sClt (str): client name
            iRec (int): recursion limit
        """
        if sClt in self.dMod:
            m=self.dMod[sClt]
            if type(m)==ldmTypes.TupleType:
                if iRec>0:
                    return self.__getImgModByName__(m,iRec=iRec-1)
                else:
                    return None
            return self.dMod[sClt]
        else:
            return None
        if sClt in ['ldmCore']:
            return imgCore
        if sClt in ['ldmMed']:
            return ldmWidImgMed
        return None
    def addBitmaps(self,sClt):
        m=self.__getImgModByName__(sClt)
        if m is None:
            return
        lBitmaps=dir(m)
        
        if sClt in self.dImg:
            dBmp=self.dImg[sClt]
        else:
            dBmp={None:[]}
            self.dImg[sClt]=dBmp
        lName=dBmp[None]
        for sN in lBitmaps:
            if fnmatch.fnmatch(sN,'get*Bitmap'):
                sBmp=sN[3:-6]
                if sBmp not in dBmp:
                    lName.append(sBmp)
                    dBmp[sBmp]=sN
                    if logUtil.iVerbose>20:
                        print('',sBmp)
                        logUtil.logDbg('addBitmaps %s %s %s',sBmp,sN,__name__)
        lName.sort()
        logUtil.logDbg('lName:%r org:%s',lName,__name__)
        logUtil.logDbg('lName:%r org:%s',dBmp,__name__)
        logUtil.logDbg('lName:%r org:%s',self.dImg,__name__)
    def GetBitmap(self,sClt,sArt,sz=(16,16)):
        if sClt not in self.dImg:
            return self.bmpNull
        sArtId='.'.join([sClt,sArt])
        if sArtId in self.dCache:
            return self.dCache[sArtId]
        else:
            img=self.CreateBitmap(sClt,sArt,sz)
            self.dCache[sArtId]=img
            return img
    def CreateBitmap(self,sClt,sArt,sz):
        try:
            m=self.__getImgModByName__(sClt)
            if m is not None:
                bmp=getattr(m,''.join(['get',sArt,'Bitmap']))()
                return bmp
        except:
            return EmptyBitmap(sz[0],sz[1])
        return self.bmpNull
    def GetImage(self,sClt,sArt,sz=(16,16)):
        if sClt not in self.dImg:
            return self.bmpNull
        sArtId='.'.join([sClt,sArt])
        if sArtId in self.dCacheImg:
            return self.dCacheImg[sArtId]
        else:
            img=self.CreateImage(sClt,sArt,sz)
            self.dCacheImg[sArtId]=img
            return img
    def CreateImage(self,sClt,sArt,sz):
        try:
            m=self.__getImgModByName__(sClt)
            if m is not None:
                img=getattr(m,''.join(['get',sArt,'Image']))()
                return img
        except:
            return EmptyImage(sz[0],sz[1])
        return self.imgNull

__artProv=None
__bInstalled=False

def Install(oProvider=None):
    if logUtil.iVerbose>0:
        logUtil.logDbg('register oProvider;%o'%(oProvider),__name__)
    global __bInstalled
    if __bInstalled:
        return
    __bInstalled=True
    global __artProv
    if oProvider is None:
        __artProv=ldmGuiArtProvider()
    else:
        __artProv=oProvider
def DeInstall():
    global __bInstalled
    if __bInstalled==False:
        return
    __bInstalled=False
    global __artProv
    __artProv=None
def GetProv(sN,mod):
    global __bInstalled
    if __bInstalled:
        pass
    else:
        Install()
    global __artProv
    return __artProv
def AddMod(sN,mod):
    global __bInstalled
    if __bInstalled:
        pass
    else:
        Install()
    global __artProv
    __artProv.AddMod(sN,mod)
def GetBmp(sN,sz=(16,16)):
    global __bInstalled
    if __bInstalled:
        pass
    else:
        Install()
    global __artProv
    iOfs=sN.find('imgCore.get')
    if iOfs==0:
        sClt,sArt='core',sN[11:-8]
        return __artProv.GetBitmap(sClt,sArt,sz)
    iOfs=sN.find('.')
    if iOfs==-1:
        sClt,sArt='core',sN
        return __artProv.GetBitmap(sClt,sArt,sz)
    else:
        sClt,sArt=sN[:iOfs],sN[iOfs+1:]
    return __artProv.GetBitmap(sClt,sArt,sz)
def getBmp(sClt,sArt,sz=(16,16)):
    global __bInstalled
    if __bInstalled:
        pass
    else:
        Install()
    global __artProv
    return __artProv.GetBitmap(sClt,sArt,sz)
def getImg(sClt,sArt,sz=(16,16)):
    global __bInstalled
    if __bInstalled:
        pass
    else:
        Install()
    global __artProv
    return __artProv.GetImage(sClt,sArt,sz)
def getIcn(sClt,sArt,sz=(16,16)):
    bmp=getBmp(sClt,sArt,sz)
    icon = EmptyIcon()
    icon.CopyFromBitmap(bmp)
    return icon
def getIcon(bmp):
    icon = EmptyIcon()
    icon.CopyFromBitmap(bmp)
    return icon

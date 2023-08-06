#----------------------------------------------------------------------------
# Name:         logUtil.py
# Purpose:      logging utilities
#
# Author:       Walter Obweger
#
# Created:      20191223
# CVS-ID:       $Id$
# Copyright:    (c) 2019 by Walter Obweger
# Licence:      MIT
#----------------------------------------------------------------------------

import logging
import logging.handlers
import traceback

import lindworm.ldmOS as ldmOS

lngFileHandler=None
iVerbose=0

def logInit(sLogFN,sLogger='',iLevel=logging.DEBUG,iNameLen=6):
    """initialize logging
    ### parameter
        sLogFN      ... filename
        sLogger     ... module log name
        iLevel      ... detail level
        iNameLen    ... module name length of formatting
    ### return 
        oLog        ... logging object
                None .. something went wront
    """
    # +++++ beg:info
    global lngFileHandler
    if iVerbose>0:
        print('logInit:%s'%(sLogFN))
    # ----- end:info
    # +++++ beg:build FN
    try:
        iRet,sBldFN=ldmOS.bldFN(sLogFN,sExt='log')
        if iRet>0:
            sLogFN=sBldFN
    except:
        pass
    # ----- end:build FN
    # +++++ beg:prepare logging
    lngFileHandler=logging.handlers.RotatingFileHandler(sLogFN,backupCount=9)
    lngFileHandler.setLevel(iLevel)
    sFmt='%(asctime)s|%(name)-'+'%d'%(iNameLen)+'s|%(levelname)-8s|%(message)s'
    formatter=logging.Formatter(sFmt)
    lngFileHandler.setFormatter(formatter)
    lngFileHandler.doRollover()
    if iVerbose>0:
        print('lngFileHandler:%r'%(lngFileHandler))
    # ----- end:prepare logging
    # +++++ beg:add root logger
    logging.getLogger('').setLevel(iLevel)
    logging.getLogger('').addHandler(lngFileHandler)
    # ----- end:add root logger
    # +++++ beg:add specific logger
    if sLogger is not None:
        oLog=logGet(sLogger)
        return oLog
    else:
        return None
    # ----- end:add specific logger

def logGet(sLogger,iLevel=logging.DEBUG):
    """get logger
    ### parameter
        sLogger ... logging name
        iLevel  ... logging level
    """
    global lngFileHandler
    if iVerbose>0:
        print('logGet:%s'%(sLogger))
        print('lngFileHandler:%r'%(lngFileHandler))
    oLog=logging.getLogger(sLogger)
    oLog.setLevel(iLevel)
    #if lngFileHandler is not None:
    #    oLog.addHandler(lngFileHandler)
    return oLog

def logCreate(sLogFN,sLogger='',iLv=2,iNameLen=6):
    """create logging target, file handler 10 files auto rollover
    and simplified level definition, just numbers from 0 to 4,
    lower numbers are more detailed information.
    ### parameter
        sLogger     ... log origin
        iLv         ... trivial logging level
            0       ... debug
            1       ... info
            2       ... warning
            3       ... error
            4       ... critical
            x       ... debug
        iNameLen    ... module name length of formatting
        iVerbose    ... higher values add more logs
    """
    if iLv==0:
        iLevel=logging.DEBUG
    elif iLv==1:
        iLevel=logging.INFO
    elif iLv==2:
        iLevel=logging.WARNING
    elif iLv==3:
        iLevel=logging.ERROR
    elif iLv==4:
        iLevel=logging.CRITICAL
    else:
        iLevel=logging.DEBUG
    return logInit(sLogFN,sLogger,iLevel,iNameLen=iNameLen)

def logTB():
    """log traceback
    """
    logging.error(traceback.format_exc())

def logDbg(sMsg,*args):
    """log information data
    ### parameter
        sMsg    ... message
        args    ... arguments for mmessage
    """
    if len(args)==0:
        logging.debug(sMsg)
    else:
        logging.debug(sMsg%args)
def logInf(sMsg,*args):
    """log information data
    ### parameter
        sMsg    ... message
        args    ... arguments for mmessage
    """
    if len(args)==0:
        logging.info(sMsg)
    else:
        logging.info(sMsg%args)
def logWrn(sMsg,*args):
    """log warning data
    ### parameter
        sMsg    ... message
        args    ... arguments for mmessage
    """
    if len(args)==0:
        logging.warning(sMsg)
    else:
        logging.warning(sMsg%args)
def logErr(sMsg,*args):
    """log error data
    ### parameter
        sMsg    ... message
        args    ... arguments for mmessage
    """
    if len(args)==0:
        logging.error(sMsg)
    else:
        logging.error(sMsg%args)
def logCri(sMsg,*args):
    """log critical data
    ### parameter
        sMsg    ... message
        args    ... arguments for mmessage
    """
    if len(args)==0:
        logging.critical(sMsg)
    else:
        logging.critical(sMsg%args)
def log(iLv,sMsg,*args):
    """log data
    ### parameter
        iLv     ... trivial logging level
            0   ... debug
            1   ... info
            2   ... warning
            3   ... error
            4   ... critical
            x   ... debug
        sMsg    ... message
        args    ... arguments for mmessage
    """
    if iLv==0:
        logDbg(sMsg,*args)
    elif iLv==1:
        logInf(sMsg,*args)
    elif iLv==2:
        logWrn(sMsg,*args)
    elif iLv==3:
        logErr(sMsg,*args)
    elif iLv==4:
        logCri(sMsg,*args)
    else:
        logDbg(sMsg,*args)

class ldmUtilLog:
    """basic logging object should be inherited by complex objects, widgets
    to ease use of logging package.
    """
    def __init__(self,sLogger='',iLv=0,iLevel=None,iVerbose=0,sOrg=None,iIndent=2):
        """constructor
        ### parameter
            sLogger     ... log origin
            iLv         ... trivial logging level
                0       ... debug
                1       ... info
                2       ... warning
                3       ... error
                4       ... critical
                x       ... debug
            iLevel      ... logging level
            iVerbose    ... higher values add more logs
        """
        self.iVerbose=iVerbose
        if iLevel is None:
            if iLv==0:
                iLevel=logging.DEBUG
            elif iLv==1:
                iLevel=logging.INFO
            elif iLv==2:
                iLevel=logging.WARNING
            elif iLv==3:
                iLevel=logging.ERROR
            elif iLv==4:
                iLevel=logging.CRITICAL
            else:
                iLevel=logging.DEBUG
        self.oLog=logGet(sLogger,iLevel)
        self.iIsDbg=0
        self.iIndent=iIndent
        self.iDepth=0
        if iLevel==logging.DEBUG:
            self.iIsDbg=1
        if sOrg:
            self.sOrg=sOrg
        else:
            self.sOrg=sLogger
    def rstDepth(self):
        """reset depth
        """
        self.iDepth=-1
        self.bldIndent()
    def setDepth(self,iDepth):
        """set depth
        """
        self.iDepth=iDepth
        self.bldIndent()
    def incDepth(self):
        """increment depth
        """
        if self.iDepth<0:
            self.iDepth=0
        self.iDepth+=1
        self.bldIndent()
    def decDepth(self):
        """decrement depth
        """
        self.iDepth-=1
        if self.iDepth<0:
            self.iDepth=0
        self.bldIndent()
    def bldIndent(self):
        """build indention string to be added as prefix to log message
        per depth (level) amount of iIdent spaces are added.
        """
        if self.iDepth<=0:
            self.sIndent=None
        else:
            self.sIndent=' '*(min(self.iIndent*self.iDepth,30))
    def logDbg(self,sMsg,*args):
        """log debugging data
        ### parameter
            sMsg    ... message
            args    ... arguments for mmessage
        """
        if self.oLog is not None:
            try:
                if self.iDepth>0:
                    if self.sIndent is not None:
                        if len(args)==0:
                            self.oLog.debug(self.sIndent+sMsg)
                        else:
                            self.oLog.debug(self.sIndent+sMsg%args)
                        return
            except:
                pass
            if len(args)==0:
                self.oLog.debug(sMsg)
            else:
                self.oLog.debug(sMsg%args)
    def logInf(self,sMsg,*args):
        """log information data
        ### parameter
            sMsg    ... message
            args    ... arguments for mmessage
        """
        if self.oLog is not None:
            if len(args)==0:
                self.oLog.info(sMsg)
            else:
                self.oLog.info(sMsg%args)
    def logWrn(self,sMsg,*args):
        """log warning data
        ### parameter
            sMsg    ... message
            args    ... arguments for mmessage
        """
        if self.oLog is not None:
            if len(args)==0:
                self.oLog.warning(sMsg)
            else:
                self.oLog.warning(sMsg%args)
    def logErr(self,sMsg,*args):
        """log error data
        ### parameter
            sMsg    ... message
            args    ... arguments for mmessage
        """
        if self.oLog is not None:
            if len(args)==0:
                self.oLog.error(sMsg)
            else:
                self.oLog.error(sMsg%args)
    def logCri(self,sMsg,*args):
        """log critical data
        ### parameter
            sMsg    ... message
            args    ... arguments for mmessage
        """
        if self.oLog is not None:
            if len(args)==0:
                self.oLog.critical(sMsg)
            else:
                self.oLog.critical(sMsg%args)
    def log(self,iLv,sMsg,*args):
        """log data
        ### parameter
            iLv     ... trivial logging level
                0   ... debug
                1   ... info
                2   ... warning
                3   ... error
                4   ... critical
                x   ... debug
            sMsg    ... message
            args    ... arguments for mmessage
        """
        if iLv==0:
            self.logDbg(sMsg,*args)
        elif iLv==1:
            self.logInf(sMsg,*args)
        elif iLv==2:
            self.logWrn(sMsg,*args)
        elif iLv==3:
            self.logErr(sMsg,*args)
        elif iLv==4:
            self.logCri(sMsg,*args)
        else:
            self.logDbg(sMsg,*args)
    def logTB(self):
        """log traceback, typical called in exception part
        """
        self.oLog.error(traceback.format_exc())
    def GetVerbose(self,iVerbose=-1):
        """get verbose level 
        ### parameter
            iVerbose    ... verbose level to check
        ### return
            True    ... object verbose >= iVerbose
            False   ... object verbose < iVerbose
            number  ... object verbose if iVerbose < 0
        """
        if iVerbose>=0:
            if self.iVerbose>=iVerbose:
                return True
            else:
                return False
        else:
            return self.iVerbose
    def GetVerboseDbg(self,iVerbose=-1):
        """get verbose level in debugging mode
        ### parameter
        ### return
            True    ... object verbose >= iVerbose
            False   ... object verbose < iVerbose
                    ... log level not in debugging
            number  ... object verbose if iVerbose < 0
        """
        if self.iIsDbg>0:
            return self.GetVerbose(iVerbose=iVerbose)
        else:
            return False

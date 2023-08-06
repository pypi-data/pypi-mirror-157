#----------------------------------------------------------------------------
# Name:         lmdStr.py
# Purpose:      string helper class
#
# Author:       Walter Obweger
#
# Created:      20200108
# CVS-ID:       $Id$
# Copyright:    Walter Obweger
# Licence:      MIT
#----------------------------------------------------------------------------

import logging
import traceback

class ldmStr:
    """string auxillary class
    """
    def findBegEnd(self,sLine,iLen,iPos,cBeg='[',cEnd=']',iVerbose=-1):
        """find whitespace begin or end
        
        Args:
            sLine (str): string to search
            iLen (int): string length
            iPos (int): position to start search
            cBeg (str , optional): string to find begin
            cEnd (str , optional): string to find end
            iVerbose (int , optional): verbosity 
        
        Returns:
            tuple
                int: iBeg, begin position 
                    - >=0 ... okay processing done
                    - <0  ... not found

                int: iEnd, end position
                    - >=0 ... okay processing done
                    - <0  ... not found

        """
        try:
            # +++++ beg:initialize
            if iVerbose>0:
                logging.debug('beg:%s iVerbose:%d'%('ldmStr::findWhiteSpace',iVerbose))
            iRet=-1
            iBeg=-1
            iEnd=-1
            lWhiteSpace=[' ']
            # ----- end:initialize
            # +++++ beg:
            iBeg=sLine.find(cBeg,iPos)
            if iBeg>=0:
                iEnd=sLine.find(cEnd,iBeg+1)
                if iEnd>0:
                    return iBeg,iEnd
            # ----- end:
            # +++++ beg:finalize
            if iVerbose>0:
                logging.debug('end:%s  iRet:%d iBeg:%d iEnd:%d'%('ldmStr::findWhiteSpace',iRet,
                                                    iBeg,iEnd))
            # ----- end:finalize
            return iBeg,iEnd
        except:
            logging.error(traceback.format_exc())
            return -1,-1
    def findWhiteSpace(self,sLine,iLen,iPos,iMode=1,iVerbose=-1):
        """find whitespace begin or end
        
        Args:
            sLine (str): string to search
            iLen (int): string length
            iPos (int): position to start search
            iMode (int , optional): search mode, 1= find begin , 0+ find end 
            iVerbose (int , optional): verbosity 
        
        Returns:
            return code
                - >0 : okay processing done
                - =0 : okay nop
                - <0 : error
        """
        try:
            # +++++ beg:
            if iVerbose>0:
                logging.debug('beg:%s iVerbose:%d'%('ldmStr::findWhiteSpace',iVerbose))
            iRet=-1
            lWhiteSpace=[' ']
            # ----- end:
            # +++++ beg:
            if iLen<0:
                iLen=len(sLine)
            if iPos<0:
                iPos=0
            iOfs=iPos
            iFound=0
            while (iFound==0) and (iOfs<iLen):
                sChk=sLine[iOfs]
                if iMode>0:
                    if sChk not in lWhiteSpace:
                        iOfs=iOfs+1
                    else:
                        iFound=1
                        iRet=iOfs
                else:
                    if sChk in lWhiteSpace:
                        iOfs=iOfs+1
                    else:
                        iFound=1
                        iRet=iOfs
            if iFound==0:
                if iOfs>=iLen:
                    iRet=sLine.rfind('\r')
                    if iRet<0:
                        iRet=sLine.rfind('\n')
                        if iRet<0:
                            iRet=iLen
            # ----- end:
            # +++++ beg:
            if iVerbose>0:
                logging.debug('end:%s  iRet:%d'%('ldmStr::findWhiteSpace',iRet))
            # ----- end:
            return iRet
        except:
            logging.error(traceback.format_exc())
            return -1
    def replaceIgnore(self,sNav,sReplIgnore=''):
        """replace strange characters to ensure proper 
        header navigation.
        
        Args:
            sNav (str): string to manipulate, a new copy with only valid characters is returned
            sReplIgnore (str , optional): character to use as replacement
        
        Returns:
            str: sNav ... new string
                - ''.. exception happened
        """
        try:
            # +++++ beg:initialize
            iLen=len(sNav)
            lNav=[]
            # ----- end:initialize
            # +++++ beg:loop through string
            for iOfs in range(0,iLen):
                cTmp=sNav[iOfs]
                iTmp=ord(cTmp)
                if (iTmp>=65) and (iTmp<=90):
                    pass
                elif (iTmp>=97) and (iTmp<=122):
                    pass
                elif (iTmp>=48) and (iTmp<=57):
                    pass
                elif cTmp in ['.']:
                    pass
                else:
                    cTmp=sReplIgnore
                lNav.append(cTmp)
            # ----- end:loop through string
            # +++++ beg:build result
            sNav=''.join(lNav)
            # ----- end:build result
            return sNav
        except:
            logging.error(traceback.format_exc())
            return ''

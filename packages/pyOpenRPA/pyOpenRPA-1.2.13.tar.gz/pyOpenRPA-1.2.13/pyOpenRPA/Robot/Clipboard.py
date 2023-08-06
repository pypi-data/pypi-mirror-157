import win32clipboard
####################################
#Info: Clipboard module of the Robot app (OpenRPA - Robot)
####################################
# GUI Module - interaction with Windows clipboard

def Get():
    """
    Получить текстовое содержимое буфера обмена.

    .. code-block:: python

        # Clipboard: Взаимодействие с буфером
        from pyOpenRPA.Robot import Clipboard
        lClipStr = Clipboard.Get()

    :return: Текстовое содержимое буфера обмена
    :rtype: str
    """
    return ClipboardGet()

def Set(inTextStr:str):
    """
    Установить текстовое содержимое в буфер обмена.

    .. code-block:: python

        # Clipboard: Взаимодействие с буфером
        from pyOpenRPA.Robot import Clipboard
        lClipStr = Clipboard.Set(inTextStr="HELLO WORLD")

    :param inTextStr: Текстовое содержимое для установки в буфера обмена
    :type inTextStr: str
    """
    ClipboardSet(inText=inTextStr)

def ClipboardGet():
    win32clipboard.OpenClipboard()
    lResult = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    return lResult

def ClipboardSet(inText):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT,inText)
    win32clipboard.CloseClipboard()

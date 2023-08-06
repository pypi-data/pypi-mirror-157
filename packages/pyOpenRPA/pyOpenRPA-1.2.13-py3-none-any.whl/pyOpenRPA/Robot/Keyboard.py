from keyboard import *
import time

# Настройки модуля Keyboard
WAIT_AFTER_SEC_FLOAT = 0.4 # Время, которое ожидать после выполнения любой операции модуля Keyboard. Настройка является единой для всех участов кода, использующих модуль Keyboard. Если для некоторой функции требуется изменить данное время ожидания, то в отношении этой функции можно применить соответсвующий аргумент.

# ШЕСТНАДЦАТИРИЧНЫЙ СКАН-КОД В РУССКОЙ РАСКЛАДКЕ (НЕЗАВИСИМО ОТ ВЫБРАННОГО ЯЗЫКА НА КЛАВИАТУРЕ) 
# ОТОБРАЖЕНИЕ СКАН КОДОВ НА КЛАВИАТУРЕ https://snipp.ru/handbk/scan-codes

KEY_RUS_Ф = 0x1E #A
KEY_RUS_И = 0x30 #B
KEY_RUS_С = 0x2E #C
KEY_RUS_В = 0x20 #D
KEY_RUS_У = 0x12 #E
KEY_RUS_А = 0x21 #F
KEY_RUS_П = 0x22 #G
KEY_RUS_Р = 0x23 #H
KEY_RUS_Ш = 0x17 #I
KEY_RUS_О = 0x24 #J
KEY_RUS_Л = 0x25 #K
KEY_RUS_Д = 0x26 #L
KEY_RUS_Ь = 0x32 #M
KEY_RUS_Т = 0x31 #N
KEY_RUS_Щ = 0x18 #O
KEY_RUS_З = 0x19 #P
KEY_RUS_Й = 0x10 #Q
KEY_RUS_К = 0x13 #R
KEY_RUS_Ы = 0x1F #S
KEY_RUS_Е = 0x14 #T
KEY_RUS_Г = 0x16 #U
KEY_RUS_М = 0x2F #V
KEY_RUS_Ц = 0x11 #W
KEY_RUS_Ч = 0x2D #X
KEY_RUS_Н = 0x15 #Y
KEY_RUS_Я = 0x2C #Z
KEY_RUS_Ё = 0x29 #~
KEY_RUS_Ж = 0x27 #:
KEY_RUS_Б = 0x33 #<
KEY_RUS_Ю = 0x34 #>
KEY_RUS_Х = 0x1A #[
KEY_RUS_Ъ = 0x1B #]
KEY_RUS_Э = 0x28 #'

KEY_ENG_A = 0x1E #A
KEY_ENG_B = 0x30 #B
KEY_ENG_C = 0x2E #C
KEY_ENG_D = 0x20 #D
KEY_ENG_E = 0x12 #E
KEY_ENG_F = 0x21 #F
KEY_ENG_G = 0x22 #G
KEY_ENG_H = 0x23 #H
KEY_ENG_I = 0x17 #I
KEY_ENG_J = 0x24 #J
KEY_ENG_K = 0x25 #K
KEY_ENG_L = 0x26 #L
KEY_ENG_M = 0x32 #M
KEY_ENG_N = 0x31 #N
KEY_ENG_O = 0x18 #O
KEY_ENG_P = 0x19 #P
KEY_ENG_Q = 0x10 #Q
KEY_ENG_R = 0x13 #R
KEY_ENG_S = 0x1F #S
KEY_ENG_T = 0x14 #T
KEY_ENG_U = 0x16 #U
KEY_ENG_V = 0x2F #V
KEY_ENG_W = 0x11 #W
KEY_ENG_X = 0x2D #X
KEY_ENG_Y = 0x15 #Y
KEY_ENG_Z = 0x2C #Z


KEY_HOT_NUMPAD_0 = 0x52
KEY_HOT_NUMPAD_1 = 0x4F
KEY_HOT_NUMPAD_2 = 0x50
KEY_HOT_NUMPAD_3 = 0x51
KEY_HOT_NUMPAD_4 = 0x4B
KEY_HOT_NUMPAD_5 = 0x4C
KEY_HOT_NUMPAD_6 = 0x4D
KEY_HOT_NUMPAD_7 = 0x47
KEY_HOT_NUMPAD_8 = 0x48
KEY_HOT_NUMPAD_9 = 0x49
KEY_HOT_NUMPAD_ASTERISK = 0x37 #*
KEY_HOT_NUMPAD_PLUS = 0x4E
KEY_HOT_NUMPAD_MINUS = 0x4A
KEY_HOT_NUMPAD_DELETE = 0x53
KEY_HOT_NUMPAD_SOLIDUS = 0x35 #/
KEY_HOT_NUMPAD_ENTER = 0x11c

KEY_HOT_F1 = 0x3B
KEY_HOT_F2 = 0x3C
KEY_HOT_F3 = 0x3D
KEY_HOT_F4 = 0x3E
KEY_HOT_F5 = 0x3F
KEY_HOT_F6 = 0x40
KEY_HOT_F7 = 0x41
KEY_HOT_F8 = 0x42
KEY_HOT_F9 = 0x43
KEY_HOT_F10 = 0x44
KEY_HOT_F11 = 0x57
KEY_HOT_F12 = 0x58
KEY_HOT_F13 = 0x7C
KEY_HOT_F14 = 0x7D
KEY_HOT_F15 = 0x7E
KEY_HOT_F16 = 0x7F
KEY_HOT_F17 = 0x80
KEY_HOT_F18 = 0x81
KEY_HOT_F19 = 0x82
KEY_HOT_F20 = 0x83
KEY_HOT_F21 = 0x84
KEY_HOT_F22 = 0x85
KEY_HOT_F23 = 0x86
KEY_HOT_F24 = 0x87

KEY_HOT_TILDE = 0x29 #~
KEY_HOT_COLON = 0x27 #:
KEY_HOT_PLUS = 0x0D #+
KEY_HOT_MINUS = 0x0C #-
KEY_HOT_LESS_THAN = 0x33 #< ,
KEY_HOT_GREATER_THAN = 0x34 #> .
KEY_HOT_SOLIDUS = 0x35 #/ ?
KEY_HOT_SQUARE_BRACKET_LEFT = 0x1A #[
KEY_HOT_SQUARE_BRACKET_RIGHT = 0x1B #]
KEY_HOT_APOSTROPHE = 0x28 #' "
KEY_HOT_VERTICAL_LINE = 0x2B #| \

KEY_HOT_ESC = 0x1
KEY_HOT_BACKSPACE = 0x0E
KEY_HOT_TAB = 0x0F
KEY_HOT_ENTER = 0x1C
KEY_HOT_CONTEXT_MENU = 0x15D
KEY_HOT_SHIFT_LEFT = 0x2A
KEY_HOT_SHIFT_RIGHT = 0x36
KEY_HOT_CTRL_LEFT = 0x1D
KEY_HOT_CTRL_RIGHT = 0x11D
KEY_HOT_ALT_LEFT = 0x38
KEY_HOT_ALT_RIGHT = 0x138
KEY_HOT_WIN_LEFT = 57435 #OLD AND DONT WORK 0x5B
KEY_HOT_WIN_RIGHT = 57436 #OLD AND DONT WORK 0x5C
KEY_HOT_CAPS_LOCK = 0x3A
KEY_HOT_NUM_LOCK = 0x45
KEY_HOT_SCROLL_LOCK = 0x46
KEY_HOT_END = 0x4F
KEY_HOT_HOME = 0x47
KEY_HOT_SPACE = 0x39
KEY_HOT_PAGE_UP = 0x49
KEY_HOT_PAGE_DOWN = 0x51
KEY_HOT_CLEAR = 0x4C
KEY_HOT_LEFT = 0x4B
KEY_HOT_UP = 0x48
KEY_HOT_RIGHT = 0x4D
KEY_HOT_DOWN = 0x50
KEY_HOT_PRINT_SCREEN = 0x137
KEY_HOT_INSERT = 0x52
KEY_HOT_DELETE = 0x53

KEY_HOT_0 = 0xB
KEY_HOT_1 = 0x2
KEY_HOT_2 = 0x3
KEY_HOT_3 = 0x4
KEY_HOT_4 = 0x5
KEY_HOT_5 = 0x6
KEY_HOT_6 = 0x7
KEY_HOT_7 = 0x8
KEY_HOT_8 = 0x9
KEY_HOT_9 = 0xA

def Write(inTextStr:str, inDelayFloat:float=0, inRestoreStateAfterBool:bool=True, inExactBool:bool=None, inWaitAfterSecFloat:float=WAIT_AFTER_SEC_FLOAT):
    """
    Печатает текст, который был передан в переменной inTextStr (поддерживает передачу в одной строке символов разного языка). Не зависит от текущей раскладки клавиатуры! Посылает искусственные клавишные события в ОС, моделируя печать данного текста. Знаки, не доступные на клавиатуре, напечатаны как явный unicode знаки, использующие определенную для ОС функциональность, такие как alt+codepoint.
    Чтобы гарантировать текстовую целостность, все в настоящее время нажатые ключи выпущены прежде текст напечатан, и модификаторы восстановлены впоследствии.

    ВНИМАНИЕ! ПЕЧАТАЕТ ЛЮБУЮ СТРОКУ, ДАЖЕ В СОЧЕТАНИИ НЕСКОЛЬКИХ ЯЗЫКОВ ОДНОВРЕМЕННО. ДЛЯ РАБОТЫ С ГОРЯЧИМИ КЛАВИШАМИ ИСПОЛЬЗУЙ ФУНКЦИЮ Send, Up, Down, HotkeyCombination

    .. code-block:: python

        # Keyboard: Взаимодействие с клавиатурой
        from pyOpenRPA.Robot import Keyboard
        Keyboard.Write("Привет мой милый мир! Hello my dear world!")

    :param inTextStr: Текст, отправляемый на печать. Не зависит от текущей раскладки клавиатуры! 
    :type inTextStr: str
    :param inDelayFloat: Число секунд, которое ожидать между нажатиями. По умолчанию 0
    :type inDelayFloat: float, опциональный
    :param inRestoreStateAfterBool: Может использоваться, чтобы восстановить регистр нажатых ключей после того, как текст напечатан, т.е. нажимает ключи, которые были выпущены в начало.
    :type inRestoreStateAfterBool: bool, опциональный
    :param inExactBool: Печатает все знаки как явный unicode. Необязательный параметр
    :type inExactBool: bool, опциональный
    :param inWaitAfterSecFloat: Количество секунд, которые ожидать после выполнения операции. По умолчанию установлено в настройках модуля Keyboard (базовое значение 0.4)
    :type inWaitAfterSecFloat: float, опциональный
    """
    write(text=inTextStr, delay=inDelayFloat, restore_state_after=inRestoreStateAfterBool, exact=inExactBool)
    time.sleep(inWaitAfterSecFloat)

def HotkeyCombination(*inKeyList, inDelaySecFloat = 0.3,inWaitAfterSecFloat:float=WAIT_AFTER_SEC_FLOAT):
    """Получает перечень клавиш для одновременного нажатия. Между нажатиями программа ожидания время inDelaySecFloat
    ВНИМАНИЕ! НЕ ЗАВИСИТ ОТ ТЕКУЩЕЙ РАСКЛАДКИ КЛАВИАТУРЫ

    .. code-block:: python

        # Keyboard: Взаимодействие с клавиатурой
        from pyOpenRPA.Robot import Keyboard
        Keyboard.HotkeyCombination(Keyboard.KEY_HOT_CTRL_LEFT,Keyboard.KEY_ENG_A) # Ctrl + a
        Keyboard.HotkeyCombination(Keyboard.KEY_HOT_CTRL_LEFT,Keyboard.KEY_ENG_C) # Ctrl + c
        Keyboard.HotkeyCombination(Keyboard.KEY_HOT_CTRL_LEFT,Keyboard.KEY_ENG_A)
        Keyboard.HotkeyCombination(Keyboard.KEY_HOT_ALT_LEFT,Keyboard.KEY_HOT_TAB, Keyboard.KEY_HOT_TAB)
    
    :param inKeyList: Список клавиш для одновременного нажатия. Перечень клавиш см. в разделе "Коды клавиш". Пример: KEY_HOT_CTRL_LEFT,KEY_ENG_A
    :param inDelaySecFloat: Интервал между нажатиями. Необходим в связи с тем, что операционной системе требуется время на реакцию на нажатие клавиш, по умолчанию: 0.3
    :type inDelaySecFloat: float, опциональный
    :param inWaitAfterSecFloat: Количество секунд, которые ожидать после выполнения операции. По умолчанию установлено в настройках модуля Keyboard (базовое значение 0.4)
    :type inWaitAfterSecFloat: float, опциональный
    """
    for l_key_item in inKeyList:
        if l_key_item == inKeyList[-1]:
            send(l_key_item)
        else:
            press(l_key_item)
        time.sleep(inDelaySecFloat)
    lRevKeyList = list(reversed(inKeyList))
    for l_key_item in lRevKeyList:
        if l_key_item == lRevKeyList[0]:
            pass
        else:
            release(l_key_item)
        time.sleep(inDelaySecFloat)
    time.sleep(inWaitAfterSecFloat)

def HotkeyCtrlA_CtrlC(inWaitAfterSecFloat:float=0.4) -> None:
    """Выполнить выделение текста, после чего скопировать его в буфер обмена
    ВНИМАНИЕ! НЕ ЗАВИСИТ ОТ ТЕКУЩЕЙ РАСКЛАДКИ КЛАВИАТУРЫ
    
    .. code-block:: python

        # Keyboard: Взаимодействие с клавиатурой
        from pyOpenRPA.Robot import Keyboard
        Keyboard.HotkeyCtrlA_CtrlC() # Отправить команды: выделить все, скопировать в буфер обмена
    
    :param inWaitAfterSecFloat: Количество секунд, которые ожидать после выполнения операции. По умолчанию установлено в настройках модуля Keyboard (базовое значение 0.4)
    :type inWaitAfterSecFloat: float, опциональный
    """
    HotkeyCombination(KEY_HOT_CTRL_LEFT,KEY_ENG_A) # Ctrl + a
    HotkeyCombination(KEY_HOT_CTRL_LEFT,KEY_ENG_C) # Ctrl + c
    time.sleep(inWaitAfterSecFloat)

def Send(inKeyInt:int, inDoPressBool:bool=True, inDoReleaseBool:bool=True,inWaitAfterSecFloat:float=WAIT_AFTER_SEC_FLOAT) -> None:
    """
    Имитация нажатия/отпускания любой физической клавиши. Посылает событие в операционную систему, которые выполняет нажатие и отпускание данной клавиши
    
    ВНИМАНИЕ! ПРИ ПОПЫТКЕ ПЕЧАТИ ТЕКСТА БУДЕТ УЧИТЫВАТЬ ТЕКУЩУЮ РАСКЛАДКУ КЛАВИАТУРЫ. ДЛЯ ПЕЧАТИ ТЕКСТА ИСПОЛЬЗУЙ Write!

    .. code-block:: python

        # Keyboard: Взаимодействие с клавиатурой
        from pyOpenRPA.Robot import Keyboard
        Keyboard.Send(Keyboard.KEY_ENG_A) # Нажать клавишу A. Если будет активна русская раскладка, то будет выведена буква ф.

    :param inKeyInt: Перечень клавиш см. в разделе "Коды клавиш". Пример: KEY_HOT_CTRL_LEFT,KEY_ENG_A
    :type inKeyInt: int
    :param inDoPressBool: Выполнить событие нажатия клавиши, По умолчанию True
    :type inDoPressBool: bool, опциональный
    :param inDoReleaseBool: Выполнить событие отпускания клавиши, По умолчанию True
    :type inDoReleaseBool: bool, опциональный
    :param inWaitAfterSecFloat: Количество секунд, которые ожидать после выполнения операции. По умолчанию установлено в настройках модуля Keyboard (базовое значение 0.4)
    :type inWaitAfterSecFloat: float, опциональный
    """
    send(hotkey=inKeyInt, do_press=inDoPressBool, do_release=inDoReleaseBool)
    time.sleep(inWaitAfterSecFloat)
    
def Up(inKeyInt:int, inWaitAfterSecFloat:float=WAIT_AFTER_SEC_FLOAT) -> None:
    """
    Отпустить (поднять) клавишу. Если клавиша уже была поднята, то ничего не произойдет.
    
    ВНИМАНИЕ! ПРИ ПОПЫТКЕ ПЕЧАТИ ТЕКСТА БУДЕТ УЧИТЫВАТЬ ТЕКУЩУЮ РАСКЛАДКУ КЛАВИАТУРЫ. ДЛЯ ПЕЧАТИ ТЕКСТА ИСПОЛЬЗУЙ Write!

    .. code-block:: python

        # Keyboard: Взаимодействие с клавиатурой
        from pyOpenRPA.Robot import Keyboard
        Keyboard.Up(Keyboard.KEY_ENG_A) # Отпустить клавишу A.

    :param inKeyInt: Перечень клавиш см. в разделе "Коды клавиш". Пример: KEY_HOT_CTRL_LEFT, KEY_ENG_A
    :type inKeyInt: int
    :param inWaitAfterSecFloat: Количество секунд, которые ожидать после выполнения операции. По умолчанию установлено в настройках модуля Keyboard (базовое значение 0.4)
    :type inWaitAfterSecFloat: float, опциональный
    """
    send(hotkey=inKeyInt, do_press=False, do_release=True)
    time.sleep(inWaitAfterSecFloat)
    
def Down(inKeyInt:int, inWaitAfterSecFloat:float=WAIT_AFTER_SEC_FLOAT) -> None:
    """
    Нажать (опустить) клавишу. Если клавиша уже была опущена, то ничего не произойдет.
    
    ВНИМАНИЕ! ПРИ ПОПЫТКЕ ПЕЧАТИ ТЕКСТА БУДЕТ УЧИТЫВАТЬ ТЕКУЩУЮ РАСКЛАДКУ КЛАВИАТУРЫ. ДЛЯ ПЕЧАТИ ТЕКСТА ИСПОЛЬЗУЙ Write!

    .. code-block:: python

        # Keyboard: Взаимодействие с клавиатурой
        from pyOpenRPA.Robot import Keyboard
        Keyboard.Down(Keyboard.KEY_ENG_A) # Отпустить клавишу A.

    :param inKeyInt: Перечень клавиш см. в разделе "Коды клавиш". Пример: KEY_HOT_CTRL_LEFT, KEY_ENG_A
    :type inKeyInt: int
    :param inWaitAfterSecFloat: Количество секунд, которые ожидать после выполнения операции. По умолчанию установлено в настройках модуля Keyboard (базовое значение 0.4)
    :type inWaitAfterSecFloat: float, опциональный
    """
    send(hotkey=inKeyInt, do_press=True, do_release=False)
    time.sleep(inWaitAfterSecFloat)

def IsDown(inKeyInt:int) -> bool:
    """
    Проверить, опущена ли клавиша. Вернет True если опущена; False если поднята.
    
    ВНИМАНИЕ! ПРИ ПОПЫТКЕ ПЕЧАТИ ТЕКСТА БУДЕТ УЧИТЫВАТЬ ТЕКУЩУЮ РАСКЛАДКУ КЛАВИАТУРЫ. ДЛЯ ПЕЧАТИ ТЕКСТА ИСПОЛЬЗУЙ Write!

    .. code-block:: python

        # Keyboard: Взаимодействие с клавиатурой
        from pyOpenRPA.Robot import Keyboard
        lKeyAIsPressedBool = Keyboard.IsDown(Keyboard.KEY_ENG_A) # Проверить, опущена ли клавиша A.

    :param inKeyInt: Перечень клавиш см. в разделе "Коды клавиш". Пример: KEY_HOT_CTRL_LEFT, KEY_ENG_A
    :type inKeyInt: int
    """
    return is_pressed(inKeyInt)

def Wait(inKeyInt:int,inWaitAfterSecFloat:float=WAIT_AFTER_SEC_FLOAT):
    """Блокирует осуществление программы, пока данная обозначенная клавиша не будет нажата.
    ВНИМАНИЕ! НЕ ЗАВИСИТ ОТ ТЕКУЩЕЙ РАСКЛАДКИ КЛАВИАТУРЫ. ОЖИДАЕТ НАЖАТИЕ СООТВЕТСВУЮЩЕЙ ФИЗИЧЕСКОЙ КЛАВИШИ
    
    .. code-block:: python

        # Keyboard: Взаимодействие с клавиатурой
        from pyOpenRPA.Robot import Keyboard
        Keyboard.Wait(Keyboard.KEY_ENG_A) # Ждать нажатие клавиши A.

    :param inKeyInt: Перечень клавиш см. в разделе "Коды клавиш". Пример: KEY_HOT_CTRL_LEFT,KEY_ENG_A
    :type inKeyInt: int
    :param inWaitAfterSecFloat: Количество секунд, которые ожидать после выполнения операции. По умолчанию установлено в настройках модуля Keyboard (базовое значение 0.4)
    :type inWaitAfterSecFloat: float, опциональный
    """
    wait(hotkey=inKeyInt)
    time.sleep(inWaitAfterSecFloat)

key_to_scan_codes("win") # 2022 06 10 Люблю смотреть скан код клавиши Виндовс :)
import locale
import re

from kivy.uix.textinput import TextInput

class NumericTextInput(TextInput):
    locale.setlocale(locale.LC_ALL, '')

    def insert_text(self, substring, from_undo=False):
        '''get thousand seperator and decimal char. used by system #update this to global variables'''
        number_toget_locale = '1000.1'
        format_number_toget_locale = locale.format_string("%f", locale.atof(number_toget_locale), grouping=True)
        system_setthou = format_number_toget_locale[1]
        system_setdec = format_number_toget_locale[5]

        # Ensure only numbers and dot can be entered to textinput
        if re.match((u'^[0-9.]*$'), substring):
            cc, cr = self.cursor
            # return, if first textinput is '0' and entered figure has '0' as well
            if self._lines[cr]=='0' and substring=='0':
                return
            # return, if textinput has a decimal point and entered figure as a decimal point as well
            if '.' in self._lines[cr] and '.' in substring:
                return

            # (incase of paste) return, if entered figure is not a float with maximum of 6d.p
            '''#to be updated so user can paste float or integer with thousand seperator up to 6d.p'''
            if not re.match((u'^[0-9]*\\.?[0-9]{,6}$'), substring):
                '''#proposed update below'''
                # or not re.match((u'^-?[0-9]{,3},([0-9]{3,3},)*[0-9]{3,3}\\.?[0-9]{,6}$'), substring) \
                # or not re.match((u'^-?[0-9]{,3}\\.?[0-9]{,6}$'), substring):
                return

            # return if textinput has 6d.p and user tries to enter another number in decimal place
            if re.match((u"^[0-9]{,3}[\s,.]([0-9]{3,3}[\s,.])*[0-9]{3,3}\\.?[0-9]{6,6}$"),self._lines[cr]) or re.match((u'^[0-9]{,3}\\.?[0-9]{6,6}$'), self._lines[cr]):
                # checks if cursor position is around the filled 6d.p
                if cc in range(len(self._lines[cr])-6,len(self._lines[cr])+1):
                    return
            super(NumericTextInput, self).insert_text(substring, from_undo=from_undo)
            cc, cr = self.cursor

            # convert self._lines to float and
            # format resulting numeric text to include thousand seperator
            new_text=locale.format_string("%f",locale.atof(self._lines[cr]), grouping=True)
            new_text_fmt=new_text

            # if user inputs '.', strip only trailing zeros
            if system_setdec in substring:
                 new_text=new_text.rstrip('0')
            else:
                 new_text=new_text.rstrip('0').rstrip(system_setdec)

            # increase cursor column position to account for
            # thousand seperator included automatically in text
            ntext_thou=new_text.count(system_setthou)
            lines_thou=self._lines[cr].count(system_setthou)
            curs_adjus=ntext_thou-lines_thou
            if len(new_text)>len(self._lines[cr]):
                if ntext_thou>lines_thou:
                    new_cursor=list(self._cursor)
                    new_cursor[0]=new_cursor[0]+curs_adjus
                    self._cursor=tuple(new_cursor)

            # so user can input '0' after decimal sign with no glitches
            # if user inputs tenth placed zero or decimal place zero greater than tenth
            finddecipos_lines=self._lines[cr].find(system_setdec)
            finddecipos_ntext= new_text_fmt.find(system_setdec)
            if '0' in substring and cc == len(new_text) + 2 and system_setdec in self._lines[cr] and cc == finddecipos_lines+2:
                    new_text = new_text + system_setdec + '0'
            elif '0' in substring and cc>finddecipos_lines+1 and system_setdec in self._lines[cr]:
                 new_text=new_text_fmt[:finddecipos_ntext]+self._lines[cr][finddecipos_lines:]

            # set line text with new_text
            self._set_line_text(cr, new_text)

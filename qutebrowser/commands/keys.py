from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
import logging
import re

class KeyParser(QObject):
    keystring = ''
    set_cmd_text = pyqtSignal(str)
    keystring_updated = pyqtSignal(str)
    key_to_cmd = {}

    def from_cmd_dict(self, d):
        for cmd in d.values():
            if cmd.key is not None:
                logging.debug('registered: {} -> {}'.format(cmd.name, cmd.key))
                self.key_to_cmd[cmd.key] = cmd

    def handle(self, e):
        self._handle(e)
        self.keystring_updated.emit(self.keystring)

    def _handle(self, e):
        logging.debug('Got key: {} / text: "{}"'.format(e.key(), e.text()))
        txt = e.text().strip()
        if not txt:
            logging.debug('Ignoring, no text')
            return

        self.keystring += txt

        if self.keystring == ':':
            self.set_cmd_text.emit(':')
            self.keystring = ''
            return

        (countstr, cmdstr) = re.match('^(\d*)(.*)', self.keystring).groups()

        if not cmdstr:
            return

        # FIXME this doesn't handle ambigious keys correctly.
        #
        # If a keychain is ambigious, we probably should set up a QTimer with a
        # configurable timeout, which triggers cmd.run() when expiring. Then
        # when we enter _handle() again in time we stop the timer.
        try:
            cmd = self.key_to_cmd[cmdstr]
        except KeyError:
            if self._partial_match(cmdstr, txt):
                logging.debug('No match for "{}" (added {})'.format(
                    self.keystring, txt))
                return
            else:
                logging.debug('Giving up with "{}", no matches'.format(
                    self.keystring))
                self.keystring = ''
                return

        self.keystring = ''
        count = int(countstr) if countstr else None

        if cmd.nargs and cmd.nargs != 0:
            logging.debug('Filling statusbar with partial command {}'.format(
                cmd.name))
            self.set_cmd_text.emit(':{} '.format(cmd.name))
        elif count is not None:
            cmd.run(count=count)
        else:
            cmd.run()

    def _partial_match(self, cmdstr, txt):
        pos = len(cmdstr)
        for cmd in self.key_to_cmd:
            try:
                if cmdstr[-1] == cmd[pos-1]:
                    return True
            except IndexError:
                continue
        else:
            return False

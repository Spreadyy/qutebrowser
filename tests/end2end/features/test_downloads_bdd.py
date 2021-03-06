# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2015-2016 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import shlex

import pytest
import pytest_bdd as bdd
bdd.scenarios('downloads.feature')


pytestmark = pytest.mark.qtwebengine_todo("Downloads not implemented yet",
                                          run=False)


PROMPT_MSG = ("Asking question <qutebrowser.utils.usertypes.Question "
              "default={!r} mode=<PromptMode.download: 5> "
              "text='Save file to:'>, *")


@bdd.given("I set up a temporary download dir")
def temporary_download_dir(quteproc, tmpdir):
    quteproc.set_setting('storage', 'prompt-download-directory', 'false')
    quteproc.set_setting('storage', 'remember-download-directory', 'false')
    quteproc.set_setting('storage', 'download-directory', str(tmpdir))
    (tmpdir / 'subdir').ensure(dir=True)
    try:
        os.mkfifo(str(tmpdir / 'fifo'))
    except AttributeError:
        pass
    unwritable = tmpdir / 'unwritable'
    unwritable.ensure(dir=True)
    unwritable.chmod(0)


@bdd.given("I clean old downloads")
def clean_old_downloads(quteproc):
    quteproc.send_cmd(':download-cancel --all')
    quteproc.send_cmd(':download-clear')


@bdd.when("I wait until the download is finished")
def wait_for_download_finished(quteproc):
    quteproc.wait_for(category='downloads', message='Download * finished')


@bdd.when(bdd.parsers.parse("I wait until the download {name} is finished"))
def wait_for_download_finished_name(quteproc, name):
    quteproc.wait_for(category='downloads',
                      message='Download {} finished'.format(name))


@bdd.when(bdd.parsers.parse('I wait for the download prompt for "{path}"'))
def wait_for_download_prompt(tmpdir, quteproc, path):
    full_path = path.replace('(tmpdir)', str(tmpdir)).replace('/', os.sep)
    quteproc.wait_for(message=PROMPT_MSG.format(full_path))


@bdd.when("I download an SSL page")
def download_ssl_page(quteproc, ssl_server):
    quteproc.send_cmd(':download https://localhost:{}/'
                      .format(ssl_server.port))


@bdd.then(bdd.parsers.parse("The downloaded file {filename} should not exist"))
def download_should_not_exist(filename, tmpdir):
    path = tmpdir / filename
    assert not path.check()


@bdd.then(bdd.parsers.parse("The downloaded file {filename} should exist"))
def download_should_exist(filename, tmpdir):
    path = tmpdir / filename
    assert path.check()


@bdd.then(bdd.parsers.parse("The downloaded file {filename} should contain "
                            "{size} bytes"))
def download_size(filename, size, tmpdir):
    path = tmpdir / filename
    assert path.size() == int(size)


@bdd.then(bdd.parsers.parse('The download prompt should be shown with '
                            '"{path}"'))
def download_prompt(tmpdir, quteproc, path):
    full_path = path.replace('(tmpdir)', str(tmpdir)).replace('/', os.sep)
    quteproc.wait_for(message=PROMPT_MSG.format(full_path))
    quteproc.send_cmd(':leave-mode')


@bdd.when("I open the download")
def download_open(quteproc):
    cmd = '{} -c "import sys; print(sys.argv[1])"'.format(
        shlex.quote(sys.executable))
    quteproc.send_cmd(':download-open {}'.format(cmd))


@bdd.when("I open the download with a placeholder")
def download_open_placeholder(quteproc):
    cmd = '{} -c "import sys; print(sys.argv[1])"'.format(
        shlex.quote(sys.executable))
    quteproc.send_cmd(':download-open {} {{}}'.format(cmd))


@bdd.when("I directly open the download")
def download_open_with_prompt(quteproc):
    cmd = '{} -c pass'.format(shlex.quote(sys.executable))
    quteproc.send_cmd(':prompt-open-download {}'.format(cmd))


@bdd.when(bdd.parsers.parse("I delete the downloaded file {filename}"))
def delete_file(tmpdir, filename):
    (tmpdir / filename).remove()


@bdd.then("the FIFO should still be a FIFO")
def fifo_should_be_fifo(tmpdir):
    assert tmpdir.exists() and not os.path.isfile(str(tmpdir / 'fifo'))

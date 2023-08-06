#!/usr/bin/env python3

## Test the pylit.py literal python module's user interface
## ========================================================
##
## :Date:      $Date: 2007-05-17 $
## :Version:   SVN-Revision $Revision: 45 $
## :URL:       $URL: svn+ssh://svn.berlios.de/svnroot/repos/pylit/trunk/test/pylit_ui_test.py $
## :Copyright: 2006 Guenter Milde.
##             Released under the terms of the GNU General Public License
##             (v. 2 or later)
##
## .. contents::
##
## ::

"""pylit_test.py: test the "literal python" module's user interface"""

import argparse
import copy
from pprint import pprint

from pylit import *
from pylit_test import (text, stripped_text, textdata,
                        code, stripped_code, codedata)

import nose

## Global defaults
## ===============
##
## ::

def test_global_option_defaults():
    """dictionary of programming languages and extensions"""
    assert defaults.languages[".py"] == "python"
    assert defaults.languages[".sl"] == "slang"
    assert defaults.languages[".cc"] == "c++"
    assert defaults.languages[".c"] == "c"


## Command line use
## ================
##
## Test the option parsing::

class test_PylitOptions:
    """Test the PylitOption class"""
    def setUp(self):
        self.options = PylitOptions()

    def test_args_parsing(self):
        """parse cmd line args with `ArgumentParser.parse_args()`"""
        # "1st non option arg is infile, 2nd is outfile"
        values = self.options.parser.parse_args(["--txt2code", "text.txt", "code.py"])
        print(values.infile)
        assert values.infile == "text.txt"
        assert values.outfile == "code.py"
        # option with argument
        values = self.options.parser.parse_args(['in.py', '--language', 'slang'])
        assert values.language == "slang"

    def test_args_comment_string(self):
        """command line arg should appear in values"""
        values = self.options(['in.py', '--comment-string=% '])
        pprint(vars(values))
        assert values.comment_string == "% "

    def test_args_code_block_marker(self):
        """command line option --code-block-marker should set option value"""
        values = self.options(['in.py', '--code-block-marker=.. test-dir::'])
        pprint(vars(values))
        assert values.code_block_marker == '.. test-dir::'

    def test_get_outfile_name(self):
        """should return a sensible outfile name given an infile name"""
        # return stdout for stdin
        values = copy.copy(defaults)
        values.infile = '-'
        assert "-" == self.options._get_outfile_name(values)
        # return with ".txt" stripped
        values = copy.copy(defaults)
        values.infile = 'foo.py.txt'
        assert "foo.py" == self.options._get_outfile_name(values)
        # return with ".txt" added if extension marks code file
        values = copy.copy(defaults)
        values.infile = 'foo.py'
        assert "foo.py.txt" == self.options._get_outfile_name(values)
        values = copy.copy(defaults)
        values.infile = 'foo.sl'
        assert "foo.sl.txt" == self.options._get_outfile_name(values)
        values = copy.copy(defaults)
        values.infile = 'foo.c'
        assert "foo.c.txt" == self.options._get_outfile_name(values)
        # return with ".txt" added if txt2code == False (not None!)
        values = copy.copy(defaults)
        values.infile = 'foo.py'
        values.txt2code = False
        assert "foo.py.txt" == self.options._get_outfile_name(values)
        # catchall: add ".out" if no other guess possible
        values = copy.copy(defaults)
        values.infile = 'foo'
        values.txt2code = None
        print(self.options._get_outfile_name(values))
        assert "foo.out" == self.options._get_outfile_name(values)

    def test_complete_values(self):
        """Basic test of the option completion"""
        values = copy.copy(defaults)
        values.infile = "foo"
        values = self.options.complete_values(values)
        # the following options should be set:
        print('txt2code after:', values.txt2code)
        print(values.outfile)
        assert values.outfile == "foo.out" # fallback extension .out added
        print(values.txt2code)
        assert values.txt2code == True # the default
        print(values.language)
        assert values.language == "python" # the default

    def test_complete_values_txt(self):
        """Test the option completion with a text input file"""
        values = copy.copy(defaults)
        values.infile = "foo.txt"
        values = self.options.complete_values(values)
        # should set outfile (see also `test_get_outfile_name`)
        assert values.outfile == "foo"
        # should set conversion direction according to extension
        assert values.txt2code == True

    def test_complete_values_code(self):
        """Test the option completion with a code input file"""
        values = copy.copy(defaults)
        values.infile = "foo.py"
        values = self.options.complete_values(values)
        # should set outfile name
        assert values.outfile == "foo.py.txt"
        # should set conversion directions according to extension
        print(values.txt2code)
        assert values.txt2code == False, "set conversion according to extension"

    def test_complete_values_dont_overwrite(self):
        """The option completion must not overwrite existing option values"""
        values = copy.copy(defaults)
        values.infile = "foo.py"
        values.outfile = "bar.txt"
        values.txt2code = True
        values = self.options.complete_values(values)
        pprint(values)
        assert values.outfile == "bar.txt"
        assert values.txt2code == True

    def test_complete_values_language_infile(self):
        """set the language from the infile extension"""
        values = copy.copy(defaults)
        values.infile = "foo.cc"
        values = self.options.complete_values(values)
        pprint(values)
        assert values.language == "c++"

    def test_complete_values_language_outfile(self):
        """set the language from the outfile extension"""
        values = copy.copy(defaults)
        values.txt2code = True
        values.infile = 'in-file'
        values.outfile = "foo.sl"
        values = self.options.complete_values(values)
        pprint(values)
        assert values.language == "slang"

    def test_complete_values_language_fallback(self):
        """set the language from the fallback language"""
        values = copy.copy(defaults)
        values.infile = 'in-file'  # required
        values = self.options.complete_values(values)
        pprint(values)
        print("fallback language:", defaults.languages[''])
        assert values.language == defaults.languages['']

    def test_call(self):
        # if setting is not specified, use fallback from module `defaults`
        values = self.options(infile='in-file')
        assert values.txt2code == True
        # default should appear in options
        values = self.options(infile='in-file', txt2code=False)
        # print(values, type(values), dir(values))
        assert values.txt2code == False
        # "cmd line arg should appear as option overwriting default"
        values = self.options(["--txt2code", "foo.sl"], txt2code=False)
        pprint(values)
        assert values.txt2code == True
        assert values.infile == "foo.sl"
        # "cmd line arg should appear as option overwriting default"
        values = self.options(['in-file', '--comment-string=% '],
                              comment_string="##")
        assert values.comment_string == '% '

    def test_call_language(self):
        """test the language setting from filename"""
        values = self.options(["foo.sl"])
        pprint(values)
        assert values.language == "slang"

    def test_call_language_outfile(self):
        """test the language setting from filename"""
        values = self.options(["foo, foo.sl"])
        pprint(values)
        assert values.language == "slang"

## Input and Output streams
## ------------------------
##
## ::

class IOTests:
    """base class for IO tests, sets up and tears down example files in /tmp
    """
    txtpath = "/tmp/pylit_test.py.txt"
    codepath = "/tmp/pylit_test.py"
    outpath = "/tmp/pylit_test.out"
    #
    def setUp(self):
        """Set up the test files"""
        txtfile = open(self.txtpath, 'w')
        txtfile.write(text)
        # txtfile.flush()  # is this needed if we close?
        txtfile.close()
        #
        codefile = open(self.codepath, 'w')
        codefile.write(code)
        # codefile.flush()  # is this needed if we close?
        codefile.close()
    #
    def tearDown(self):
        """clean up after all member tests are done"""
        try:
            os.unlink(self.txtpath)
            os.unlink(self.codepath)
            os.unlink(self.outpath)
        except OSError:
            pass
    #
    def get_output(self):
        """read and return the content of the output file"""
        with open(self.outpath, 'r') as outstream:
            return outstream.read()



class test_Streams(IOTests):
    def test_is_newer(self):
        # this __file__ is older, than code file
        print(__file__, os.path.getmtime(__file__))
        print(self.codepath, os.path.getmtime(self.codepath))
        #
        assert is_newer(self.codepath, __file__) is True, "file1 is newer"
        assert is_newer(__file__, self.codepath) is False, "file2 is newer"
        assert is_newer(__file__, "fffo") is True, "file2 doesnot exist"
        assert is_newer("fflo", __file__) is False, "file1 doesnot exist"
        #
        assert is_newer(__file__, __file__) is None, "equal is not newer"
        assert is_newer("fflo", "fffo") is None, "no file exists -> equal"

    def test_open_streams(self):
        # default should return stdin and -out:
        (instream, outstream) = open_streams()
        assert instream is sys.stdin
        assert outstream is sys.stdout

        # open input and output file
        (instream, outstream) = open_streams(self.txtpath, self.outpath)
        print(type(instream), type(outstream))
        assert type(instream) == type(open(self.txtpath))
        assert type(outstream) == type(open(self.outpath))
        # read something from the input
        assert instream.read() == text
        # write something to the output
        outstream.write(text)
        # check the output, we have to flush first
        outstream.flush()
        outfile = open(self.outpath, 'r')
        assert outfile.read() == text

    def test_open_streams_no_infile(self):
        """should exit with usage info if no infile given"""
        try:
            (instream, outstream) = open_streams("")
            assert False, "should rise IOError"
        except IOError:
            pass

## get_converter
## ~~~~~~~~~~~~~

## Return "right" converter instance (Text2Code or Code2Text instance)::

def test_get_converter():
    # with default or txt2code
    converter = get_converter(textdata)
    print(converter.__class__)
    assert converter.__class__ == Text2Code
    converter = get_converter(textdata, txt2code=False)
    assert converter.__class__ == Code2Text

# the run_doctest runs a doctest on the text version (as doc-string)
class test_Run_Doctest(IOTests):
    """Doctest should run on the text source"""
    def test_doctest_txt2code(self):
        (failures, tests) = run_doctest(self.txtpath, txt2code=True)
        assert (failures, tests) == (0, 0)
    def test_doctest_code2txt(self):
        (failures, tests) = run_doctest(self.codepath, txt2code=False)
        assert (failures, tests) == (0, 0)

## The main() function is called if the script is run from the command line
##
## ::

class test_Main(IOTests):
    """test default operation from command line
    """
    def test_text_to_code(self):
        """test conversion of text file to code file"""
        main(infile=self.txtpath, outfile=self.outpath)
        output = self.get_output()
        print(repr(output))
        assert output == code

    def test_text_to_code_strip(self):
        """test conversion of text file to stripped code file"""
        main(infile=self.txtpath, outfile=self.outpath, strip=True)
        output = self.get_output()
        print(repr(output))
        assert output == stripped_code

    def test_text_to_code_twice(self):
        """conversion should work a second time"""
        main(infile=self.txtpath, outfile=self.outpath)
        main(infile=self.txtpath, outfile=self.outpath, overwrite='yes')
        output = self.get_output()
        print(repr(output))
        assert output == code

    def test_code_to_text(self):
        """test conversion of code file to text file"""
        main(infile=self.codepath, outfile=self.outpath)
        output = self.get_output()
        assert output == text

    def test_code_to_text_strip(self):
        """test conversion of code file to stripped text file"""
        main(infile=self.codepath, outfile=self.outpath, strip=True)
        output = self.get_output()
        assert output == stripped_text

    def test_code_to_text_twice(self):
        """conversion should work also a second time"""
        main(infile=self.codepath, outfile=self.outpath)
        main(infile=self.codepath, outfile=self.outpath, overwrite='yes')
        output = self.get_output()
        assert output == text

    def test_diff(self):
        result = main(infile=self.codepath, diff=True)
        print("diff return value", result)
        assert result is False # no differences found

    def test_diff_with_differences(self):
        """diffing a file to itself should fail, as the input is converted"""
        result = main(infile=self.codepath, outfile=self.codepath, diff=True)
        print("diff return value", result)
        assert result is True # differences found

    def test_execute(self):
        result = main(infile=self.txtpath, execute=True)
        print(result)

    def test_execute_code(self):
        result = main(infile=self.codepath, execute=True)


class test_Programmatic_Use(IOTests):
    """test various aspects of programmatic use"""

    def test_conversion(self):
        (data, out_stream) = open_streams(self.txtpath)
        print("data: %r"%data)
        print("out_stream: %r"%out_stream)
        converter = get_converter(data)
        lines = converter()
        print("output: %r"%lines)
        # lines = converter()
        assert lines == codedata


if __name__ == "__main__":
    nose.runmodule() # requires nose 0.9.1
    sys.exit()

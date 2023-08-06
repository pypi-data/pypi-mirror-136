import abc
import subprocess
import shutil
import glob
import os
import logging


class LatexGenerator(abc.ABC):
    """
    Base class that is used to consume Tex files and produce pdf files
    """

    @abc.abstractmethod
    def generate(self,
                 main_tex_file: str,
                 tex_folder: str = None,
                 texFolder: str = None,
                 latex_args: list[str] = []) -> None:
        """
        Generates the pdf file at the resultFile location given the main_tex
        file if main_tex_file does not have a file extension .tex is assumed,
        if result file is not specified, {main_tex_file}.pdf is assumed
        """
        pass


class PdfLatexGenerator:
    """
    A Latex Generator for PDFLatex, requires pdflatex to be installed in order
    to be used
    """

    def generate(self,
                 main_tex_file: str,
                 tex_folder: str = ".",
                 resultFolder: str = ".",
                 latex_args: list[str] = []) -> None:
        """
        Override of LatexGenerator.generate
        """
        command = ['pdflatex',
                   '-halt-on-error',
                   f'{main_tex_file}'] + latex_args
        logging.info(f"generating pdf with command {command}")
        process = subprocess.Popen(command,
                                   cwd=tex_folder,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderro = process.communicate()
        exitCode = process.returncode
        for file in glob.glob(f"{main_tex_file.split('.')[0]}.*"):
            shutil.move(file, os.path.join(resultFolder, file))
        if exitCode != 0:
            logging.error(f"pflatex had a non-0 exit code: {exitCode}")
            logging.error(stdout.decode('utf-8'))
            raise Exception(stdout)

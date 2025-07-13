import subprocess
import tempfile
from pathlib import Path

import jinja2
import pyvips
from django.core.files.base import File
from django.db import transaction

from noteprinter.settings import BASE_DIR
from notes.models import Note, NoteImage
from notes.utils import random_string, get_file_path


def convert_to_image(pdf_file: Path):
    out_png = pdf_file.with_suffix(".png")
    image = pyvips.Image.pdfload(
        pdf_file,
        page=0,
        dpi=72 * 2
    )

    # Save as PNG
    image.pngsave(
        out_png,
        bitdepth=1,
        compression=9
    )

    subprocess.run(["oxipng", str(out_png), "--strip", "all"], check=True, capture_output=True)
    return out_png, (image.width, image.height)


class NoteRenderer:

    def __init__(self, note: Note):
        self.note = note
        # self.dir = os.path.join(BASE_DIR, "pdfs")
        self.template_dir = BASE_DIR / "notes" / "templates"
        self.env = jinja2.Environment(
            block_start_string=r'\BLOCK{',
            block_end_string='}',
            variable_start_string=r'\VAR{',
            variable_end_string='}',
            comment_start_string=r'\#{',
            comment_end_string='}',
            line_statement_prefix='%#',
            line_comment_prefix='%%',
            trim_blocks=True,
            autoescape=False,  # noqa: S701
            loader=jinja2.FileSystemLoader(self.template_dir)
        )
        # self.env.filters['formatdigit'] = format_digit
        self.template = self.env.get_template('latex/template.tex')

    def generate_latex(self) -> str:
        data = {
            "note": self.note,
        }
        return self.template.render(**data)

    def render_note(self):
        with tempfile.TemporaryDirectory(prefix="note_render_") as tmpdirname:
            tmpdir = Path(tmpdirname)
            print(tmpdir)

            with open(tmpdir / "main.tex", "w") as f:
                f.write(self.generate_latex())
            subprocess.run(
                ["lualatex", "-interaction", "batchmode", "main.tex"],
                check=True,
                capture_output=True,
                cwd=tmpdir
            )
            pdf_file = tmpdir / "main.pdf"
            assert pdf_file.exists()
            png_file, (width, height) = convert_to_image(pdf_file)
            assert png_file.exists()
            with transaction.atomic():
                try:
                    old_image = self.note.image
                    old_image.delete()
                except Note.image.RelatedObjectDoesNotExist:
                    ...
                rand = random_string()

                with png_file.open("rb") as png_f, pdf_file.open("rb") as pdf_f:
                    noteimage = NoteImage(
                        note=self.note,
                        image=File(png_f, name=get_file_path(rand, ".png")),
                        pdf_file=File(pdf_f, name=get_file_path(rand, ".pdf")),
                        width=width,
                        height=height,
                    )
                    noteimage.save()
                self.note.image = noteimage
                self.note.save(just_setting_image=True)

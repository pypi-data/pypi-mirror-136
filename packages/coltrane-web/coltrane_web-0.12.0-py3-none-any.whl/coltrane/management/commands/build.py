import time
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand

from coltrane.config.paths import (
    get_base_directory,
    get_output_directory,
    get_output_json,
    get_output_static_directory,
)
from coltrane.manifest import Manifest, ManifestItem
from coltrane.retriever import get_content


class Command(BaseCommand):
    help = "Build all static HTML files and put them into a directory named output."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force building all files",
        )

    def _call_collectstatic(self):
        stdout = StringIO()
        stderr = StringIO()

        # Force DEBUG to always be `False` so that
        # whitenoise.storage.CompressedManifestStaticFilesStorage will use the static
        # assets with hashed failenames
        settings.DEBUG = False

        # TODO: Option to remove static files before re-generating
        management.call_command(
            "collectstatic",
            interactive=False,
            verbosity=1,
            stdout=stdout,
            stderr=stderr,
        )

        stderr.seek(0)

        # Get relative output static directory
        output_static_directory = str(get_output_static_directory()).replace(
            str(get_base_directory()), ""
        )
        output_static_directory = f"{output_static_directory}/"[1:]

        # Get output from standard out and clean it up
        stdout.seek(0)
        collectstatic_stdout = stdout.read()
        collectstatic_stdout = collectstatic_stdout.replace(
            "'" + str(get_output_static_directory()) + "'", output_static_directory
        )[1:-2]
        collectstatic_stdout = collectstatic_stdout.replace("copied ", "")
        collectstatic_stdout = "Copy " + collectstatic_stdout

        self.stdout.write(f"- {collectstatic_stdout}")

        # TOOD: Handle files in output.json that weren't
        # found in content? (--clean option?)

    def output_markdown_file(
        self,
        manifest: Manifest,
        is_force: bool,
        markdown_file: Path,
    ):
        item = ManifestItem.create(markdown_file)
        existing_item = manifest.get(markdown_file)

        if existing_item and not is_force:
            skip_message = ""

            if item.mtime == existing_item.mtime:
                skip_message = f"- Skip output/{item.name} because the modified date is not changed"
            elif item.md5 == existing_item.md5:
                skip_message = (
                    f"- Skip output/{item.name} because the content is not changed"
                )

                # Update item in manifest to get newest mtime
                manifest.add(markdown_file)

            if skip_message:
                self.stdout.write(skip_message)
                return

        rendered_html = item.render_html()

        action = "- Create"

        if item.generated_file.exists():
            action = "- Update"

        item.generated_file.write_text(rendered_html)
        manifest.add(markdown_file)

        self.stdout.write(f"{action} {item.generated_file_name}")

    def handle(self, *args, **options):
        start_time = time.time()

        self.stdout.write(self.style.WARNING("Start generating the static site...\n"))

        self._call_collectstatic()

        output_directory = get_output_directory()
        output_directory.mkdir(exist_ok=True)

        content_paths = get_content()
        manifest = Manifest(
            manifest_file=get_output_json(),
            out=self.stdout,
        )

        is_force = False

        if options["force"]:
            is_force = True
            self.stdout.write("- Force update because of command line argument")

        if not is_force and manifest.static_files_manifest_changed:
            # At least one static file has changed, so re-render all files because
            # we don't have granularity to know which static files are used in
            # particular markdown or template files
            is_force = True
            self.stdout.write("- Force update because static file(s) updated")

        for markdown_file in content_paths:
            self.output_markdown_file(manifest, is_force, markdown_file)

        if manifest.is_dirty:
            self.stdout.write("- Update manifest")
            manifest.write_data()

        self.stdout.write()

        elapsed_time = abs((time.time() - start_time))
        self.stdout.write(
            self.style.SUCCESS(f"Static site output completed in {elapsed_time:.4f}s")
        )

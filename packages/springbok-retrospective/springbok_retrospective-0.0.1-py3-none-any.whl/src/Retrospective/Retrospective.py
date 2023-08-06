"""
This project seeks to create a 'retrospective' of Google News top hits.
Copyright (C) Springbok LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from argparse import ArgumentParser
import base64
import datetime
import logging
import os
import re
import unicodedata
import json
import subprocess
import src.Retrospective.ChromeDriver as ChromeDriver
from string import Template

from dateutil.relativedelta import relativedelta

from src.Retrospective.GoogleNewsDriver import GoogleNewsDriver


logger = logging.getLogger(__name__)


class Retrospective:
    def __init__(self):
        self.googleNewsDriver = GoogleNewsDriver()

    def collect_google_news(self, query, period, window, span):
        """Collect Google News search results over a time span.

        Params:
        period - the time period in which separate queries will take place, in months
        window - the time window in which individual queries take place, in weeks
        span - the time span in which the total search takes place, in years
        """
        # Initialize date and results
        current_date = datetime.date.today()
        results = []

        # Check if current search date is within the specified time span
        search_date = current_date
        span_date = current_date - relativedelta(years=+span)
        while search_date >= span_date:

            # Calculate beginning of search window
            max_date = search_date
            min_date = max_date - datetime.timedelta(days=window)

            # Define the URL, then get and parse the page
            print(query)
            print(min_date.strftime("%m/%d/%Y"))
            print(max_date.strftime("%m/%d/%Y"))
            news_url = self.googleNewsDriver.get_google_news_url(
                query,
                min_date=min_date,
                max_date=max_date,
                sorted_by_date=True,
                page_number=1,
            )
            page_source = self.googleNewsDriver.get_search_result_page_source(news_url)
            try:
                result = self.googleNewsDriver.parse_search_result_page_source(page_source)[
                    0
                ]
                results.append(result)
            except:
                print(f"Could not get query: {news_url}")

            # Set the search date for an earlier time span
            search_date = search_date - relativedelta(months=+period)

        return results

    def write_posts(self, repo_path, content_path, image_path, template_path, results):
        """Write GoHugo files for blog posts.

        Params:
        repo_path - path for static site repo
        content_path - absolute path containing hugo list
        image_path - absolute path containing hugo images
        results - collected Google News search results
        """

        content_path = repo_path + content_path
        image_path = repo_path + image_path

        with open(template_path, 'r') as f:
            template = Template(f.read())

        for result in results:

            # Strip new line from title
            title = result["title"].replace('\n', '')

            # Create slugified version of title for use in blog dir
            base_name = self.slugify(title)
            tagged_base_name = f"retrospective-{base_name}"

            # Create absolute blog path for creation of blog dir and files
            blog_path = f"{content_path}/{tagged_base_name}"

            # Create directory if it does not exist
            if not os.path.isdir(blog_path):
                os.makedirs(blog_path, exist_ok=False)
            # Else continue to avoid creating duplicate articles
            else:
                continue

            # Write the image to a file, if image exists
            if result["image"]:
                fields = result["image"].split(",")
                image_extn = fields[0].split("/")[1].split(";")[0]
                image_data = base64.b64decode(fields[1])
                image_name = f"{base_name}.{image_extn}"
                with open(f"{image_path}/{image_name}", "wb") as f:
                    f.write(image_data)
            else:
                image_name = "placeholder.png"

            # Create dictionary for template
            d = {
                'title': title,
                'date': result["date_time"].strftime("%Y-%m-%d"),
                'url': result["link"],
                'image': image_name,
                'body': result["description"],
            }

            text = template.substitute(d)

            # Write the index markdown if image is found
            index_path = f"{blog_path}/index.md"
            with open(index_path, "w+") as f:
                f.writelines(text)

    def output_results(self, repo, content_path, image_path, template, results, config_fname=None):

        if template and config_fname is not None:
            retrospective.add_to_config_file(
                args.search_term, args.period, args.window, args.span, args.repo, config_fname
            )

        if template:
            retrospective.write_posts(
                repo, content_path, image_path, template, results
            )
        else:
            for result in results:
                print(result)

    def slugify(self, value, allow_unicode=False):
        """
        Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
        Remove characters that aren't alphanumerics, underscores, or hyphens.
        Convert to lowercase. Also strip leading and trailing whitespace.
        Source: https://docs.djangoproject.com/en/3.0/_modules/django/utils/text/#slugify
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize("NFKC", value)
        else:
            value = (
                unicodedata.normalize("NFKD", value)
                .encode("ascii", "ignore")
                .decode("ascii")
            )
        value = re.sub(r"[^\w\s-]", "", value).strip().lower()
        return re.sub(r"[-\s]+", "-", value)

    def add_to_config_file(self, search_term, period, window, span, repo_path, config_fname):

        search_details = {"period": period, "window": window, "span": span}

        config_path = repo_path + "/" + config_fname

        # Check if file exists
        if os.path.isfile(config_path):
            # Load and resave
            with open(config_path, "r+") as config_file:
                data = json.load(config_file)
                data[search_term] = search_details
                config_file.seek(0)
                json.dump(data, config_file, indent=4)
        else:
            with open(config_path, "w") as config_file:
                data = {}
                data[search_term] = search_details
                config_file.seek(0)
                json.dump(data, config_file, indent=4)

    def populate_from_config_file(self, repo_path, content_path, image_path, template, config_fname):

        config_path = repo_path + "/" + config_fname

        with open(config_path, "r") as config_file:
            searches = json.load(config_file)

            for search in searches:

                results = retrospective.collect_google_news(
                    search,
                    searches[search]["period"],
                    searches[search]["window"],
                    searches[search]["span"],
                )
                retrospective.output_results(repo_path, content_path, image_path, template, results)

    def save(self, tag, repo_dir, ):

        subprocess.run(["rm", "-r", "public"], cwd=repo_dir)
        subprocess.run("hugo", cwd=repo_dir)
        subprocess.run(["hugo", "deploy", "--target=staging"], cwd=repo_dir)
        subprocess.run(["git", "commit", "-am", '"' + tag + '"'], cwd=repo_dir)
        subprocess.run(
            ["git", "tag", "-a", tag, "-m", str(datetime.date.today())], cwd=repo_dir
        )
        subprocess.run(["git", "push", "origin", tag], cwd=repo_dir)

    def load(self, tag, repo_dir):
        subprocess.run(["git", "checkout", tag], cwd=repo_dir)
        subprocess.run(["rm", "-r", "public"], cwd=repo_dir)
        subprocess.run("hugo", cwd=repo_dir)
        subprocess.run(["hugo", "deploy", "--target=staging"], cwd=repo_dir)


def main():
    """
    Conduct a retrospective search to create GoHugo files for blog posts.
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--content-path",
        default="/content/blog",
        help="Relative path containing hugo list built off repo path - [REPO_PATH]/content/blog for static site",
    )
    parser.add_argument(
        "-i",
        "--image-path",
        default="/static/images",
        help="Relative path containing hugo images - [REPO_PATH]/static/images for static site",
    )
    parser.add_argument(
        "-t",
        "--search-term",
        default="bioinformatics",
        help="Term with which to search google news",
    )
    parser.add_argument(
        "-f",
        "--config-fname",
        default="retrospective.json",
        help="Name of retrospective config file in project dir",
    )
    parser.add_argument(
        "-p",
        "--period",
        default=6,
        type=int,
        help="Time period in which separate queries will take place, in months",
    )
    parser.add_argument(
        "-w",
        "--window",
        default=8,
        type=int,
        help="Time window in which individual queries take place, in weeks",
    )
    parser.add_argument(
        "-s",
        "--span",
        default=2,
        type=int,
        help="Time span in which the total search takes place, in years",
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Template file to use in blog. Template can accept title, date, url, image, and body. Value of None will print results",
    )
    parser.add_argument(
        "--show-c",
        action="store_true",
        help="Show copyright",
    )
    parser.add_argument(
        "--show-w",
        action="store_true",
        help="Show warranty",
    )
    parser.add_argument(
        "--from-config", action="store_true", help="populate blog from config file",
    )
    parser.add_argument(
        "--save", help="saves current hugo version with git tag. Overrides other flags",
    )
    parser.add_argument(
        "--load",
        help="loads and deploys git tag to staging area. Overrides other flags",
    )
    #TODO: remove default or make better error message
    parser.add_argument(
        "--repo",
        default="/Users/williamspear/projects/springbok/springbok/springbok-static-site/springbok-site",
        help="Directory location of hugo site git repo",
    )

    args = parser.parse_args()

    print(
        f"""
        Retrospective  Copyright (C) {datetime.datetime.now().year}  Springbok LLC
        This program comes with ABSOLUTELY NO WARRANTY; for details type `Retrospective --show-w'.
        This is free software, and you are welcome to redistribute it
        under certain conditions; type `Retrospective --show-c' for details.
        """
    )
    retrospective = Retrospective()
    ChromeDriver.update()
    if args.show_w:
        print("""
        THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
        APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
        HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
        OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
        THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
        PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
        IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
        ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
        """)
    elif args.show_c:
        print("""
        You may convey verbatim copies of the Program's source code as you
        receive it, in any medium, provided that you conspicuously and
        appropriately publish on each copy an appropriate copyright notice;
        keep intact all notices stating that this License and any
        non-permissive terms added in accord with section 7 apply to the code;
        keep intact all notices of the absence of any warranty; and give all
        recipients a copy of this License along with the Program.

          You may charge any price or no price for each copy that you convey,
        and you may offer support or warranty protection for a fee.
        """)
    elif args.from_config:
        retrospective.populate_from_config_file(
            args.repo, args.content_path, args.image_path, args.template, args.config_fname
        )
    elif args.save:
        retrospective.save(args.save, args.repo)
    elif args.load:
        retrospective.load(args.load, args.repo)
    else:
        results = retrospective.collect_google_news(
            args.search_term, args.period, args.window, args.span
        )
        retrospective.output_results(args.repo, args.content_path, args.image_path, args.template, results, args.config_fname)

if __name__ == "__main__":
    main()

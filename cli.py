import subprocess
import os
import typer
from datetime import datetime


app = typer.Typer()


class ShotScraper:

    def __init__(self, host_name: str, file_path: str, output_dir_png: str = None, output_dir_html: str = None):
        self.host_name = host_name
        self.file_path = file_path

        current_datetime = datetime.now()

        # Format the current date and time to match %F-%T format
        formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")

        self.html_dir = output_dir_html if output_dir_html else f'hosts/{self.host_name}/{formatted_datetime}/html'
        self.png_dir = output_dir_png if output_dir_png else f'hosts/{self.host_name}/{formatted_datetime}/png'


    def create_screenshots(self):
        with open(self.file_path, 'r') as file:
            urls = file.readlines()

        os.makedirs(self.png_dir)

        for url in urls:
            print(f'Running on --> {url}')
            url = url.strip()
            file_name = url.replace('/', '-')
            output_file = os.path.join(self.png_dir, f'{file_name}.png')
            command = f'shot-scraper {url} --wait 5000 --output {output_file}' # Wait 5 second to load page
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            process.wait()

    def save_htmls(self):
        with open(self.file_path, 'r') as file:
            urls = file.readlines()
        
        os.makedirs(self.html_dir)

        for url in urls:
            print(f'Running on --> {url}')
            url = url.strip()
            file_name = url.replace('/', '-')
            output_file = os.path.join(self.html_dir, f'{file_name}.html')
            command = f'shot-scraper html {url} --wait 5000 --output {output_file}' # Wait 5 second to load page
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            process.wait()

    def upload_to_storage(self, remote_server: str = None, remote_path: str = None):
        local_path = f"hosts/{self.host_name}/"
        remote_server = remote_server if remote_server else "storage"
        remote_path_server = remote_path if remote_path else f"storage/web-apps/hosts/{self.host_name}/"
        rsync_cmd = [
            "rsync",
            "-avz",  # Options for archive mode, verbose, and compression
            "--progress",  # Show progress during transfer
            local_path,
            f"{remote_server}:{remote_path_server}"
        ]
        try:
            subprocess.run(rsync_cmd, check=True)
            print("Upload successful!")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            print("Upload failed.")



@app.command()
def main(host: str, urls_file: str, output_dir_png: str = None, output_dir_html: str = None):
    shot_scraper = ShotScraper(host, urls_file, output_dir_png, output_dir_html)
    shot_scraper.create_screenshots()
    shot_scraper.save_htmls()
    shot_scraper.upload_to_storage()

@app.command()
def create_screenshots(host: str, urls_file: str, output_dir_png: str = None, output_dir_html: str = None):
    shot_scraper = ShotScraper(host, urls_file, output_dir_png, output_dir_html)
    shot_scraper.create_screenshots()

@app.command()
def create_htmls(host: str, urls_file: str, output_dir_png: str = None, output_dir_html: str = None):
    shot_scraper = ShotScraper(host, urls_file, output_dir_png, output_dir_html)
    shot_scraper.save_htmls()

@app.command()
def upload_to_storage(host: str, urls_file: str):
    shot_scraper = ShotScraper(host, urls_file)
    shot_scraper.upload_to_storage()


if __name__ == "__main__":
    app()

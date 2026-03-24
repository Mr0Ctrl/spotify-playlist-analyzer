import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import config
from utils import math_utils

class ReportGenerator:
    """Handles the creation and layout of the PDF report."""

    def __init__(self, output_dir: str, playlist_name: str):
        self.output_path = os.path.join(output_dir, f"Analysis_Report_{playlist_name}.pdf")
        self.pdf = PdfPages(self.output_path)
        # Convert A4 mm to inches for Matplotlib
        self.page_size = (
            math_utils.mm_to_inches(config.A4_LANDSCAPE[0]),
            math_utils.mm_to_inches(config.A4_LANDSCAPE[1])
        )

    def add_title_page(self, playlist_name: str, track_info:dict):
        """Creates a professional cover page for the report."""
        fig = plt.figure(figsize=self.page_size)
        fig.clf() # Clear figure
        
        # Add Title
        fig.text(0.5, 0.7, config.REPORT_TITLE, size=config.TITLE_FONT_SIZE, ha="center", weight="bold")
        
        # Add Subtitle
        subtitle = f"Playlist: {playlist_name}\n"
        info =""
        for index, (key, value) in enumerate(track_info.items()):
            info = info + f"{str(key):_<15}:{str(value):_>15}\n"


        fig.text(0.5, 0.55, subtitle, size=config.SUBTITLE_FONT_SIZE, ha="center")
        fig.text(0.5, 0.45, info    , size=config.FONT_SIZE, ha="center")
        
        # Add Footer
        fig.text(0.5, 0.1, config.FOOTER_TEXT, size=10, ha="center", style="italic")
        
        self.pdf.savefig(fig)
        plt.close(fig)

    def add_visual_page(self, fig: plt.Figure):
        """Appends a visualization figure as a new page in the PDF."""
        # Ensure the figure matches the PDF page size
        fig.set_size_inches(self.page_size)
        self.pdf.savefig(fig)
        plt.close(fig)

    def close(self):
        """Finalizes and saves the PDF file."""
        self.pdf.close()
        print(f"Report successfully saved to: {self.output_path}")
from shiny import App, render, ui, reactive
from shiny.types import ImgData

import imageio as iio

app_ui = ui.page_fluid(
    ui.panel_title("Image denoising"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file(
                "file", "Upload an image file", accept="image/*", multiple=False
            ),
        ),
        ui.panel_main(
            ui.output_image("out_img"),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.image
    def out_img():
        if input.file() is not None:
            img = iio.imread(input.file()[0]["datapath"])
            # im
            # img = ImgData(src=img, alt="Uploaded image")
            return img


app = App(app_ui, server)

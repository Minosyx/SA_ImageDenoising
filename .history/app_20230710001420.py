from shiny import App, render, ui, reactive
from shiny.types import ImgData

import imageio.v3 as iio
import io

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
            path = input.file()[0]["datapath"]
            props = iio.improps(path)
            height, width = "auto", "auto"
            if props["height"] > props["width"]:
                height = "100%"
            else:
                width = "100%"
            img = ImgData(src=path, alt="Uploaded image", height=height, width=width)
            return img


app = App(app_ui, server)

from shiny import App, render, ui
from shiny.types import ImgData

app_ui = ui.page_fluid(
    ui.panel_title("Image denoising"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file(
                "file", "Upload an image file", accept="image/*", multiple=False
            ),
        ),
        ui.panel_main(
            ui.output_image("out_img", width="100%"),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.image
    def out_img():
        if input.file():
            print(ImgData(input.file()))
            return ImgData(input.file())


app = App(app_ui, server)

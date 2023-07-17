from shiny import App, render, ui, reactive
from shiny.types import ImgData

import image_processing as ip

app_ui = ui.page_fluid(
    ui.panel_title("Image denoising"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file(
                "file", "Upload an image file", accept="image/*", multiple=False
            ),
            ui.input_select(
                "denoise_method",
                "Denoising method",
                choices={
                    "svd: "Singular Value Decomposition"",
                    "fft": "Fast Fourier Transform",
                    "Wavelet Transform": "wavelet",
                },
            ),
            ui.input_action_button("denoise", "Denoise"),
            width=2,
        ),
        ui.panel_main(
            ui.output_image("out_img"),
        ),
    ),
)


def server(input, output, session):
    imgPath = None

    @output
    @render.image
    def out_img():
        if input.file() is not None:
            imgPath = input.file()[0]["datapath"]
            img = ImgData(
                src=imgPath, alt="Uploaded image", height="100%", width="auto"
            )
            return img


app = App(app_ui, server)

from shiny import App, render, ui, reactive, Inputs, Outputs, Session
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
                    "svd": "Singular Value Decomposition",
                    "fft": "Fast Fourier Transform",
                    "wavelet": "Wavelet Transform",
                },
            ),
            ui.panel_conditional(
                "output.busy == False",
                ui.input_action_button("denoise", "Denoise"),
            ),
            ui.panel_conditional(
                "output.denosing_ended == True",
                ui.download_button(
                    "download",
                    "Download",
                    filename="denoised_image.png",
                    data="denoised_img",
                ),
                # style="display: none;",
            ),
            width=2,
        ),
        ui.panel_main(
            ui.output_image("out_img"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    img_path = reactive.Value(None)
    output.denosing_ended = reactive.Value(False)
    output.denoised_img = reactive.Value(None)
    output.busy = reactive.Value(False)

    @output
    @render.image
    def out_img():
        if input.file() is not None:
            output.denosing_ended.set(False)
            img_path.set(input.file()[0]["datapath"])
            img = ImgData(
                src=img_path.get(), alt="Uploaded image", height="100%", width="auto"
            )
            return img

    # @reactive.Effect
    # @reactive.event(input.file)
    # def activate_denoise_button():
    #     if input.file() is not None:

    @reactive.Effect
    @reactive.event(input.denoise)
    def denoise():
        if input.denoise_method() is not None and img_path.get() is not None:
            img = ip.ImageDenoising(img_path.get(), input.denoise_method())
            output.denoised_img.set(img.denoise())
            output.denosing_ended.set(True)


app = App(app_ui, server)

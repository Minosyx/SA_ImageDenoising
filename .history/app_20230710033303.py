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
            ui.input_action_button("denoise", "Denoise"),
            ui.input_action_button("download", "Download", disabled=True),
            width=2,
        ),
        ui.panel_main(
            ui.output_image("out_img"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    img_path = reactive.Value(None)
    denosing_ended = reactive.Value(False)

    @output
    @render.image
    def out_img():
        if input.file() is not None:
            img_path.set(input.file()[0]["datapath"])
            img = ImgData(
                src=img_path, alt="Uploaded image", height="100%", width="auto"
            )
            return img

    @reactive.Effect
    @reactive.event(input.denoise, img_path)
    def denoise():
        if input.denoise_method() is not None and img_path.get() is not None:
            img = ip.ImageDenoising(img_path, input.denoise_method())
            img.denoise()
            denosing_ended.set(True)

    @reactive.Effect
    @reactive.event(denosing_ended)
    def enable_download():
        if denosing_ended.get():
            session.set_enabled("download", True)
        else:
            session.set_enabled("download", False)


app = App(app_ui, server)
